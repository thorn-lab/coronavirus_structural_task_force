"""Score an electron-microscopy model against its experimental map.

Reproduces CCP-EM's "Atomic model validation" job
(``pipeliner.atomic_model_validation`` in ccpem-pipeliner 1.6.1) with the same
open-source programs and settings, run from this package's environment:

* FSC: ``servalcat fsc --model M --map MAP --mask_soft_edge 6`` (model mask);
  FSCavg = mean FSC weighted by Fourier coefficients per shell, up to the map
  resolution (also stored: all shells, and up to FSC = 0.5).
* Global fit: ``TEMPy.scores -r RES --contour-level C`` (CCC, MI, overlap).
* Local fit: ``TEMPy.smoc -r RES --smoc-window 1``; Z-score of each residue
  against the SMOC of residues whose CA lies within 12 A (itself included,
  only if more than 2 such residues); outlier if Z < -2.0 (the value the
  pipeliner code applies; its labels say -1.5).
* Contour: the author-recommended level from the EMDB header, otherwise
  1.5 x the spread of map values above the background peak.

On PDB 6nur this matched every number of the CCP-EM job, per residue for
SMOC. See docs/source/validate/em_validation.md.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from importlib.metadata import version
from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from cstf.validate.haruspex import HaruspexStep

SUMMARY_NAME = "model_map_validation.json"
SUMMARY_VERSION = 3  # bump when the summary's meaning changes, to rescore
SERVALCAT_MASK_SOFT_EDGE = 6
SMOC_WINDOW = 1
SMOC_NEIGHBOUR_RADIUS = 12.0
SMOC_OUTLIER_Z = -2.0
CONTOUR_SIGMA_FACTOR = 1.5


class EMMapFitStep(ValidationStep):
    """Model-map FSCavg, TEMPy global scores and SMOC outliers for an EM entry.

    Options: ``resolution`` (fallback in A when neither the model nor the EMDB
    header gives one) and ``timeout`` (seconds per program, default 3600).
    """

    name = "em_map_fit"

    def __init__(self, *, skip_existing=True, **options):
        super().__init__(skip_existing=skip_existing, **options)
        self.map_path = None

    def check_input(self, entry: Entry):
        if not entry.is_em:
            return "not_applicable: exp_method is {!r}".format(entry.exp_method)
        if entry.model_path is None:
            return "no_input: no .pdb or .cif model found"
        self.map_path = HaruspexStep.find_map(entry.path)
        return None if self.map_path else "no_input: no .mrc/.map/.ccp4 file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.em_validation_dir

    def summary_path(self, entry: Entry) -> Path:
        return self.output_dir(entry) / SUMMARY_NAME

    def is_complete(self, entry: Entry) -> bool:
        try:
            summary = json.loads(self.summary_path(entry).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return summary.get("summary_version") == SUMMARY_VERSION

    def execute(self, entry: Entry) -> dict:
        model = Path(entry.model_path).resolve()
        map_path = Path(self.map_path).resolve()
        resolution, resolution_source = self._resolution_for(entry, model, map_path)
        contour = self._recommended_contour(entry.path, map_path)
        contour_source = "EMDB recommended"
        if contour is None:
            contour = round(sigma_contour(map_path), 3)
            contour_source = "1.5 sigma above background peak"
        out_dir = self.output_dir(entry) / "tool_output"
        shutil.rmtree(out_dir, ignore_errors=True)  # never read a stale output
        out_dir.mkdir(parents=True)
        summary = {
            "summary_version": SUMMARY_VERSION,
            "programs": "servalcat {}, BioTEMPy {}".format(
                version("servalcat"), version("biotempy")
            ),
            "resolution": resolution,
            "resolution_source": resolution_source,
            "contour": contour,
            "contour_source": contour_source,
            **self._score(model, map_path, resolution, contour, out_dir),
        }
        self.summary_path(entry).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    def summarize(self, entry: Entry, result: dict) -> dict:
        return {
            "report": entry.rel(self.summary_path(entry)),
            "map": entry.rel(self.map_path),
            **{k: v for k, v in result.items() if k != "summary_version"},
        }

    def _score(self, model, map_path, resolution, contour, out_dir: Path) -> dict:
        timeout = self.options.get("timeout", 3600)
        python = sys.executable
        fsc_file = out_dir / "masked_fsc.dat"
        _run(
            [python, "-m", "servalcat", "fsc", "--model", str(model), "--map", str(map_path),
             "--mask_soft_edge", str(SERVALCAT_MASK_SOFT_EDGE), "-o", str(fsc_file)],
            out_dir, timeout, "servalcat fsc",
        )
        tempy = "from TEMPy.script.{} import main; main()"
        _run(
            [python, "-c", tempy.format("scores"), "-m", str(map_path), "-p", str(model),
             "-r", str(resolution), "--contour-level", str(contour),
             "--output-prefix", "globscores", "--output-format", "csv"],
            out_dir, timeout, "TEMPy.scores",
        )
        _run(
            [python, "-c", tempy.format("smoc"), "-m", str(map_path), "-p", str(model),
             "-r", str(resolution), "--smoc-window", str(SMOC_WINDOW),
             "--output-format", "json", "--output-prefix", "smoc"],
            out_dir, timeout, "TEMPy.smoc",
        )
        smoc = {
            str(chain): {str(r): float(v) for r, v in residues.items()}
            for chain, residues in json.loads((out_dir / "smoc.json").read_text())["chains"].items()
        }
        zscores = smoc_zscores(smoc, ca_positions(model))
        with (out_dir / "smoc_per_residue.tsv").open("w") as out:
            out.write("chain\tresidue\tsmoc\tz\n")
            for chain, residues in smoc.items():
                for residue, value in residues.items():
                    z = zscores.get((chain, residue))
                    out.write("{}\t{}\t{:.4f}\t{}\n".format(
                        chain, residue, value, "" if z is None else "{:.3f}".format(z)))
        tempy_scores = read_tempy_scores(out_dir / "globscores.csv")
        return {
            **fsc_averages(read_servalcat_fsc(fsc_file), resolution),
            **{key: tempy_scores.get(key) for key in ("ccc", "ccc_mask", "mi", "mi_mask", "overlap")},
            **smoc_summary(zscores),
        }

    def _resolution_for(self, entry, model, map_path):
        resolution = self._resolution(model)
        if resolution is not None:
            return resolution, "model metadata"
        resolution = self._emdb_resolution(entry.path, map_path)
        if resolution is not None:
            return resolution, "EMDB header"
        if "resolution" in self.options:
            return float(self.options["resolution"]), "configured fallback"
        raise RuntimeError(
            "No resolution in the model or EMDB header; pass resolution= to the step"
        )

    @staticmethod
    def _emdb_header(entry_path: Path, map_path: Path):
        match = re.search(r"emd[_-](\d+)", Path(map_path).name, re.IGNORECASE)
        if not match:
            return None
        try:
            return ET.parse(Path(entry_path) / "emd-{}.xml".format(match.group(1))).getroot()
        except (OSError, ET.ParseError):
            return None

    @classmethod
    def _emdb_resolution(cls, entry_path: Path, map_path: Path):
        root = cls._emdb_header(entry_path, map_path)
        node = root.find(".//final_reconstruction/resolution") if root is not None else None
        try:
            return float(node.text) if node is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _recommended_contour(cls, entry_path: Path, map_path: Path):
        """Author-recommended contour of the primary map from the EMDB header."""
        root = cls._emdb_header(entry_path, map_path)
        level = root.find("map/contour_list/contour/level") if root is not None else None
        try:
            return float(level.text) if level is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _resolution(model_path: Path):
        """Read a nominal resolution from common PDB/mmCIF metadata fields."""
        try:
            text = Path(model_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
        patterns = (
            r"(?im)^REMARK\s+2\s+RESOLUTION\.\s*([0-9.]+)\s+ANGSTROMS",
            r"(?im)^\s*_em_3d_reconstruction\.resolution\s+['\"]?([0-9.]+)",
            r"(?im)^\s*_refine\.ls_d_res_high\s+['\"]?([0-9.]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if value > 0:
                    return value
        return None


# ---------------------------------------------------------------------------
# Result handling
# ---------------------------------------------------------------------------


def read_servalcat_fsc(path) -> list[dict]:
    """Shells of a servalcat ``fsc.dat`` as dicts (low to high resolution)."""
    header, shells = None, []
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "d_min":
            header = fields
            continue
        if header:
            shells.append({key: float(value) for key, value in zip(header, fields)})
    if not shells:
        raise RuntimeError("No FSC shells found in {}".format(path))
    return shells


def fsc_averages(shells: list[dict], resolution: float | None) -> dict:
    """FSCavg over all shells, up to the map resolution, and up to FSC=0.5."""

    def average(upto):
        selected = shells[:upto]
        weight = sum(s["ncoeffs"] for s in selected)
        if not selected or not weight:
            return None
        return sum(s["fsc_FC_full"] * s["ncoeffs"] for s in selected) / weight

    def last_index(condition):
        for index in range(len(shells) - 1, -1, -1):
            if condition(shells[index]):
                return index + 1
        return None

    to_resolution = (
        last_index(lambda s: (s["d_min"] + s["d_max"]) / 2.0 >= resolution)
        if resolution
        else None
    )
    to_half = last_index(lambda s: s["fsc_FC_full"] >= 0.5)
    return {
        "fsc_avg": average(to_resolution) if to_resolution else None,
        "fsc_avg_all_shells": average(len(shells)),
        "fsc_avg_to_fsc_0_5": average(to_half) if to_half else None,
    }


def ca_positions(model_path) -> dict[tuple[str, str], tuple[float, float, float]]:
    """CA coordinates of the first model, keyed by (chain, residue number)."""
    import gemmi

    structure = gemmi.read_structure(str(model_path))
    positions = {}
    for chain in structure[0]:
        for residue in chain:
            atom = residue.find_atom("CA", "*")
            if atom is not None:
                positions.setdefault(
                    (chain.name, str(residue.seqid.num)), tuple(atom.pos.tolist())
                )
    return positions


def smoc_zscores(smoc: dict[str, dict[str, float]], positions) -> dict:
    """Local SMOC Z-scores, as computed by CCP-EM's get_smoc_results.py."""
    import numpy as np
    from scipy.spatial import cKDTree

    keys = list(positions)
    if not keys:
        return {}
    tree = cKDTree(np.array([positions[k] for k in keys], dtype=float))
    zscores = {}
    for chain, residues in smoc.items():
        for residue, value in residues.items():
            if (chain, residue) not in positions:
                continue
            neighbours = tree.query_ball_point(positions[(chain, residue)], SMOC_NEIGHBOUR_RADIUS)
            values = [
                smoc[keys[n][0]][keys[n][1]]
                for n in neighbours
                if keys[n][1] in smoc.get(keys[n][0], {})
            ]
            spread = float(np.std(values)) if len(values) > 2 else 0.0
            zscores[(chain, residue)] = (
                (value - float(np.mean(values))) / spread if spread > 0 else 0.0
            )
    return zscores


