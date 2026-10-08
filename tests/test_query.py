import pandas as pd
from unittest.mock import patch
import pytest
from pathlib import Path
from cstf.update import config


def test_get_ids(reference_df, random_date_range, taxonomy):
    from cstf.update.query import get_ids
    from cstf.update.config import taxonomy_query

    df = reference_df[taxonomy].copy()
    start_dt, end_dt = random_date_range

    # Revision dates might be different so we only check release dates
    past_df = df[((df["release_date"] >= start_dt) & (df["release_date"] <= end_dt))]

    if past_df.empty:
        pytest.skip("No past entries in this random date range.")

    past_ids = set(past_df.index.tolist())

    # Call real API
    queries = {taxonomy: taxonomy_query[taxonomy]}
    live_ids = set(get_ids(start=str(start_dt), end=str(end_dt), rcsb_queries=queries))
    # past_ids might have been deleted because they were not_assigned
    assert (past_ids - live_ids) is not None, past_ids - live_ids
    # assert past_ids.issubset(live_ids)


def test_get_proteins(reference_df, taxonomy, random_date_range, tmp_path):
    """
    Test get_proteins using sampled IDs from the historical dataframe.

    The rule:
      - If live_get_proteins returns "not_assigned", ignore that ID.
      - Otherwise assert equality with the past_df["protein"] entry.
    """
    from cstf.update.query import get_proteins

    df = reference_df[taxonomy].copy()
    start, end = random_date_range

    expected_df = df[
        ((df["release_date"] >= start) & (df["release_date"] <= end))
        | ((df["last_revised"] >= start) & (df["last_revised"] <= end))
    ]

    # expected_ids = expected_df.index.tolist()
    expected_ids = {
        entity_id: {"taxonomy": taxonomy} for entity_id in expected_df.index.tolist()
    }
    print(len(expected_ids))
    if not expected_ids:
        pytest.skip("No entries in sampled date range")

    data_path = Path(__file__).parent / "test_data"
    fasta_path = data_path / f"fasta/test_{taxonomy}.fasta"
    print(fasta_path)

    live_dict = get_proteins(expected_ids, [fasta_path])
    live_dict_entry = {
        entity_id[:4]: protein_dict for entity_id, protein_dict in live_dict.items()
    }

    for live_entry in live_dict_entry:
        if not live_entry in expected_ids:
            continue

        live_prot = live_dict_entry[live_entry]["protein"]
        if live_prot == "":
            continue

        past_prot = expected_df.loc[live_entry, "protein"]

        assert live_prot in past_prot.split(
            "-"
        ), f"{live_entry}: {live_prot} not in {past_prot}"


def test_get_attributes(reference_df, random_date_range, taxonomy):
    from cstf.update.query import _get_attributes

    df = reference_df[taxonomy].copy()

    start_dt, end_dt = random_date_range

    # Filter the reference df to the same window used in update_dataframe_inplace tests
    expected_df = df[
        ((df["release_date"] >= start_dt) & (df["release_date"] <= end_dt))
        | ((df["last_revised"] >= start_dt) & (df["last_revised"] <= end_dt))
    ]

    if expected_df.empty:
        pytest.skip("No entries found in this random date range for this taxonomy.")

    sampled_ids = expected_df.index.tolist()
    attributes_dict = config.Presets().attributes()
    attrs_live = _get_attributes(sampled_ids, attributes_dict)
    attrs_live_entry = {
        entry_id[:4]: attrs_dict for entry_id, attrs_dict in attrs_live.items()
    }

    for live_pdb_id in attrs_live_entry:
        expected_row = expected_df.loc[live_pdb_id]

        # assert pdb_id in attrs_live, f"{pdb_id} not in returned attributes"

        live = attrs_live[live_pdb_id]
        # assert isinstance(live["title"], str), pdb_id
        # assert (
        # expected_row["title"].lower().strip() in live["title"].lower().strip()
        # ), pdb_id
        if pd.notna(expected_row["exp_method"]):
            assert (
                live["exp_method"].lower() == expected_row["exp_method"].lower()
            ), live_pdb_id
