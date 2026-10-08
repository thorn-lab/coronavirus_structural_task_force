"""
charts.py

Matplotlib replacements for the two Phenix/MolProbity plotting utilities the
original run_molprobity.sh called: `rama_chart_pdf` and `multichart`.

    plot_ramachandran(...)  -> Ramachandran report PDF laid out like
                               MolProbity's: six panels (general, Ile/Val,
                               pre-Pro, Gly, trans-Pro, cis-Pro) with the
                               Top8000 contours, labelled outliers, and a
                               statistics / outlier-list text block.
    plot_multichart(...)    -> per-residue "strip chart" PDF: one row per
                               criterion (Rama, rotamer, Cbeta, clash,
                               CaBLAM, ...) plus a B-factor track, laid out
                               along each chain so problem regions stand out.
    write_charts(...)       -> convenience wrapper used by the orchestrator.

Design notes
------------
* Uses the object-oriented matplotlib API (Figure, PdfPages) and never
  touches pyplot, so it is safe in worker processes / threads and needs no
  backend configuration.
* Plotting is decoupled from mmtbx: everything is drawn from small
  dataclasses (RamaPoint, Residue, Track). The `*_from_mmtbx` adapters at the
  bottom convert validation result objects into those; if your own
  ramalyze/rotalyze/... wrapper modules return something different, build
  the dataclasses directly (or write a ten-line adapter) and the plotting
  code does not change.
* The Ramachandran background is read from the Top8000 reference grids that
  ship with Phenix (chem_data/rotarama_data). It is identical for every
  structure, so it is parsed once per process and cached.
"""

from __future__ import annotations

import gzip
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, ListedColormap, Normalize
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Patch

log = logging.getLogger(__name__)

# (chain_id, resseq, insertion_code), all stripped; resseq is int when possible.
Key = Tuple[str, Union[int, str], str]


# --------------------------------------------------------------------------
# Data containers
# --------------------------------------------------------------------------


def make_key(chain: Any, resseq: Any, icode: Any = "") -> Key:
    """Normalise identifiers so results from different modules line up."""
    rs = str(resseq).strip()
    try:
        rs_val: Union[int, str] = int(rs)
    except ValueError:
        rs_val = rs
    return (str(chain).strip(), rs_val, (str(icode) if icode else "").strip())


@dataclass
class RamaPoint:
    key: Key
    resname: str
    phi: float
    psi: float
    res_type: int  # index into RAMA_TYPES
    status: str  # "favored" | "allowed" | "outlier"


@dataclass
class Residue:
    key: Key
    resname: str = ""
    b_mean: Optional[float] = None

    @property
    def label(self) -> str:
        _, num, ic = self.key
        return f"{num}{ic}"


# Residue-level severity codes used by the strip chart.
NA, OK, WARN, OUTLIER = 0, 1, 2, 3


@dataclass
class Track:
    """One row of the strip chart.

    levels  : {residue key: NA/OK/WARN/OUTLIER}
    default : level for residues that are absent from `levels`. Use OK for
              criteria that assess every residue but only report problems
              (clashes), NA for criteria that skip some residues (rotamers
              skip Gly/Ala, Cbeta skips Gly).
    """

    name: str
    levels: Dict[Key, int] = field(default_factory=dict)
    default: int = NA

    def level(self, key: Key) -> int:
        return self.levels.get(key, self.default)


# --------------------------------------------------------------------------
# Ramachandran chart -- laid out after the MolProbity rama_chart_pdf page:
# portrait letter, 3x2 panels, open-circle points, two contour lines,
# labelled outliers, then a text block with the statistics and outlier list.
# --------------------------------------------------------------------------

# Order matches mmtbx.validation.ramalyze RAMA_GENERAL .. RAMA_ILE_VAL.
RAMA_TYPES = [
    "general",
    "glycine",
    "cis-proline",
    "trans-proline",
    "pre-proline",
    "isoleucine / valine",
]

# Glob (inside the reference dir) for each type's Top8000 probability grid.
_REF_GLOBS = [
    "rama8000-general*",
    "rama8000-gly*",
    "rama8000-cispro*",
    "rama8000-transpro*",
    "rama8000-prepro*",
    "rama8000-ileval*",
]

# (allowed, favored) probability cutoffs used to draw the contours.
# NOTE: written from memory of MolProbity's per-type cutoffs -- check them
# against ramalyze.py in your Phenix version if the contours look off.
_CONTOUR_LEVELS = [
    (0.0005, 0.02),
    (0.001, 0.02),
    (0.002, 0.02),
    (0.001, 0.02),
    (0.0005, 0.02),
    (0.0005, 0.02),
]
_CONTOUR_COLORS = ("#6a5df2", "#4a9be8")  # allowed (outer), favored (inner)

