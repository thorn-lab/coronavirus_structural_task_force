import re
from pathlib import Path
import pandas as pd
import pytest


def parse_report(path: Path):
    """
    Parse a weekly report into structured sections:
    - revised: list[str]
    - new: list[str]
    - by_protein: dict[str, list[str]]
    """
    text = path.read_text().strip().splitlines()

    revised = []
    new = []
    by_protein = {}

    section = None
    current_protein = None

    for line in text:
        line = line.strip()

        if line.startswith("##### ") and "revised structures" in line:
            section = "revised"
            continue

        if (
            line.startswith("##### ")
            and "new structures" in line
            and "by protein" not in line
        ):
            section = "new"
            continue

        if line.startswith("##### new structures by protein"):
            section = "by_protein"
            continue

        # Parse revised/new lists
        if section in ("revised", "new") and line:
            ids = [x.strip() for x in line.split(",") if x.strip()]
            if ids:
                if section == "revised":
                    revised.extend(ids)
                else:
                    new.extend(ids)
            continue

        # Parse by-protein grouping
        if section == "by_protein":
            if not line:
                continue

            # protein name line
            if not line.startswith(">"):
                current_protein = line
                by_protein[current_protein] = []
                continue

            if current_protein:
                ids = re.split(r"\s+", line[1:].strip())
                ids = [x for x in ids if x]
                by_protein[current_protein].extend(ids)

    return {
        "revised": set(revised),
        "new": set(new),
        "by_protein": {k: set(v) for k, v in by_protein.items()},
    }


@pytest.mark.usefixtures("taxonomy")
def test_write_reports_matches_historical(
    taxonomy,
    reference_df,
    random_date_range,
    historical_path,
    tmp_path,
):
    """
    For all effective dates in the random date range:
    - Generate new reports using refactored write_reports() into tmp_path.
    - Load corresponding historical reports.
    - Compare: new IDs, by-protein groups.
    """
    from cstf.update.report import write_reports
    from cstf.update.utils import get_time

    df_subset = reference_df[taxonomy].copy()

    start, end = random_date_range

    # limit df to the date range, not strictly necesssary
    # df_subset = df[
    # df.release_date.between(start, end) | df.last_revision.between(start, end)
    # ]

    # generate new reports with the refactored code
    test_repo = tmp_path / "test_data"
    test_repo.mkdir()

    write_reports(df_subset, str(start), str(end), test_repo)

    # temporary weekly_reporst output directory
    tmp_reports = test_repo / "weekly_reports"

    start_dt = get_time(str(start), next_week=True)
    end_dt = get_time(str(end))
    dates = pd.date_range(
        start_dt, end_dt, periods=(end_dt - start_dt).days // 7 + 1
    ).date
    for day in dates:

        # historical file path
        historical_file = Path(historical_path) / Path(
            f"{day}_update_report_{taxonomy}.txt"
        )
        if not historical_file.exists():
            # Historical coverage may be incomplete; skip gracefully
            # pytest.skip(f"No historical report for {historical_file}")
            continue

        new_file = tmp_reports / f"{day}_update_report.txt"
        assert new_file.exists(), f"Missing generated report {new_file}"

        hist_struct = parse_report(historical_file)
        new_struct = parse_report(new_file)

        if "not_assigned" in hist_struct["by_protein"]:
            continue

        # Compare by-protein groups
        for protein, ids in new_struct["by_protein"].items():
            if (protein == "orf9b") or (protein == "protein_e"):
                continue
            assert not (ids - hist_struct["by_protein"][protein]), (
                f"Mismatch in by-protein section for {day} ({taxonomy} {protein}"
                f"{(ids - hist_struct['by_protein'][protein])}\n"
            )

        #  Compare new IDs
        assert not (new_struct["new"] - (hist_struct["new"])), (
            f"Mismatch in new IDs for {day} ({taxonomy})\n"
            f"historical={hist_struct['new']}\n"
            f"new={new_struct['new']}"
        )
