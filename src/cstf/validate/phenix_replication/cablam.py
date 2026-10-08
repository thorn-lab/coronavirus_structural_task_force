"""
cablam.py

Open-source replacement for `phenix.cablam`, built on
mmtbx.validation.cablam - the CaBLAM backbone-conformation validation
(CA-based Local Analysis of Backbone), useful particularly for flagging
suspect loop geometry that Ramachandran analysis alone can miss.

Usage:
    python cablam.py model.pdb
    python cablam.py model.pdb --out cablam.out
    python cablam.py model.pdb --kinemage cablam.kin
"""

import argparse
import io
import sys

import iotbx.pdb
from mmtbx.validation import cablam as cablam_module


def run_cablam(model_path):
    pdb_input = iotbx.pdb.input(file_name=model_path)
    pdb_hierarchy = pdb_input.construct_hierarchy()
    pdb_hierarchy.atoms().reset_i_seq()

    result = cablam_module.cablamalyze(
        pdb_hierarchy=pdb_hierarchy,
        out=None,
        outliers_only=False,
        quiet=True,
    )

    return result


def format_report(result, model_path):
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

    def pct(n, total):
        return 100.0 * n / total if total else 0.0

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
            pct(disfavored, residue_count),
        )
    )

    lines.append(
        "SUMMARY: {} residues ({:.1f}%) have outlier conformations. "
        "(<=1% expected)".format(
            outliers,
            pct(outliers, residue_count),
        )
    )

    lines.append(
        "SUMMARY: {} residues ({:.2f}%) have severe CA geometry outliers. "
        "(<=0.5% expected)".format(
            ca_geom,
            pct(ca_geom, residue_count),
        )
    )

    lines.append(
        "SUMMARY: {} residues ({:.2f}%) are helix-like, "
        "{} residues ({:.2f}%) are beta-like".format(
            alpha_count,
            pct(alpha_count, residue_count),
            beta_count,
            pct(beta_count, residue_count),
        )
    )

    lines.append(
        "SUMMARY: {} residues ({:.2f}%) are correctable to helix, "
        "{} residues ({:.2f}%) are correctable to beta".format(
            correctable_helix,
            pct(correctable_helix, residue_count),
            correctable_beta,
            pct(correctable_beta, residue_count),
        )
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Path to PDB/mmCIF model file")
    parser.add_argument(
        "--out",
        help="Write report to this file (default: stdout)",
    )
    parser.add_argument(
        "--kinemage",
        help="Optional path to write a kinemage visualization file",
    )
    args = parser.parse_args()

    result, cablam_output = run_cablam(args.model)
    report = format_report(
        result,
        args.model,
        cablam_output,
    )

    if args.out:
        with open(args.out, "w") as fh:
            fh.write(report + "\n")
    else:
        sys.stdout.write(report + "\n")

    if args.kinemage and hasattr(result, "as_kinemage"):
        with open(args.kinemage, "w") as fh:
            fh.write(result.as_kinemage())


if __name__ == "__main__":
    main()
