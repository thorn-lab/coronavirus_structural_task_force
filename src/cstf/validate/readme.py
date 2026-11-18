"""Write an entry's README.md from the persisted validation summaries.

All validation figures come from ``validation/validation_summary.json``,
which each step fills through ``ValidationStep.summarize``; this step never
parses tool output. The only other sources are the model mmCIF (for the
description), the entry's file layout, and external links, each of which is
checked before it is written.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Callable, Mapping

import requests

from cstf.validate.base import Entry, ValidationStep, succeeded

logger = logging.getLogger("xtal_validation.orchestrator.readme")

README_NAME = "README.md"
WATER_IDS = {"HOH", "DOD", "WAT"}

STEP_LABELS = {
    "pdb_redo": "PDB-REDO",
    "auspex": "AUSPEX",
    "haruspex": "HARUSPEX",
    "em_map_fit": "EM model-map fit",
    "xtriage": "XTRIAGE",
    "cablam": "CaBLAM",
    "clashscore": "Clashscore",
    "reduce": "Reduce",
    "molprobity": "MOLPROBITY",
    "charts": "MolProbity charts",
    "checkmymetal": "CheckMyMetal",
}
# Steps whose output all lives in validation/molprobity.
MOLPROBITY_FAMILY = ("molprobity", "cablam", "clashscore", "reduce", "charts")

# Web pages to link, each with an API URL that answers 404 for unknown IDs
# (the pages themselves return 200 for any ID, so they cannot be checked).
RCSB_PAGE = "https://www.rcsb.org/structure/{id}"
RCSB_PROBE = "https://data.rcsb.org/rest/v1/core/entry/{id}"
PDBE_PAGE = "https://www.ebi.ac.uk/pdbe/entry/pdb/{id}"
PDBE_PROBE = "https://www.ebi.ac.uk/pdbe/api/pdb/entry/summary/{id}"
LIGAND_PAGE = "https://www.rcsb.org/ligand/{id}"
LIGAND_PROBE = "https://data.rcsb.org/rest/v1/core/chemcomp/{id}"
EMDB_PAGE = "https://www.ebi.ac.uk/emdb/{emd}"
EMDB_MAP_DIR = "https://files.wwpdb.org/pub/emdb/structures/{emd}/map/"


class LinkChecker:
    """Cache-backed check that a URL (or its probe URL) resolves."""

    def __init__(self, timeout: float = 20, get: Callable = requests.get):
        self.timeout = timeout
        self._get = get
        self._cache: dict[str, bool] = {}

    def exists(self, url: str, probe: str | None = None) -> bool:
        target = probe or url
        if target not in self._cache:
            try:
                response = self._get(target, timeout=self.timeout, stream=True)
                response.close()
                self._cache[target] = response.status_code < 400
            except requests.RequestException as exc:
                logger.warning("Could not verify %s: %s", target, exc)
                return False  # not cached: a later entry may succeed
            if not self._cache[target]:
                logger.info("Link target missing, not linking: %s", target)
        return self._cache[target]


class WriteReadmeStep(ValidationStep):
    """Render README.md for one entry from all recorded validation results."""

    name = "readme"
    record_result = False

    def __init__(
        self,
        *,
        skip_existing=True,
        step_classes: Mapping[str, type[ValidationStep]] | None = None,
        link_checker: LinkChecker | None = None,
        **options,
    ):
        super().__init__(skip_existing=skip_existing, **options)
        # Validation steps the README reports on, in display order.
        self.step_classes = dict(step_classes or {})
        self.links = link_checker or LinkChecker()

    def target(self, entry: Entry) -> Path:
        return entry.path / README_NAME

    def execute(self, entry: Entry) -> Path:
        text = render_readme(entry, entry.load_summary(), self.step_classes, self.links)
        target = self.target(entry)
        temporary = target.with_suffix(".md.tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(target)
        return target


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_readme(entry, summary, step_classes, links: LinkChecker) -> str:
    done = {
        name: record.get("data", {})
        for name, record in summary.items()
        if succeeded(record.get("status", ""))
    }
    sections = [
        "# PDB {}".format(entry.pdb_id.lower()),
        _overview(entry),
        _description(entry, links),
        _basefolder(entry),
        _subfolders(entry, done),
        _maps(entry, links),
        _data_summary(entry, done),
        _haruspex(entry, done.get("haruspex")),
        _checkmymetal(entry, done.get("checkmymetal")),
        _not_performed(entry, summary, step_classes),
        _external_links(entry, links),
    ]
    return "\n\n".join(section for section in sections if section) + "\n"


def _overview(entry) -> str:
    # Entries live at pdb/<protein>/<organism>/<pdb_id>.
    protein = entry.path.parent.parent.name.replace("_", " ")
    organism = entry.path.parent.name
    return "## Overview\n\n**Protein name**: {}\n\n**Organism**: {}".format(
        protein, organism
    )


def _description(entry, links) -> str:
    """Part of {group title}. {group description} The potential binding ligand(s): ..."""
    cif = _model_cif(entry)
    if cif is None:
        return ""
    try:
        import gemmi

        block = gemmi.cif.read(str(cif)).sole_block()
    except Exception as exc:  # noqa: BLE001 - a broken cif only loses the description
        logger.warning("Could not read %s for the description: %s", cif, exc)
        return ""

    def values(tag):
        return [gemmi.cif.as_string(v).strip() for v in block.find_values(tag)]

    titles = [v for v in values("_pdbx_deposit_group.group_title") if v]
    descriptions = [v for v in values("_pdbx_deposit_group.group_description") if v]
    ligands = sorted(
        {v for v in values("_pdbx_entity_nonpoly.comp_id") if v and v not in WATER_IDS}
    )

    parts = []
    if titles:
        parts.append("Part of {}.".format(titles[0].rstrip(".")))
    if descriptions:
        description = " ".join(descriptions[0].split())
        parts.append(description if description.endswith(".") else description + ".")
    if ligands:
        parts.append(
            "The potential binding ligand(s): {}.".format(
                ", ".join(
                    _link(code, LIGAND_PAGE.format(id=code), LIGAND_PROBE.format(id=code), links)
                    for code in ligands
                )
            )
        )
    return "## Description\n\n" + " ".join(parts) if parts else ""


def _basefolder(entry) -> str:
    lines = []
    models = [p for p in (entry.files.get("pdb"), _model_cif(entry)) if p]
    if models:
        lines.append(
            "{} - the coordinates of the three-dimensional molecular model".format(
                " and ".join(p.name for p in models)
            )
        )
    for path in sorted(entry.path.glob("*-sf.cif")):
        lines.append("{} - deposited diffraction data for this PDB entry".format(path.name))
    if entry.files.get("mtz"):
        lines.append(
            "{} - deposited structure factors converted to MTZ".format(entry.files["mtz"].name)
        )
    return "## Basefolder\n\n" + "\n\n".join(lines) if lines else ""


def _subfolders(entry, done) -> str:
    lines = []
    isolde = entry.path / "isolde"
    if isolde.is_dir():
        info = isolde / "directory_info.txt"
        lines.append(
            "**isolde** - contains manual re-refinements from ISOLDE in ChimeraX. "
            "See details [here]({})".format(entry.rel(info if info.is_file() else isolde))
        )
    if (entry.path / "old").is_dir():
        lines.append("**old** - contains files from historical revisions")
    tools = _validation_links(entry, done)
    if tools:
        lines.append(
            "**validation** - contains validation reports. This structure has been "
            "analyzed by <br>" + " ".join(tools)
        )
    return "## Subfolders\n\n" + "\n\n".join(lines) if lines else ""


def _validation_links(entry, done) -> list[str]:
    targets = []
    if "pdb_redo" in done:
        targets.append(("PDB-REDO", done["pdb_redo"].get("directory")))
    if "auspex" in done:
        plot = done["auspex"].get("plot")
        targets.append(("AUSPEX", str(Path(plot).parent) if plot else None))
    if "haruspex" in done:
        targets.append(("HARUSPEX", done["haruspex"].get("directory")))
    if "em_map_fit" in done:
        targets.append(("EM MODEL-MAP FIT", done["em_map_fit"].get("report")))
    if any(name in done for name in MOLPROBITY_FAMILY):
        targets.append(("MOLPROBITY", entry.rel(entry.molprobity_dir)))
    if "xtriage" in done:
        targets.append(("XTRIAGE", done["xtriage"].get("log")))
    if done.get("checkmymetal", {}).get("files"):
        targets.append(("CHECKMYMETAL", done["checkmymetal"].get("directory")))
    return [
        "[**{}**]({})".format(label, path)
        for label, path in targets
        if path and (entry.path / path).exists()
    ]


def _maps(entry, links) -> str:
    if not entry.is_em:
        return ""
    from cstf.validate.haruspex import HaruspexStep

    primary = HaruspexStep.find_map(entry.path)
    if primary is None:
        return ""
    text = "Primary map {} available.".format(primary.name)
    match = re.search(r"emd[_-](\d+)", primary.name, re.IGNORECASE)
    if match:
        emd = "EMD-{}".format(match.group(1))
        if links.exists(EMDB_MAP_DIR.format(emd=emd)):
            text += " **Click** [here]({})".format(EMDB_MAP_DIR.format(emd=emd))
        if links.exists(EMDB_PAGE.format(emd=emd)):
            text += "\n\n**EMDB**: {}".format(EMDB_PAGE.format(emd=emd))
    return "## Maps\n\n" + text


def _data_summary(entry, done) -> str:
    blocks = []
    xtriage = done.get("xtriage")
    if xtriage:
        blocks.append(
            "**Diffraction Data Quality** (xtriage)\n\n"
            + _table(
                ["Resolution", "Completeness", "I/sigma"],
                [
                    _fmt(xtriage.get("d_min"), "{:.2f} Å"),
                    _fmt(xtriage.get("completeness"), "{:.1f} %"),
                    _fmt(xtriage.get("i_over_sigma"), "{:.2f}"),
                ],
            )
        )
    molprobity = done.get("molprobity", {})
    if molprobity.get("r_work") is not None or molprobity.get("r_free") is not None:
        blocks.append(
            "**Discrepancy between model and data** (MolProbity; the lower, the better)\n\n"
            + _table(
                ["R-work", "R-free"],
                [_fmt(molprobity.get("r_work"), "{:.4f}"), _fmt(molprobity.get("r_free"), "{:.4f}")],
            )
        )
    em = done.get("em_map_fit")
    if em and "programs" in em:
        blocks.append(
            "**Model-map fit** ({}, settings of the CCP-EM atomic model validation job)\n\n".format(
                em["programs"]
            )
            + _table(
                ["Resolution used", "FSCavg", "CCC (mask)", "MI (mask)", "SMOC outliers"],
                [
                    "{} ({})".format(
                        _fmt(em.get("resolution"), "{:.2f} Å"), em.get("resolution_source", "")
                    ),
                    _fmt(em.get("fsc_avg"), "{:.3f}"),
                    _fmt(em.get("ccc_mask"), "{:.3f}"),
                    _fmt(em.get("mi_mask"), "{:.3f}"),
                    _fmt(em.get("smoc_outlier_percent"), "{:.1f} %"),
                ],
            )
            + "\n\nFSCavg: servalcat model-masked FSC averaged up to the resolution used. "
            "CCC and MI: TEMPy, within the map contoured at {} ({}). SMOC outliers: "
            "residues with a SMOC Z-score below {} relative to residues within 12 Å.".format(
                _fmt(em.get("contour"), "{:.4g}"),
                em.get("contour_source", ""),
                em.get("smoc_outlier_z", "–"),
            )
        )
    cablam = done.get("cablam", {})
    clashscore = molprobity.get("clashscore")
    if clashscore is None:
        clashscore = done.get("clashscore", {}).get("clashscore")
    geometry = [
        _fmt(molprobity.get("molprobity_score"), "{:.2f}"),
        _fmt(clashscore, "{:.2f}"),
        _fmt(molprobity.get("rama_outliers_percent"), "{:.2f} %"),
        _fmt(cablam.get("outliers_percent"), "{:.1f} %"),
        _fmt(cablam.get("ca_geom_outliers_percent"), "{:.2f} %"),
    ]
    if any(value != "–" for value in geometry):
        blocks.append(
            "**Geometry validation (the lower, the better)**\n\n"
            + _table(
                [
                    "MolProbity<br>score",
                    "Clashscore",
                    "Ramachandran<br>outliers",
                    "CaBLAM<br>Conformation outliers",
                    "CaBLAM<br>CA outliers",
                ],
                geometry,
            )
        )
    return "## Data Summary\n\n" + "\n\n".join(blocks) if blocks else ""


def _haruspex(entry, haruspex) -> str:
    if not haruspex:
        return ""
    text = (
        "Available. This separates the deposited map into individual maps for "
        "alpha-helical, beta sheet and RNA/DNA."
    )
    files = [f for f in haruspex.get("files", []) if (entry.path / f).is_file()]
    if files:
        text += " Maps: " + ", ".join("[{}]({})".format(Path(f).name, f) for f in files)
    render = haruspex.get("render")
    if render and (entry.path / render).is_file():
        text += "\n\n![Haruspex annotation]({})".format(render)
    return "## HARUSPEX results\n\n" + text


def _checkmymetal(entry, checkmymetal) -> str:
    files = [f for f in (checkmymetal or {}).get("files", []) if (entry.path / f).is_file()]
    if not files:
        return ""
    return "## CheckMyMetal results\n\nMetal-binding site images: " + ", ".join(
        "[{}]({})".format(Path(f).name, f) for f in files
    )


def _not_performed(entry, summary, step_classes) -> str:
    """List steps without results: not run yet, missing input, or failed."""
    lines = []
    for name, step_class in step_classes.items():
        record = summary.get(name)
        status = record.get("status", "") if record else None
        if status is not None and succeeded(status):
            continue
        if status is None:
            # Never attempted: ask the step whether it would apply at all.
            reason = step_class().check_input(entry)
            if reason and reason.startswith("not_applicable"):
                continue
            status = reason or "not_run"
        if status.startswith("not_applicable"):
            continue
        lines.append("- **{}**: {}".format(STEP_LABELS.get(name, name), _reason(status)))
    if not lines:
        return ""
    return "## Validation not performed\n\n" + "\n".join(lines)


def _reason(status: str) -> str:
    kind, _, detail = status.partition(":")
    detail = re.sub(r"\x1b\[[0-9;]*m", "", detail)  # drop ANSI colours
    detail = " ".join(detail.split())
    if len(detail) > 200:
        detail = detail[:197] + "..."
    if kind == "not_run":
        return "not run yet"
    if kind == "no_input":
        return "skipped, missing input ({})".format(detail)
    if kind == "error":
        return "failed ({})".format(detail) if detail else "failed"
    return status


def _external_links(entry, links) -> str:
    pdb_id = entry.pdb_id.lower()
    lines = []
    for label, page, probe in (
        ("PDBe", PDBE_PAGE, PDBE_PROBE),
        ("PDBr", RCSB_PAGE, RCSB_PROBE),
    ):
        url = page.format(id=pdb_id)
        if links.exists(url, probe.format(id=pdb_id)):
            lines.append("**{}**: {}".format(label, url))
    return "## Other relevant links\n\n" + "\n\n".join(lines) if lines else ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _model_cif(entry) -> Path | None:
    cif = entry.files.get("cif")
    return cif if cif and not cif.name.lower().endswith("-sf.cif") else None


def _link(text, url, probe, links) -> str:
    return "[{}]({})".format(text, url) if links.exists(url, probe) else text


def _fmt(value, pattern, missing="–") -> str:
    return missing if value is None else pattern.format(value)


def _table(headers, row) -> str:
    return "\n".join(
        [
            "|   | " + " | ".join(headers) + " |",
            "|---|" + "|".join("-------------:" for _ in headers) + "|",
            "|   | " + " | ".join(row) + " |",
        ]
    )
