import pytest
import pandas as pd
from pathlib import Path
import random
from datetime import date, timedelta


@pytest.fixture(params=["SARS-CoV", "SARS-CoV-2"])
def taxonomy(request):
    """Parameter fixture: each test using `taxonomy` runs twice."""
    return request.param


@pytest.fixture(scope="session")
def reference_df():
    """Load both reference dataframes into a dict."""
    base = Path(__file__).parent / "test_data" / "dataframes"
    df1 = pd.read_pickle(base / "test_SARS-CoV-2.pkl")
    df2 = pd.read_pickle(base / "test_SARS-CoV.pkl")
    df1["taxonomy"] = "SARS-CoV-2"
    df2["taxonomy"] = "SARS-CoV"

    for df in (df1, df2):
        df.rename(columns={"last_revision": "last_revised"}, inplace=True)
    dfs = {
        "SARS-CoV-2": df1,
        "SARS-CoV": df2,
    }

    return dfs


@pytest.fixture
def random_date_range():
    """Generate a reproducible date range inside 17.3.2021–1.3.2023."""
    random.seed(44)
    start = date.fromisoformat("2021-03-17")
    end = date.fromisoformat("2023-03-01")
    first_day = start + timedelta(random.randint(0, (end - start).days))
    last_day = first_day + timedelta(random.randint(0, (end - first_day).days))
    print(first_day, last_day)
    return first_day, last_day


@pytest.fixture
def historical_path():
    return Path(__file__).parents[1] / "utils/update_pipeline/weekly_reports"
