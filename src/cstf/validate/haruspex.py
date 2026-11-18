"""Run Haruspex for an electron microscopy entry."""

import logging
import os
from pathlib import Path
from cstf.validate.base import Entry, ValidationStep

from cstf.validate.docker_service import ContainerService, DockerServiceError

logger = logging.getLogger("xtal_validation.orchestrator.haruspex")

HARUSPEX_IMAGE = os.environ.get("HARUSPEX_IMAGE", "haruspex:arm64")
HARUSPEX_PLATFORM = os.environ.get("HARUSPEX_PLATFORM", "linux/arm64")

HARUSPEX_ARGS = [
    "-d",
    "map-predict",
    "{map}",
    "-o",
    "{out}",
]

MAP_EXTS = (".mrc", ".map", ".ccp4")
SKIP_IN_NAME = ("half", "mask", "msk")  # prefer the full map over half maps/masks

RENDER_CLASSES = {
    "helix": (("helix",), "#c8202e"),
    "sheet": (("sheet", "strand"), "#2a78b5"),
    "nucleotide": (("npair", "nuc", "rna", "dna"), "#e08a00"),
}
RENDER_IMAGE_NAME = "haruspex_render.jpg"
RENDER_LEVEL_FRACTION = 0.2  # contour at 20% of each map's maximum

LOG_NAMES = {"haruspex_stdout.log", "haruspex_stderr.log", RENDER_IMAGE_NAME}


