"""EM model-map fit: result parsing and Z-scores.

The numbers these functions produce were checked against a run of CCP-EM's
``pipeliner.atomic_model_validation`` job (ccpem-pipeliner 1.6.1) on PDB 6nur:
FSCavg, SMOC outlier percentage, per-residue SMOC Z-scores and the default
contour all agreed. These tests pin the logic with small synthetic inputs.
"""

import pytest

from cstf.validate import em_map_fit as eb
from cstf.validate.orchestrator import _build_steps

FSC_DAT = """\
# FC from model.cif
     d_min      d_max  ncoeffs  power_FP_mask     power_FC  fsc_FC_full
 8.000000  20.000000       10   1.0   1.0     0.90
 4.000000   8.000000       30   1.0   1.0     0.70
 3.000000   4.000000       60   1.0   1.0     0.40
 2.000000   3.000000      100   1.0   1.0     0.10
"""


def test_fsc_averages_follow_ccpem_cutoffs(tmp_path):
    path = tmp_path / "masked_fsc.dat"
    path.write_text(FSC_DAT)
    shells = eb.read_servalcat_fsc(path)
    assert [s["ncoeffs"] for s in shells] == [10, 30, 60, 100]

    result = eb.fsc_averages(shells, resolution=3.1)
    # Shell midpoints 14, 6, 3.5, 2.5 A: up to 3.1 A keeps the first three.
    assert result["fsc_avg"] == pytest.approx((9 + 21 + 24) / 100)
    assert result["fsc_avg_all_shells"] == pytest.approx((9 + 21 + 24 + 10) / 200)
    # Highest-resolution shell with FSC >= 0.5 is the second one.
    assert result["fsc_avg_to_fsc_0_5"] == pytest.approx((9 + 21) / 40)


def test_smoc_zscores_use_neighbours_within_12_angstrom():
    positions = {("A", str(i)): (3.8 * i, 0.0, 0.0) for i in range(1, 5)}
    positions[("B", "1")] = (500.0, 0.0, 0.0)  # isolated: fewer than 3 neighbours
    smoc = {"A": {"1": 0.8, "2": 0.8, "3": 0.2, "4": 0.8}, "B": {"1": 0.1}}

    z = eb.smoc_zscores(smoc, positions)

    # Residue A3 sees all four A residues (itself included) within 12 A.
    values = [0.8, 0.8, 0.2, 0.8]
    mean = sum(values) / 4
    std = (sum((v - mean) ** 2 for v in values) / 4) ** 0.5
    assert z[("A", "3")] == pytest.approx((0.2 - mean) / std)
    assert z[("B", "1")] == 0.0
    summary = eb.smoc_summary(z)
    assert summary["n_smoc_residues"] == 5
    assert summary["smoc_outlier_percent"] == pytest.approx(0.0)  # -1.73 > -2.0


def test_read_tempy_scores(tmp_path):
    path = tmp_path / "globscores.csv"
    path.write_text("ccc,0.324\nmi_mask,0.016\noverlap,0.252\n")
    assert eb.read_tempy_scores(path) == {"ccc": 0.324, "mi_mask": 0.016, "overlap": 0.252}


def test_step_options_reach_the_step():
    steps = _build_steps(
        ["em_map_fit"], skip_existing=True, step_options={"em_map_fit": {"resolution": 3.5}}
    )
    assert steps["em_map_fit"].options["resolution"] == 3.5
    with pytest.raises(ValueError):
        _build_steps(["em_map_fit"], skip_existing=True, step_options={"nope": {}})