def smoc_summary(zscores: dict) -> dict:
    outliers = sum(1 for z in zscores.values() if z < SMOC_OUTLIER_Z)
    return {
        "n_smoc_residues": len(zscores),
        "smoc_outlier_z": SMOC_OUTLIER_Z,
        "smoc_outlier_percent": 100.0 * outliers / len(zscores) if zscores else None,
    }


def read_tempy_scores(path) -> dict:
    """``TEMPy.scores`` CSV (metric,value rows) as a dict of floats."""
    scores = {}
    for line in Path(path).read_text().splitlines():
        name, _, value = line.partition(",")
        try:
            scores[name.strip()] = float(value)
        except ValueError:
            continue
    return scores


def sigma_contour(map_path, sigma_factor=CONTOUR_SIGMA_FACTOR) -> float:
    """CCP-EM's default contour: sigma_factor x spread above the background peak.

    The background peak is the most populated bin of the density histogram
    (refined once within that bin); the spread is the RMS deviation from the
    peak of all values at or above it.
    """
    import mrcfile
    import numpy as np

    with mrcfile.open(str(map_path), permissive=True) as mrc:
        data = np.asarray(mrc.data, dtype=np.float64).ravel()
    mean, std = data.mean(), data.std()
    low, high, peak = data.min(), data.max(), None
    for _ in range(2):
        sample = data[(data >= low) & (data <= high)]
        counts, edges = np.histogram(sample, 100)
        best = None
        for i in np.flatnonzero(counts == counts.max()):
            centre = (edges[i] + edges[i + 1]) / 2.0
            if centre < mean + std:
                best = (centre, edges[i], edges[i + 1])
        if best is None:
            break
        peak, low, high = best
    if peak is None:
        peak = mean
    above = data[data >= peak]
    return float(sigma_factor * np.sqrt(np.mean(np.square(above - peak))))


def _run(command, cwd, timeout, what):
    env = {**os.environ, "MPLBACKEND": "Agg"}  # headless; Jupyter sets its own
    try:
        process = subprocess.run(
            command, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, env=env, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("{} exceeded the {} s timeout".format(what, timeout)) from exc
    if process.returncode != 0:
        detail = (process.stderr or process.stdout or "").strip()[-2000:]
        raise RuntimeError("{} failed: {}".format(what, detail))
    return process