class HaruspexStep(ValidationStep):
    """Run Haruspex on applicable cryo-EM entries."""

    name = "haruspex"

    def __init__(self, *, skip_existing=True, service=None, **options):
        super().__init__(skip_existing=skip_existing, **options)
        self.service = service
        self.map_path = None

    def check_input(self, entry: Entry):
        if not entry.is_em:
            return "not_applicable: exp_method is {!r}".format(entry.exp_method)
        self.map_path = self.find_map(entry.path)
        return None if self.map_path else "no_input: no .mrc/.map/.ccp4 file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.haruspex_dir

    def is_complete(self, entry: Entry) -> bool:
        return entry.haruspex_dir.is_dir() and any(
            path.is_file() and path.name not in LOG_NAMES
            for path in entry.haruspex_dir.iterdir()
        )

    def execute(self, entry: Entry) -> list[Path]:
        return self._run_haruspex(
            map_path=str(self.map_path),
            output_dir=str(entry.haruspex_dir),
            service=self.service,
        )

    def format_result(self, result: list[Path]) -> str:
        return "done ({} files)".format(len(result))

    def summarize(self, entry: Entry, result: list[Path]) -> dict:
        render = next((p for p in result if p.name == RENDER_IMAGE_NAME), None)
        return {
            "directory": entry.rel(entry.haruspex_dir),
            "map": entry.rel(self.map_path),
            "files": [entry.rel(p) for p in result if p.name != RENDER_IMAGE_NAME],
            "render": entry.rel(render) if render else None,
        }

    @staticmethod
    def find_map(path):
        """Return the primary density map in `path` (or None). Full maps are
        preferred over half maps and masks; compressed maps (.gz) are ignored,
        so gunzip them first."""
        path = Path(path)
        if not path.is_dir():
            return None
        maps = sorted(
            f for f in path.iterdir() if f.is_file() and f.name.lower().endswith(MAP_EXTS)
        )
        if not maps:
            return None
        primary = [f for f in maps if not any(s in f.name.lower() for s in SKIP_IN_NAME)]
        return (primary or maps)[0]


    @staticmethod
    def _snapshot(directory):
        return {p: p.stat().st_mtime_ns for p in directory.iterdir() if p.is_file()}


    def render_haruspex_image(
        self,
        produced,
        output_dir,
        image_name=RENDER_IMAGE_NAME,
        size=(2000, 2000),
        smooth_sigma=0.8,
        level_fraction=RENDER_LEVEL_FRACTION,
        levels=None,
        min_blob_voxels=30,
        view="xy",
        zoom=1.5,
    ):
        """
        Render the per-class Haruspex maps as one image with PyVista:
        red = helices, blue = sheets, orange = nucleotides, on black.

        Args:
            level_fraction: contour at this fraction of each map's maximum.
            levels: optional absolute per-class levels, e.g. {"helix": 0.02}.
            min_blob_voxels: drop disconnected specks smaller than this (0 = keep all).
            view: "xy", "xz", "yz" (axis-aligned) or "iso".
            zoom: camera zoom after fitting the scene.

        Returns the image Path, or None if nothing could be rendered. Never raises.
        """
        try:
            import mrcfile
            import numpy as np
            import pyvista as pv
            from scipy.ndimage import gaussian_filter, label
        except ImportError as exc:
            logger.warning("Skipping Haruspex render (missing dependency): %s", exc)
            return None

        levels = levels or {}
        out_path = Path(output_dir) / image_name
        mrc_files = [p for p in produced if p.suffix.lower() == ".mrc"]

        try:
            pv.OFF_SCREEN = True
            plotter = pv.Plotter(off_screen=True, window_size=list(size))
            plotter.set_background("black")
            n_meshes = 0

            for cls, (keywords, color) in RENDER_CLASSES.items():
                map_file = next(
                    (p for p in mrc_files if any(k in p.stem.lower() for k in keywords)),
                    None,
                )
                if map_file is None:
                    logger.info(
                        "Haruspex render: no %s map found among %s, skipping",
                        cls,
                        [p.name for p in mrc_files],
                    )
                    continue

                with mrcfile.open(str(map_file), permissive=True) as mrc:
                    data = np.asarray(mrc.data, dtype=np.float32)
                    vs = mrc.voxel_size
                    spacing = (float(vs.x) or 1.0, float(vs.y) or 1.0, float(vs.z) or 1.0)

                if smooth_sigma:
                    data = gaussian_filter(data, sigma=smooth_sigma)

                vmax = float(data.max())
                level = levels.get(cls, level_fraction * vmax)
                if not (float(data.min()) < level < vmax):
                    logger.warning(
                        "Haruspex render: level %.3g outside %s map range "
                        "[%.3g, %.3g], skipping",
                        level,
                        cls,
                        data.min(),
                        vmax,
                    )
                    continue
                logger.info(
                    "Haruspex render: %s contour level %.4g (max %.4g)", cls, level, vmax
                )

                # Remove tiny disconnected specks before contouring.
                if min_blob_voxels:
                    labels, n_labels = label(data > level)
                    if n_labels:
                        sizes = np.bincount(labels.ravel())
                        small = sizes < min_blob_voxels
                        small[0] = False  # label 0 = background
                        data = data.copy()
                        data[small[labels]] = data.min()

                # mrcfile arrays are (z, y, x); PyVista wants dimensions (x, y, z)
                # with x varying fastest, which a C-order ravel gives.
                grid = pv.ImageData(
                    dimensions=(data.shape[2], data.shape[1], data.shape[0]),
                    spacing=spacing,
                )
                grid.point_data["density"] = data.ravel()
                surface = grid.contour([level], scalars="density")
                if surface.n_points == 0:
                    logger.warning("Haruspex render: empty %s surface, skipping", cls)
                    continue

                plotter.add_mesh(
                    surface.smooth(n_iter=10),  # light smoothing keeps detail
                    color=color,
                    smooth_shading=True,
                    ambient=0.25,
                    diffuse=0.75,
                    specular=0.4,
                    specular_power=25,
                )
                n_meshes += 1

            if n_meshes == 0:
                plotter.close()
                logger.warning("Haruspex render: no surfaces to draw")
                return None

            # Ambient occlusion gives the soft depth shading of ChimeraX's
            # "lighting soft". Optional: skipped if the backend can't do it.
            try:
                xmin, xmax, ymin, ymax, zmin, zmax = plotter.bounds
                extent = max(xmax - xmin, ymax - ymin, zmax - zmin)
                plotter.enable_ssao(radius=0.03 * extent, bias=0.005 * extent)
            except Exception as exc:
                logger.info("Haruspex render: SSAO unavailable (%s)", exc)
            try:
                plotter.enable_anti_aliasing("fxaa")
            except Exception as exc:
                logger.info("Haruspex render: anti-aliasing unavailable (%s)", exc)

            plotter.camera_position = view
            plotter.reset_camera()
            plotter.camera.zoom(zoom)

            plotter.screenshot(str(out_path))  # format chosen by .jpg extension
            plotter.close()
            return out_path
        except Exception as exc:  # rendering must never break the pipeline
            logger.warning("Haruspex render failed: %s", exc)
            return None


    def _run_haruspex(
        self,
        map_path,
        output_dir,
        service=None,
        timeout=3600,
        extra_args=None,
        render=True,
        render_levels=None,
        render_level_fraction=RENDER_LEVEL_FRACTION,
    ):
        """
        Run Haruspex on a map and return the files it produced in output_dir.

        Args:
            service: ContainerService for HARUSPEX_IMAGE (shared across entries).
                If None, a temporary container is started and stopped.

        Raises HaruspexError on failure, including "ran but wrote nothing".
        """
        in_map = Path(map_path).resolve()
        out_dir = Path(output_dir).resolve()
        if not in_map.is_file():
            raise RuntimeError("Map not found: {}".format(in_map))
        out_dir.mkdir(parents=True, exist_ok=True)

        own = service is None
        if own:
            root = os.path.commonpath([str(in_map), str(out_dir)])
            service = ContainerService(HARUSPEX_IMAGE, HARUSPEX_PLATFORM, root)

        try:
            before = self._snapshot(out_dir)
            args = [a.format(map=str(in_map), out=str(out_dir)) for a in HARUSPEX_ARGS]
            args += list(extra_args or [])
            try:
                proc = service.exec(args, workdir=out_dir, timeout=timeout)
            except DockerServiceError as exc:
                raise RuntimeError(str(exc)) from exc
        finally:
            if own:
                service.stop()

        (out_dir / "haruspex_stdout.log").write_text(proc.stdout or "")
        (out_dir / "haruspex_stderr.log").write_text(proc.stderr or "")

        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip()[-1500:]
            raise RuntimeError(
                "Haruspex exited with code {}: {}".format(proc.returncode, tail)
            )

        after = self._snapshot(out_dir)
        produced = sorted(
            p for p, t in after.items() if before.get(p) != t and p.name not in LOG_NAMES
        )
        if not produced:
            raise RuntimeError(
                "Haruspex exited cleanly but wrote no output files "
                "(check HARUSPEX_ARGS and haruspex_stdout.log)"
            )

        if render:
            image = self.render_haruspex_image(
                produced,
                out_dir,
                levels=render_levels,
                level_fraction=render_level_fraction,
            )
            if image is not None:
                produced.append(image)

        return produced