# Panel order on the page, row by row: (res_type index, panel title).
_PANELS = [
    (0, "General case"),
    (5, "Isoleucine and valine"),
    (4, "Pre-proline"),
    (1, "Glycine"),
    (3, r"$\mathit{Trans}$ proline"),
    (2, r"$\mathit{Cis}$ proline"),
]

# Outlier marker colour per type. General / Ile-Val / Gly are read off the
# reference page; the three proline-related colours are my guess because the
# reference page had no outliers of those types.
_OUTLIER_COLORS = {
    0: "#d02fd0",
    5: "#e8261b",
    1: "#1fc46a",
    4: "#ff8c00",
    3: "#8b5a2b",
    2: "#00a6b8",
}

# Page geometry, in figure fractions, measured from the reference page.
_AX_W, _AX_H = 0.269, 0.2077
_COL_LEFT = (0.175, 0.569)
_ROW_TOP = (0.9155, 0.6632, 0.4109)
_TEXT_X0 = 0.0647  # left edge of the footer sentences
_ITEM_X = (0.077, 0.223, 0.369)  # x of the three outlier-list columns
_NUM_DX, _NAME_DX = 0.0265, 0.0306  # residue-number / name offsets in a row
_LINE_H = 0.01023
_FOOT_Y0 = 0.1727


def _pick_font(candidates: Sequence[str]) -> str:
    """First installed family from `candidates` (avoids findfont warnings)."""
    from matplotlib import font_manager

    have = {f.name for f in font_manager.fontManager.ttflist}
    for c in candidates:
        if c in have:
            return c
    return candidates[-1]


_SANS = _pick_font(["Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"])
_SERIF = _pick_font(["Times New Roman", "Liberation Serif", "DejaVu Serif"])


_FIND_ERRORS: List[str] = (
    []
)  # why libtbx-based lookup failed (shown by check_reference)


def _find_reference_dir() -> Optional[Path]:
    """Locate chem_data/rotarama_data.

    Order: libtbx repositories (the same lookup mmtbx itself uses), then
    mmtbx.rotamer's own helper, then $RAMA_REFERENCE_DIR, then
    $PHENIX/modules/chem_data/rotarama_data.
    """
    import os

    _FIND_ERRORS.clear()
    try:
        import libtbx.load_env  # noqa: F401  -- this is what defines libtbx.env
        import libtbx

        p = libtbx.env.find_in_repositories(
            relative_path="chem_data/rotarama_data", optional=True
        )
        if p:
            return Path(str(p))
        _FIND_ERRORS.append("libtbx.env.find_in_repositories returned None")
    except Exception as exc:
        _FIND_ERRORS.append(f"libtbx lookup failed: {exc!r}")
        log.debug("libtbx lookup failed", exc_info=True)
    try:
        from mmtbx.rotamer import find_rotarama_data_dir  # type: ignore

        p = find_rotarama_data_dir(optional=True)
        if p:
            return Path(str(p))
    except Exception as exc:
        _FIND_ERRORS.append(f"mmtbx.rotamer helper failed: {exc!r}")
    cands = []
    if os.environ.get("RAMA_REFERENCE_DIR"):
        cands.append(Path(os.environ["RAMA_REFERENCE_DIR"]))
    for var in ("PHENIX", "LIBTBX_BUILD"):
        if os.environ.get(var):
            root = Path(os.environ[var])
            cands += [
                root / "modules" / "chem_data" / "rotarama_data",
                root.parent / "modules" / "chem_data" / "rotarama_data",
            ]
    return next((c for c in cands if c.is_dir()), None)


_HDR = re.compile(r"#\s*x([12]):\s*(\S+)\s+(\S+)\s+(\d+)")


