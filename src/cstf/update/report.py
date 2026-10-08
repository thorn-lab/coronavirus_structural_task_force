from pathlib import Path
from itertools import groupby
import pandas as pd
import numpy as np
from .utils import get_time


def write_reports(
    df: pd.DataFrame, start: str, end: str, repo_path: str | Path
) -> None:
    """Generates weekly reports in the date range and a report summarising the full period which is
    overwritten the next time the function is called.

    Each report lists newly released and revised structures, with new structures additionally grouped by protein.
    Structure files do not need to be downloaded to use this function. See :ref:`this section <usage-report>`.

    Args:
        df: Output from :func:`~cstf.update.query.get_df` with aggregate=True.
        start: Start date (inclusive), ISO format: YYYY-MM-DD.
        end: End date (inclusive), ISO format: YYYY-MM-DD.
        repo_path: Reports are written to folder called "weekly_reports" in this directory.
    """
    repo_path = Path(repo_path)
    reports_path = repo_path / "weekly_reports"
    reports_path.mkdir(parents=True, exist_ok=True)

    # We start on the Wednesday after the first date
    start_dt = get_time(start, next_week=True)
    # We end on the Wednesday before the second date.
    end_dt = get_time(end)

    # Latest report
    report_path = reports_path / f"latest_update_report.txt"
    _write_single_report(df, start_dt, end_dt, report_path, latest_report=True)

    dates = pd.date_range(
        start_dt, end_dt, periods=(end_dt - start_dt).days // 7 + 1
    ).date

    for day in dates:
        df_date = df[(df.release_date == day) | (df.last_revised == day)]
        report_path = reports_path / f"{day}_update_report.txt"
        _write_single_report(df_date, day, day, report_path)


def _write_single_report(
    new_df: pd.DataFrame,
    start,
    end,
    report_path: Path,
    latest_report: bool = False,
) -> None:
    """Write a single report file containing newly released and revised structures.

    Generates a formatted text report that lists revised structures, new structures,
    and new structures grouped by protein type. The report is written to the specified file path.
    Args:
        start, end: Must be date objects and Wednesdays!
        taxonomy: Taxonomy identifier for report header.
        report_path: File path where the report will be written.
        df: DataFrame containing ids that will be written into the report, no matter their release dates.
        latest_report: If True, formats header as "start until end" for latest report.
            If False, formats header as "end weekly" for weekly reports. Defaults to False.
    """

    date_header = f"{start} until {end}" if latest_report else f"{end} weekly"
    with report_path.open("a") as doc:
        doc.write(f"{date_header} report \n\n")

    for taxonomy, taxonomy_df in new_df.groupby("taxonomy"):

        new_ids = set(taxonomy_df[taxonomy_df.release_date.between(start, end)].index)
        revised_ids = (
            set(taxonomy_df[taxonomy_df.last_revised.between(start, end)].index)
            - new_ids
        )

        with report_path.open("a") as doc:
            doc.write(f"{taxonomy}:\n")
            doc.write(f"##### {len(revised_ids)} revised structures #####\n")
            doc.write(", ".join(sorted(revised_ids)) + "\n\n")
            doc.write(f"##### {len(new_ids)} new structures #####\n")
            doc.write(", ".join(sorted(new_ids)) + "\n\n")
            doc.write("##### new structures by protein #####")
            for protein, ids in groupby(
                new_ids, key=lambda k: new_df.loc[k, "protein"]
            ):
                doc.write(f"\n{protein}\n>" + " ".join(ids))
            doc.write("\n\n\n")
