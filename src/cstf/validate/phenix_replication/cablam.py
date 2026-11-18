"""CaBLAM validation for a single model."""

from pathlib import Path

import iotbx.pdb
from mmtbx.validation import cablam as cablam_module
from cstf.validate.base import Entry, ValidationStep




class CablamStep(ValidationStep):
    """Run CaBLAM analysis for one model."""

    name = "cablam"

    def check_input(self, entry: Entry):
        return None if entry.model_path else "no_input: no model file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.molprobity_dir

    def target(self, entry: Entry) -> Path:
        return entry.molprobity_dir / "cablam.out"

    def is_complete(self, entry: Entry) -> bool:
        return self.target(entry).is_file()

    @staticmethod
    def _percent(value, total):
        return 100.0 * value / total if total else 0.0

    def execute(self, entry: Entry):
        pdb_input = iotbx.pdb.input(file_name=str(entry.model_path))
        hierarchy = pdb_input.construct_hierarchy()
        hierarchy.atoms().reset_i_seq()
        result = cablam_module.cablamalyze(
            pdb_hierarchy=hierarchy, out=None, outliers_only=False, quiet=True
        )
        self.target(entry).write_text(
            self._format_report(result, str(entry.model_path)) + "\n"
        )
        entry.results[self.name] = result
        return result

    def summarize(self, entry: Entry, result) -> dict:
        stats = result.summary_stats
        residues = stats["residue_count"]
        return {
            "report": entry.rel(self.target(entry)),
            "residue_count": int(residues),
            "outliers_percent": self._percent(stats["cablam_outliers"], residues),
            "disfavored_percent": self._percent(stats["cablam_disfavored"], residues),
            "ca_geom_outliers_percent": self._percent(stats["ca_geom_outliers"], residues),
        }

    def _format_report(self, result, model_path):
        lines = []

        lines.append(
            "residue : outlier_type : contour_level : ca_contour_level : "
            "sec struc recommendation : alpha score : beta score : three-ten score"
        )

        # Detailed residue results
        for r in result.iter_results():
            if not r.outlier:
                continue

            row = r.as_table_row_phenix()

            (
                chain_id,
                residue,
                outlier_type,
                contour_level,
                ca_contour_level,
                recommendation,
                alpha_score,
                beta_score,
                three_ten_score,
            ) = row

            lines.append(
                "{:>2} {}: {:<20}:{:.5f}:{:.5f}:{:<17}:"
                "{:.5f}:{:.5f}:{:.5f}".format(
                    chain_id,
                    residue,
                    outlier_type,
                    float(contour_level),
                    float(ca_contour_level),
                    recommendation or "",
                    float(alpha_score),
                    float(beta_score),
                    float(three_ten_score),
                )
            )

        # Summary
        stats = result.summary_stats

        residue_count = stats["residue_count"]
        ca_residue_count = stats["ca_residue_count"]
        disfavored = stats["cablam_disfavored"]
        outliers = stats["cablam_outliers"]
        ca_geom = stats["ca_geom_outliers"]

        alpha_count = stats["alpha_count"]
        beta_count = stats["beta_count"]

        correctable_helix = stats["correctable_helix_count"]
        correctable_beta = stats["correctable_beta_count"]

        lines.append(
            "SUMMARY: Note: Regardless of number of alternates, each residue "
            "is counted as having at most one outlier."
        )

        lines.append(
            "SUMMARY: CaBLAM found {} full protein residues and {} CA-only residues".format(
                residue_count,
                max(0, ca_residue_count - residue_count),
            )
        )

        lines.append(
            "SUMMARY: {} residues ({:.1f}%) have disfavored conformations. "
            "(<=5% expected).".format(
                disfavored,
                self._percent(disfavored, residue_count),
            )
        )

        lines.append(
            "SUMMARY: {} residues ({:.1f}%) have outlier conformations. "
            "(<=1% expected)".format(
                outliers,
                self._percent(outliers, residue_count),
            )
        )

        lines.append(
            "SUMMARY: {} residues ({:.2f}%) have severe CA geometry outliers. "
            "(<=0.5% expected)".format(
                ca_geom,
                self._percent(ca_geom, residue_count),
            )
        )

        lines.append(
            "SUMMARY: {} residues ({:.2f}%) are helix-like, "
            "{} residues ({:.2f}%) are beta-like".format(
                alpha_count,
                self._percent(alpha_count, residue_count),
                beta_count,
                self._percent(beta_count, residue_count),
            )
        )

        lines.append(
            "SUMMARY: {} residues ({:.2f}%) are correctable to helix, "
            "{} residues ({:.2f}%) are correctable to beta".format(
                correctable_helix,
                self._percent(correctable_helix, residue_count),
                correctable_beta,
                self._percent(correctable_beta, residue_count),
            )
        )

        return "\n".join(lines)