def _parse_grid(path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Parse a Top8000 table into (phis, psis, grid[psi, phi]).

    The files carry a header giving each axis as `lower upper bins wrapping`
    and then list (phi, psi, ..., value) rows -- but only the NON-ZERO cells
    for the proline/pre-Pro/Ile-Val tables. So the grid is rebuilt on the
    full regular lattice from the header, with unlisted cells = 0, rather
    than from whichever coordinates happen to appear. Falls back to the
    coordinates found in the file when there is no header.
    """
    opener = gzip.open if path.suffix == ".gz" else open
    dims: Dict[int, Tuple[float, float, int]] = {}
    rows = []
    with opener(path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                m = _HDR.match(line)
                if m:
                    dims[int(m.group(1))] = (
                        float(m.group(2)),
                        float(m.group(3)),
                        int(m.group(4)),
                    )
                continue
            tok = line.split()
            if len(tok) < 3:
                continue
            try:
                rows.append((float(tok[0]), float(tok[1]), float(tok[-1])))
            except ValueError:
                continue
    if not rows:
        raise ValueError(f"no numeric rows in {path}")
    a = np.asarray(rows)

    if 1 in dims and 2 in dims:
        (l1, u1, n1), (l2, u2, n2) = dims[1], dims[2]
        s1, s2 = (u1 - l1) / n1, (u2 - l2) / n2

        def index(x, lo, step, n):
            frac = float(np.median(((x - lo) / step) % 1.0))
            if frac > 0.999:  # coordinates sit on bin edges
                frac = 0.0
            return np.round((x - lo) / step - frac).astype(int) % n, frac

        i1, f1 = index(a[:, 0], l1, s1, n1)
        i2, f2 = index(a[:, 1], l2, s2, n2)
        grid = np.zeros((n2, n1))
        grid[i2, i1] = a[:, 2]
        return (l1 + (np.arange(n1) + f1) * s1, l2 + (np.arange(n2) + f2) * s2, grid)

    phis, psis = np.unique(a[:, 0]), np.unique(a[:, 1])
    grid = np.full((len(psis), len(phis)), np.nan)
    grid[np.searchsorted(psis, a[:, 1]), np.searchsorted(phis, a[:, 0])] = a[:, 2]
    return phis, psis, grid


def _grid_files(d: Path, t: int) -> List[Path]:
    """Data files for type t, text tables only (the dir also has .pickle)."""
    return [h for h in sorted(d.glob(_REF_GLOBS[t])) if h.suffix in (".data", ".gz")]


@lru_cache(maxsize=4)
def _load_reference(ref_dir: Optional[str]):
    """{res_type: (phis, psis, grid)}; empty dict if nothing usable found."""
    d = Path(ref_dir) if ref_dir else _find_reference_dir()
    if d is None or not d.is_dir():
        log.warning(
            "Ramachandran reference grids not found; plotting points "
            "without contours. Pass reference_dir=... to fix."
        )
        return {}
    out = {}
    for i, pat in enumerate(_REF_GLOBS):
        hits = _grid_files(d, i)
        if not hits:
            log.warning("no reference grid matching %s in %s", pat, d)
            continue
        try:
            out[i] = _parse_grid(hits[0])
        except Exception as exc:
            log.warning("could not parse %s: %s", hits[0], exc)
    return out


def check_reference(reference_dir: Optional[Union[str, Path]] = None) -> None:
    """Print where the Ramachandran reference grids were looked for and found,
    the head of each matched file, and how each grid relates to the contour
    cutoffs (share of total density at/above the favored and allowed cutoff;
    expect roughly 98% and 99.8%).

        python -c "import charts; charts.check_reference()"
    """
    d = Path(reference_dir) if reference_dir else _find_reference_dir()
    print("reference dir:", d)
    if d is None or not d.is_dir():
        print("  not found -- set RAMA_REFERENCE_DIR or pass reference_dir=")
        for e in _FIND_ERRORS:
            print("   ", e)
        return
    print("  contents:", ", ".join(sorted(p.name for p in d.iterdir()))[:600])
    for t, name in enumerate(RAMA_TYPES):
        hits = _grid_files(d, t)
        print(f"\n{name}: glob {_REF_GLOBS[t]!r} -> {[h.name for h in hits]}")
        if not hits:
            continue
        try:
            opener = gzip.open if hits[0].suffix == ".gz" else open
            with opener(hits[0], "rt") as fh:
                for _ in range(6):
                    print("    |", fh.readline().rstrip()[:100])
            phis, psis, grid = _parse_grid(hits[0])
        except Exception as exc:
            print("    PARSE FAILED:", repr(exc))
            continue
        g = np.nan_to_num(grid)
        lo, hi = _CONTOUR_LEVELS[t]
        tot = g.sum() or 1.0
        print(
            f"    parsed grid {g.shape}, {int((g > 0).sum())} non-zero cells, "
            f"min {g.min():.4g}, max {g.max():.4g}"
        )
        print(
            f"    mass >= favored cutoff {hi}: {100 * g[g >= hi].sum() / tot:5.1f}% (98)"
            f"   mass >= allowed cutoff {lo}: {100 * g[g >= lo].sum() / tot:5.2f}% (99.8)"
        )


_WARNED: set = set()


def _warn_once(key: str, msg: str, *args) -> None:
    if key not in _WARNED:
        _WARNED.add(key)
        log.warning(msg, *args)


def _contour_levels(g: np.ndarray, t: int) -> Tuple[float, float]:
    """(allowed, favored) contour levels for one grid.

    Normally the MolProbity cutoffs. If the grid's values never reach the
    favored cutoff (i.e. it is normalised differently from what the cutoffs
    assume, and no contour would be drawn at all), fall back to the levels
    that enclose 99.8% / 98% of the grid's total density -- which is what the
    'allowed' / 'favored' regions are defined to be.
    """
    lo, hi = _CONTOUR_LEVELS[t]
    if g.max() > hi:
        return lo, hi
    _warn_once(
        f"mass{t}",
        "reference grid for %s peaks at %.3g, below the "
        "favored cutoff %g; deriving contour levels from grid mass "
        "instead",
        RAMA_TYPES[t],
        g.max(),
        hi,
    )
    flat = np.sort(g.ravel())[::-1]
    cum = np.cumsum(flat) / flat.sum()
    pick = lambda q: float(flat[min(int(np.searchsorted(cum, q)), len(flat) - 1)])
    return pick(0.998), pick(0.98)


def check_cutoffs(
    points: Sequence[RamaPoint], reference_dir: Optional[Union[str, Path]] = None
) -> None:
    """Compare ramalyze's own favored/allowed/outlier call for each residue
    with the call implied by looking the residue up in the reference grid and
    applying _CONTOUR_LEVELS. Disagreements concentrated in one type mean
    that type's cutoffs are wrong.

        charts.check_cutoffs(charts.rama_points_from_mmtbx(mp_result.ramalyze))
    """
    from collections import Counter

    ref = _load_reference(str(reference_dir) if reference_dir else None)
    for t, name in enumerate(RAMA_TYPES):
        pts = [p for p in points if p.res_type == t]
        if t not in ref or not pts:
            print(
                f"  {name:22s} n={len(pts):4d}  (no grid)"
                if pts
                else f"  {name:22s} n=   0"
            )
            continue
        phis, psis, g = ref[t]
        lo, hi = _CONTOUR_LEVELS[t]
        conf: Counter = Counter()
        for p in pts:
            ix = int(round((p.phi - phis[0]) / (phis[1] - phis[0]))) % len(phis)
            iy = int(round((p.psi - psis[0]) / (psis[1] - psis[0]))) % len(psis)
            v = g[iy, ix]
            mine = "favored" if v >= hi else "allowed" if v >= lo else "outlier"
            conf[(p.status, mine)] += 1
        agree = sum(c for (a, b), c in conf.items() if a == b)
        bad = {f"{a}->{b}": c for (a, b), c in conf.items() if a != b}
        print(
            f"  {name:22s} n={len(pts):4d}  agree {100 * agree / len(pts):5.1f}%"
            f"   mismatches (ramalyze->grid): {bad or 'none'}"
        )


def _sort_key(p: RamaPoint):
    chain, num, ic = p.key
    return (chain, num if isinstance(num, int) else 0, ic)


def _res_label(p: RamaPoint) -> str:
    return f"{p.key[0]}  {p.key[1]}{p.key[2]} {p.resname.title()}"


def _draw_rama_panel(ax, t: int, title: str, pts: Sequence[RamaPoint], grid) -> None:
    ax.set_xlim(-180, 180)
    ax.set_ylim(-180, 180)
    ticks = list(range(-180, 181, 60))
    labels = ["-180", "", "", "0", "", "", "180"]  # labelled at -180/0/180 only
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(labels, fontsize=7, family=_SANS)
    ax.set_yticklabels(labels, fontsize=7, family=_SANS)
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.tick_params(which="major", length=4, width=0.5, pad=4)
    ax.tick_params(which="minor", length=2, width=0.4)
    for s in ax.spines.values():
        s.set_linewidth(0.5)
    ax.grid(True, which="major", color="#555555", lw=0.5)
    ax.set_axisbelow(True)
    ax.set_aspect("equal")

    if grid is not None:
        phis, psis, g = grid
        g = np.nan_to_num(g)
        lo, hi = _contour_levels(g, t)
        ax.contour(
            phis,
            psis,
            g,
            levels=[lo, hi],
            colors=list(_CONTOUR_COLORS),
            linewidths=1.1,
            zorder=2,
        )

    normal = [p for p in pts if p.status != "outlier"]
    if normal:
        ax.scatter(
            [p.phi for p in normal],
            [p.psi for p in normal],
            s=6,
            facecolors="none",
            edgecolors="black",
            linewidths=0.45,
            zorder=3,
        )
    outliers = [p for p in pts if p.status == "outlier"]
    if outliers:
        ax.scatter(
            [p.phi for p in outliers],
            [p.psi for p in outliers],
            s=9,
            facecolors="none",
            edgecolors=_OUTLIER_COLORS[t],
            linewidths=0.8,
            zorder=4,
        )
    for p in outliers:
        ax.annotate(
            _res_label(p),
            (p.phi, p.psi),
            xytext=(4, 0),
            textcoords="offset points",
            fontsize=5.5,
            family=_SERIF,
            va="center",
            ha="left",
            annotation_clip=False,
            zorder=5,
        )

    ax.set_title(title, fontsize=7, family=_SANS, pad=5)
    # "Psi"/"Phi" sit in the tick-label row/column, about 3/4 along each axis.
    ax.annotate(
        "Psi",
        xy=(0, 90),
        xycoords=ax.get_yaxis_transform(),
        xytext=(-8, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        fontsize=7,
        family=_SANS,
    )
    ax.annotate(
        "Phi",
        xy=(90, 0),
        xycoords=ax.get_xaxis_transform(),
        xytext=(0, -8),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=7,
        family=_SANS,
    )


def _draw_items(fig, items: Sequence[RamaPoint], columns, y0: float) -> None:
    """Fill (x, first_row, capacity) columns with 'A  59 Ala (phi, psi)' rows."""
    it = iter(items)
    for x, first_row, cap in columns:
        for k in range(cap):
            p = next(it, None)
            if p is None:
                return
            y = y0 - (first_row + k) * _LINE_H
            kw = dict(fontsize=6, family=_SERIF, va="center")
            fig.text(x, y, p.key[0], ha="left", **kw)
            fig.text(x + _NUM_DX, y, f"{p.key[1]}{p.key[2]}", ha="right", **kw)
            fig.text(
                x + _NAME_DX,
                y,
                f"{p.resname.title()} ({p.phi:.1f}, {p.psi:.1f})",
                ha="left",
                **kw,
            )


def _draw_credits(fig, left: str, right: str, url: Optional[str]) -> None:
    y = 0.045
    if left:
        t = fig.text(
            0.053,
            y,
            left,
            ha="left",
            va="center",
            fontsize=10.5,
            family=_SANS,
            color="#0000ee",
        )
        if url:
            t.set_url(url)
        try:  # underline: measure the text, draw a rule beneath it
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(
                fig.transFigure.inverted()
            )
            fig.add_artist(
                Line2D(
                    [bb.x0, bb.x1],
                    [bb.y0 - 0.001] * 2,
                    transform=fig.transFigure,
                    color="#0000ee",
                    lw=0.8,
                )
            )
        except Exception:
            pass
    if right:
        fig.text(0.944, y, right, ha="right", va="center", fontsize=10.5, family=_SANS)


def plot_ramachandran(
    points: Sequence[RamaPoint],
    out_pdf: Union[str, Path],
    pdb_id: str = "",
    reference_dir: Optional[Union[str, Path]] = None,
    subtitle: Optional[str] = None,
    title: str = "MolProbity Ramachandran analysis",
    credit_left: str = "http://kinemage.biochem.duke.edu",
    credit_url: Optional[str] = "http://kinemage.biochem.duke.edu",
    credit_right: str = "Lovell, Davis, et al. Proteins 50:437 (2003)",
) -> Path:
    """Ramachandran report: one portrait page, plus continuation pages only if
    the outlier list is too long for the first page's text block.

    subtitle  : line under the title (default "<pdb_id>, model 1")
    title / credit_* : page furniture copied from the reference layout;
                       pass "" to drop a credit line.
    """
    ref = _load_reference(str(reference_dir) if reference_dir else None)
    if subtitle is None:
        subtitle = f"{pdb_id}, model 1" if pdb_id else ""

    n = len(points)
    n_fav = sum(p.status == "favored" for p in points)
    n_allowed = n_fav + sum(p.status == "allowed" for p in points)
    outliers = sorted((p for p in points if p.status == "outlier"), key=_sort_key)

    def new_page() -> Figure:
        fig = Figure(figsize=(8.5, 11))
        FigureCanvasAgg(fig)  # gives the figure a renderer for text extents
        return fig

    # ---- page 1: panels + statistics + first 28 outliers ----
    fig = new_page()
    fig.text(0.5, 0.9645, title, ha="center", va="center", fontsize=16.5, family=_SANS)
    if subtitle:
        fig.text(
            0.5,
            0.937,
            subtitle,
            ha="center",
            va="center",
            fontsize=9.5,
            family=_SERIF,
            color="#444444",
        )
    for slot, (t, ptitle) in enumerate(_PANELS):
        row, col = divmod(slot, 2)
        ax = fig.add_axes((_COL_LEFT[col], _ROW_TOP[row] - _AX_H, _AX_W, _AX_H))
        _draw_rama_panel(
            ax, t, ptitle, [p for p in points if p.res_type == t], ref.get(t)
        )

    def pct(k: int) -> float:
        return 100.0 * k / max(n, 1)

    kw = dict(fontsize=6, family=_SERIF, va="center", ha="left")
    fig.text(
        _TEXT_X0,
        _FOOT_Y0,
        f"{pct(n_fav):.1f}% ({n_fav}/{n}) of all residues were in "
        "favored (98%) regions.",
        **kw,
    )
    fig.text(
        _TEXT_X0,
        _FOOT_Y0 - _LINE_H,
        f"{pct(n_allowed):.1f}% ({n_allowed}/{n}) of all residues were "
        "in allowed (>99.8%) regions.",
        **kw,
    )
    fig.text(
        _TEXT_X0,
        _FOOT_Y0 - 3 * _LINE_H,
        f"There were {len(outliers)} outliers (phi, psi):",
        **kw,
    )
    first_cols = [(_ITEM_X[0], 4, 8), (_ITEM_X[1], 4, 8), (_ITEM_X[2], 0, 12)]
    _draw_items(fig, outliers, first_cols, _FOOT_Y0)
    _draw_credits(fig, credit_left, credit_right, credit_url)
    pages = [fig]

    # ---- continuation pages for long outlier lists ----
    rest = outliers[sum(c[2] for c in first_cols) :]
    per_col = 80
    while rest:
        fig = new_page()
        fig.text(
            0.5,
            0.965,
            f"{title} (continued)",
            ha="center",
            va="center",
            fontsize=12,
            family=_SANS,
        )
        fig.text(_TEXT_X0, 0.935, f"Outliers (phi, psi), {subtitle}", **kw)
        cols = [(x, 0, per_col) for x in _ITEM_X]
        _draw_items(fig, rest, cols, 0.91)
        _draw_credits(fig, credit_left, credit_right, credit_url)
        pages.append(fig)
        rest = rest[3 * per_col :]

    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_pdf) as pdf:
        for f in pages:
            pdf.savefig(f)
    return out_pdf


# --------------------------------------------------------------------------
# Multi-criterion strip chart
# --------------------------------------------------------------------------

_LEVEL_COLORS = ["#e4e4e4", "#cfe8cf", "#f2c94c", "#d62728"]
_CMAP = ListedColormap(_LEVEL_COLORS)
_NORM = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], _CMAP.N)


def plot_multichart(
    residues: Sequence[Residue],
    tracks: Sequence[Track],
    out_pdf: Union[str, Path],
    pdb_id: str = "",
    residues_per_row: int = 100,
    rows_per_page: int = 6,
) -> Path:
    """Per-residue strip chart, paginated. `residues` must be in chain order."""
    if not tracks:
        raise ValueError("plot_multichart needs at least one Track")

    # Split each chain into fixed-width segments so all rows share one scale.
    by_chain: Dict[str, List[Residue]] = {}
    for r in residues:
        by_chain.setdefault(r.key[0], []).append(r)
    segments = [
        (cid, rs[i : i + residues_per_row])
        for cid, rs in by_chain.items()
        for i in range(0, len(rs), residues_per_row)
    ]
    if not segments:
        raise ValueError("no residues to plot")

    bvals = [r.b_mean for r in residues if r.b_mean is not None]
    bnorm = Normalize(min(bvals), max(bvals)) if bvals else None

    counts = {t.name: sum(t.level(r.key) == OUTLIER for r in residues) for t in tracks}
    summary = "   ".join(f"{k}: {v}" for k, v in counts.items())

    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_pdf) as pdf:
        for start in range(0, len(segments), rows_per_page):
            fig = Figure(figsize=(11, 8.5))
            gs = GridSpec(
                rows_per_page,
                1,
                figure=fig,
                left=0.08,
                right=0.98,
                top=0.90,
                bottom=0.10,
                hspace=0.75,
            )
            for slot, (cid, seg) in enumerate(segments[start : start + rows_per_page]):
                _draw_segment(fig, gs[slot], cid, seg, tracks, residues_per_row, bnorm)
            fig.suptitle(f"{pdb_id}  per-residue validation", fontsize=11, y=0.975)
            fig.text(
                0.5,
                0.935,
                f"outlier counts -- {summary}",
                ha="center",
                fontsize=7,
                color="0.3",
            )
            fig.legend(
                handles=[
                    Patch(color=_LEVEL_COLORS[NA], label="not assessed"),
                    Patch(color=_LEVEL_COLORS[OK], label="ok"),
                    Patch(color=_LEVEL_COLORS[WARN], label="warning / allowed"),
                    Patch(color=_LEVEL_COLORS[OUTLIER], label="outlier"),
                ],
                loc="lower left",
                ncol=4,
                fontsize=7,
                frameon=False,
                bbox_to_anchor=(0.06, 0.005),
            )
            if bnorm is not None:
                cax = fig.add_axes((0.72, 0.05, 0.22, 0.012))
                cb = fig.colorbar(
                    ScalarMappable(bnorm, "viridis"), cax=cax, orientation="horizontal"
                )
                cb.set_label("mean B (A^2)", fontsize=6)
                cb.ax.tick_params(labelsize=6)
            pdf.savefig(fig)
    return out_pdf


def _draw_segment(fig, spec, chain_id, seg, tracks, width, bnorm) -> None:
    n = len(seg)
    sub = GridSpecFromSubplotSpec(
        2, 1, subplot_spec=spec, height_ratios=[len(tracks), 1.1], hspace=0.06
    )
    ax = fig.add_subplot(sub[0])
    axb = fig.add_subplot(sub[1], sharex=ax)

    data = np.array([[t.level(r.key) for r in seg] for t in tracks])
    ax.imshow(data, cmap=_CMAP, norm=_NORM, aspect="auto", interpolation="nearest")
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_yticks(range(len(tracks)))
    ax.set_yticklabels([t.name for t in tracks], fontsize=6)
    ax.tick_params(axis="x", labelbottom=False, length=0)
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(tracks), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.5)
    ax.tick_params(which="minor", length=0)
    ax.set_title(
        f"chain {chain_id}   {seg[0].label} - {seg[-1].label}",
        fontsize=7,
        loc="left",
        pad=2,
    )

    if bnorm is not None:
        b = np.array([[np.nan if r.b_mean is None else r.b_mean for r in seg]])
        axb.imshow(
            b, cmap="viridis", norm=bnorm, aspect="auto", interpolation="nearest"
        )
    axb.set_xlim(-0.5, width - 0.5)
    axb.set_yticks([0])
    axb.set_yticklabels(["B"], fontsize=6)
    tick_idx = list(range(0, n, 10))
    axb.set_xticks(tick_idx)
    axb.set_xticklabels([seg[i].label for i in tick_idx], fontsize=5, rotation=90)
    axb.tick_params(axis="x", length=2)


# --------------------------------------------------------------------------
# mmtbx adapters
#
# These are written against the mmtbx.validation result objects as I know
# them (ramalyze/rotalyze/cbetadev/clashscore/cablam) but were NOT run
# against a live Phenix install. They read attributes defensively; if one
# is missing you get an error naming it, and the fix is local to this
# section.
# --------------------------------------------------------------------------


def _flag(obj: Any, name: str) -> bool:
    f = getattr(obj, name, None)
    return bool(f() if callable(f) else f)


def _key_of(obj: Any) -> Key:
    try:
        return make_key(obj.chain_id, obj.resseq, getattr(obj, "icode", ""))
    except AttributeError as exc:
        raise AttributeError(
            f"{type(obj).__name__} lacks chain_id/resseq ({exc}); build the "
            "chart data classes by hand for this result type"
        ) from exc


def _results(obj: Any) -> Iterable[Any]:
    return getattr(obj, "results", obj)


def residues_from_hierarchy(hierarchy: Any) -> List[Residue]:
    """Polymer residues (protein + nucleic acid) of the first model."""
    out: List[Residue] = []
    model = hierarchy.models()[0]
    for chain in model.chains():
        if not (chain.is_protein() or chain.is_na()):
            continue
        for rg in chain.residue_groups():
            bs = list(rg.atoms().extract_b())
            names = rg.unique_resnames()
            out.append(
                Residue(
                    key=make_key(chain.id, rg.resseq_as_int(), rg.icode),
                    resname=names[0].strip() if names else "",
                    b_mean=(sum(bs) / len(bs)) if bs else None,
                )
            )
    return out


def _rama_status(r: Any) -> str:
    """'outlier' | 'allowed' | 'favored' from whatever the result exposes.

    Tries, in order: is_outlier(); is_allowed(); is_favored() (not favored =>
    allowed); a ramalyze_type() / rama_type string such as 'Allowed'. If none
    can tell allowed from favored the residue is reported as favored.
    """
    if _flag(r, "is_outlier"):
        return "outlier"
    if hasattr(r, "is_allowed") and _flag(r, "is_allowed"):
        return "allowed"
    if hasattr(r, "is_favored"):
        return "favored" if _flag(r, "is_favored") else "allowed"
    for name in ("ramalyze_type", "rama_type"):
        v = getattr(r, name, None)
        if callable(v):
            try:
                v = v()
            except Exception:
                v = None
        if isinstance(v, str):
            low = v.lower()
            for key, st in (
                ("outlier", "outlier"),
                ("allow", "allowed"),
                ("favor", "favored"),
            ):
                if key in low:
                    return st
    return "favored"


def rama_points_from_mmtbx(rama: Any) -> List[RamaPoint]:
    pts = []
    rs = list(_results(rama))
    # ramalyze covers every model in the file; the reference page shows model 1.
    mids = [getattr(r, "model_id", None) for r in rs]
    first = next((m for m in mids if m is not None), None)
    if first is not None:
        rs = [r for r, m in zip(rs, mids) if m == first]
    for r in rs:
        if getattr(r, "phi", None) is None or getattr(r, "psi", None) is None:
            continue
        pts.append(
            RamaPoint(
                key=_key_of(r),
                resname=str(getattr(r, "resname", "")).strip(),
                phi=float(r.phi),
                psi=float(r.psi),
                res_type=int(getattr(r, "res_type", 0)),
                status=_rama_status(r),
            )
        )
    if len(pts) > 300 and not any(p.status == "allowed" for p in pts):
        _warn_once(
            "noallowed",
            "no 'allowed' residues among %d Ramachandran "
            "results -- status attributes may be misread; run "
            "charts.describe_results(rama)",
            len(pts),
        )
    return pts


def describe_results(results: Any, n: int = 1) -> None:
    """Dump the attributes/zero-arg methods of the first `n` result objects
    plus the status counts this module derives, to debug adapter mismatches.

        charts.describe_results(mp_result.ramalyze)
    """
    from collections import Counter

    rs = list(_results(results))
    print(f"{len(rs)} results, type {type(rs[0]).__name__ if rs else None}")
    for r in rs[:n]:
        for name in sorted(x for x in dir(r) if not x.startswith("_")):
            try:
                v = getattr(r, name)
                if callable(v):
                    try:
                        v = "()-> " + repr(v())
                    except TypeError:
                        v = "<method, needs args>"
                print(f"  {name:22s} {str(v)[:90]}")
            except Exception as exc:
                print(f"  {name:22s} <error {exc!r}>")
    if rs:
        print("derived status counts:", dict(Counter(_rama_status(r) for r in rs)))


def rama_track(points: Sequence[RamaPoint]) -> Track:
    lv = {"favored": OK, "allowed": WARN, "outlier": OUTLIER}
    return Track("Rama", {p.key: lv[p.status] for p in points})


def rota_track(rota: Any) -> Track:
    return Track(
        "Rotamer",
        {_key_of(r): OUTLIER if _flag(r, "is_outlier") else OK for r in _results(rota)},
    )


def cbeta_track(cbeta: Any, cutoff: float = 0.25) -> Track:
    lv = {}
    for r in _results(cbeta):
        out = (
            _flag(r, "is_outlier")
            if hasattr(r, "is_outlier")
            else getattr(r, "deviation", 0.0) >= cutoff
        )
        lv[_key_of(r)] = OUTLIER if out else OK
    return Track("C-beta", lv)


def clash_track(clashes: Any) -> Track:
    lv: Dict[Key, int] = {}
    for c in _results(clashes):
        for a in getattr(c, "atoms_info", []):
            lv[_key_of(a)] = OUTLIER
    return Track("Clash", lv, default=OK)


def cablam_track(cablam: Any) -> Track:
    lv = {}
    for r in _results(cablam):
        fb = getattr(r, "feedback", r)
        if getattr(fb, "cablam_outlier", False):
            lv[_key_of(r)] = OUTLIER
        elif getattr(fb, "cablam_disfavored", False) or getattr(
            fb, "c_alpha_geom_outlier", False
        ):
            lv[_key_of(r)] = WARN
        else:
            lv[_key_of(r)] = OK
    return Track("CaBLAM", lv)


# --------------------------------------------------------------------------
# Orchestrator entry point
# --------------------------------------------------------------------------


def write_charts(
    pdb_id: str,
    hierarchy: Any,
    out_dir: Union[str, Path],
    rama: Any = None,
    rota: Any = None,
    cbeta: Any = None,
    clashes: Any = None,
    cablam: Any = None,
    extra_tracks: Sequence[Track] = (),
    reference_dir: Optional[Union[str, Path]] = None,
    subtitle: Optional[str] = None,
    strict: bool = False,
) -> Dict[str, Path]:
    """Write {pdb_id}_rama.pdf and {pdb_id}_multichart.pdf into out_dir.

    Any validation result may be None (that criterion is skipped). With
    strict=False (default, suited to batch runs) a failure in one chart is
    logged and the other is still attempted; strict=True re-raises.
    """
    out_dir = Path(out_dir)
    written: Dict[str, Path] = {}

    points: List[RamaPoint] = []
    try:
        if rama is not None:
            points = rama_points_from_mmtbx(rama)
            written["rama"] = plot_ramachandran(
                points,
                out_dir / f"{pdb_id}_rama.pdf",
                pdb_id,
                reference_dir,
                subtitle=subtitle,
            )
    except Exception:
        log.exception("%s: Ramachandran chart failed", pdb_id)
        if strict:
            raise

    try:
        tracks: List[Track] = []
        if points:
            tracks.append(rama_track(points))
        for res, fn in (
            (rota, rota_track),
            (cbeta, cbeta_track),
            (clashes, clash_track),
            (cablam, cablam_track),
        ):
            if res is not None:
                tracks.append(fn(res))
        tracks.extend(extra_tracks)
        if tracks:
            written["multichart"] = plot_multichart(
                residues_from_hierarchy(hierarchy),
                tracks,
                out_dir / f"{pdb_id}_multichart.pdf",
                pdb_id,
            )
    except Exception:
        log.exception("%s: multichart failed", pdb_id)
        if strict:
            raise
    return written
