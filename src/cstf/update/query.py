"""Utilities for querying PDB structural data, specifically to

- Retrieve PDB polymer entity IDs released or revised within a given date range
  using RCSB search queries.
- Assign protein names to PDB entities via sequence similarity searches against
  reference fasta files.
- Create or update a pandas DataFrame containing PDB metadata, optionally
  merging with an existing dataset.
"""

import pandas as pd
import numpy as np
from typing import Iterable, Callable, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
from rcsbapi.search import search_attributes as attrs
from rcsbapi.search import SeqSimilarityQuery, SeqMotifQuery
from rcsbapi.search.search_query import AttributeQuery
from rcsbapi.data import DataQuery
from cstf.update.config import CustomTypes as ct
from .utils import (
    get_protein_seq_from_fastas,
    retry_with_backoff,
    retrieve_nested_attribute,
)


def get_ids(
    start: str, end: str, rcsb_queries: dict[str, AttributeQuery]
) -> dict[ct.entity_id, dict[str, str]]:
    """Retrieve PDB polymer entity IDs released or revised within a date range.

    For each supplied RCSB query this function finds polymer entities
    whose initial release date or most recent revision date falls within the specified interval.
    See :ref:`this section <usage-get-ids>`.

    Args:
        start: Start date (inclusive), ISO format: YYYY-MM-DD.
        end: End date (inclusive), ISO format: YYYY-MM-DD.
        rcsb_queries: Mapping of taxonomy name to
            :class:`~rcsbapi.search.search_query.AttributeQuery`.

            See :meth:`~cstf.update.config.Presets.queries` for example queries.

            For information on how to construct queries see:
            `RCSB Query Construction <https://rcsbapi.readthedocs.io/en/latest/search_api/query_construction.html>`_


    Returns:
        Dictionary mapping lowercase polymer entity IDs to a taxonomy string.
        If an entity matches multiple taxonomies, they are joined using "__".
    """
    # Track which taxonomies each entity ID matches
    ids_by_taxonomy = {}
    for taxonomy, rcsb_query in rcsb_queries.items():
        revised_query = (start <= attrs.rcsb_accession_info.revision_date) & (
            attrs.rcsb_accession_info.revision_date <= end
        )
        release_query = (start <= attrs.rcsb_accession_info.initial_release_date) & (
            attrs.rcsb_accession_info.initial_release_date <= end
        )
        query = rcsb_query & (revised_query | release_query)
        ids = {entity.lower() for entity in query("polymer_entity")}
        for id in ids:
            ids_by_taxonomy.setdefault(id, set()).add(taxonomy)
    return {
        id: {"taxonomy": "__".join(sorted(taxonomy))}
        for id, taxonomy in ids_by_taxonomy.items()
    }


def _get_attributes(
    ids: Iterable[ct.entity_id], attributes_to_fetch: dict[str, DataQuery]
):
    """Fetch metadata for PDB polymer entities using rcsbapi.data.

    This helper executes a bulk DataQuery and flattens nested JSON responses
    into a dictionary suitable for DataFrame construction.

    Args:
        ids: Iterable of polymer entity IDs (e.g. from get_ids).
        attributes_to_fetch: Mapping of output column name to RCSB schema path.
            These attributes must works as input_type for :class:`rcsbapi.data.DataQuery`
            Available paths for a given 'string' can be explored via::

                from rcsbapi.data import DataSchema
                DataSchema().find_field_names('string')

    Returns:
        Dictionary keyed by lowercase polymer entity ID, where each value is
        a dictionary of fetched attributes. Can be converted to a DataFrame via::

            pd.DataFrame.from_dict(result, orient="index")
    """
    query = DataQuery(
        input_type="polymer_entities",
        input_ids=list(ids),
        return_data_list=list(attributes_to_fetch.values()),
    )
    query.exec()

    # Extract and structure the response data
    raw_entries = query.get_response()["data"]["polymer_entities"]

    return {
        entry["rcsb_id"].lower(): {
            attr_name: retrieve_nested_attribute(entry, path)
            for attr_name, path in attributes_to_fetch.items()
        }
        for entry in raw_entries
    }


def get_proteins(
    ids_by_taxonomy: dict[ct.entity_id, dict[str, str]],
    fasta_paths: list[str | Path],
    workers: int = 10,
) -> dict[ct.entity_id, dict[str, str]]:
    """
    Assign protein names to PDB polymer entities using sequence similarity search.

    Protein sequences from the provided FASTA files are queried against RCSB using
    sequence similarity (or motif search for short sequences). Entities matching
    a reference sequence are assigned the corresponding protein name.

    For entities that remain unassigned: Non-protein polymers are labeled by their polymer type (e.g. "rna", "dna").
    Protein entities are compared via entity-to-entity similarity, and assigned the protein with the highest overlap to reference hits.
    See :ref:`this section <usage-get-proteins>`.



    Args:
        ids_by_taxonomy: Output from :func:`get_ids`
        fasta_path: Paths to FASTA files containing reference protein sequences.
        workers: Maximum number of threads for concurrent RCSB queries.

    Returns:
        Dictionary mapping polymer entity ID to a dictionary with:
        - "taxonomy": taxonomy label(s)
        - "protein": assigned protein name (empty string if unresolved)
    """

    # Parse FASTA sequences
    protein_sequences = get_protein_seq_from_fastas(fasta_paths)

    @retry_with_backoff
    def run_rcsb_query(query) -> set[str]:
        """
        Execute an RCSB sequence query with retry and exponential backoff.
        """
        results = query("polymer_entity")
        return set(results)
        # return {id.lower() for id in results}

    # Sequence search function
    def search_seq(
        item: tuple[str, str], id_query: AttributeQuery
    ) -> tuple[str, set[str]]:
        protein_name, seq = item
        if not seq:
            return protein_name, set()

        try:
            # Define sequence query based on length
            if len(seq) >= 25:
                seq_query = SeqSimilarityQuery(
                    value=seq,
                    evalue_cutoff=1,
                    sequence_type="protein",
                )
            else:
                seq_query = SeqMotifQuery(value=seq)

            # Combine queries using bitwise AND (&)
            combined_query = seq_query & id_query

            # Execute query (specifying polymer_entity return type)
            hits = run_rcsb_query(combined_query)
            # hits = set(combined_query("polymer_entity"))
            return protein_name, hits

        except Exception as e:
            print(f"[ERROR] {protein_name}: query failed: {e}")
            return protein_name, set()

    def run_concurrent_tasks(
        items: Iterable, id_query: AttributeQuery, desc: str
    ) -> dict[str, set[str]]:
        results: dict[str, set[str]] = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(search_seq, item, id_query): item[0] for item in items
            }
            for key, hits in tqdm(
                (future.result() for future in as_completed(futures)),
                total=len(futures),
                desc=desc,
            ):
                results.setdefault(key, set()).update(hits)

        return results

    # Run sequence similarity searches for all reference proteins
    id_query = AttributeQuery(
        attribute="rcsb_polymer_entity_container_identifiers.rcsb_id",
        operator="in",
        value=list(ids_by_taxonomy),
    )

    protein_hits = run_concurrent_tasks(
        protein_sequences, id_query, "Sequence similarity search"
    )

    # Initialize protein assignments (empty string = unassigned)
    ids_by_protein = {id: "" for id in ids_by_taxonomy}
    for id in ids_by_protein:
        for protein_name, hits in protein_hits.items():
            if id in hits:
                ids_by_protein[id] = protein_name

    # Handle unassigned entities
    not_assigned_ids = {id for id, name in ids_by_protein.items() if not name}
    if not_assigned_ids:
        attributes_to_fetch = {
            "polymer_type": "entity_poly.rcsb_entity_polymer_type",
            "seq": "entity_poly.pdbx_seq_one_letter_code_can",
        }
        attributes = _get_attributes(not_assigned_ids, attributes_to_fetch)
        not_assigned_polymer_types = {
            id: d["polymer_type"].lower() for id, d in attributes.items()
        }
        not_assigned_sequences = {id: d["seq"] for id, d in attributes.items()}
        # Assign non-protein polymer types directly
        for id, polymer_type in not_assigned_polymer_types.items():
            if polymer_type != "protein" and id in ids_by_protein:
                ids_by_protein[id] = polymer_type
                not_assigned_sequences.pop(id)

        entity_hits = run_concurrent_tasks(
            list(not_assigned_sequences.items()),
            id_query,
            "Entity similarity search",
        )
        max_proportion = {id: 0 for id in not_assigned_ids}
        for id, similar_ids in entity_hits.items():
            for protein_name, reference_ids in protein_hits.items():
                if similar_ids:
                    proportion = len(similar_ids.intersection(reference_ids)) / len(
                        similar_ids
                    )
                    if proportion > max_proportion[id]:
                        max_proportion[id] = proportion
                        ids_by_protein[id] = protein_name

    return {
        id: {
            **ids_by_taxonomy[id],
            "protein": ids_by_protein[id],
        }
        for id in ids_by_taxonomy
    }


def get_df(
    proteins_and_taxonomy: dict[str, dict],
    rcsb_data_attributes: dict[str, str] | None = None,
    functions_to_combine_columns: dict[str, Callable[[pd.Series], Any]] | None = None,
    old_df: pd.DataFrame | None = None,
    aggregate: bool = True,
) -> pd.DataFrame:
    """
    Build or update a DataFrame containing PDB metadata and protein annotations.

    This function fetches RCSB metadata for polymer entities, merges it with
    taxonomy and protein assignments, and optionally aggregates multiple
    entities belonging to the same PDB entry. See :ref:`this section <usage-get-df>`.

    Args:
        proteins_and_taxonomy: Output from :func:`get_ids` or :func:`get_proteins`.
        rcsb_data_attributes: Optional mapping of additional RCSB data attributes
            to fetch. These attributes must works as input_type for :class:`~rcsbapi.data.DataQuery`.
            Available paths for a given 'string' can be explored via::

                from rcsbapi.data import DataSchema
                schema = DataSchema()
                schema.find_paths("polymer_entities", "string")

            See :meth:`~cstf.update.config.Presets.attributes` for example data attributes.
            If omitted, only release and revision dates are included.
        functions_to_combine_columns: Optional mapping of column specifications
            to transformation functions. Each transformation function must be valid
            input to :meth:`~pandas.DataFrame.apply` with axis=1.
            Keys may encode source columns using
            the format "new_col=col1+col2" where col1 and col2 would be dropped.
            See :meth:`~cstf.update.config.Presets.functions` for example functions.
        old_df: Existing DataFrame to merge with. Existing values take precedence.
        aggregate: Whether to aggregate polymer entities per PDB entry.

    Returns:
        A pandas DataFrame containing PDB metadata and any derived columns.
    """
    if not proteins_and_taxonomy:
        return pd.DataFrame()

    # Define default attributes with any custom overrides
    attributes_to_fetch = {
        "entry": "entry.entry.id",
        "release_date": "entry.rcsb_accession_info.initial_release_date",
        "last_revised": "entry.rcsb_accession_info.revision_date",
        **(rcsb_data_attributes or {}),
    }

    extracted_attributes = _get_attributes(
        proteins_and_taxonomy.keys(), attributes_to_fetch
    )

    # Combine input data with fetched attributes
    df = pd.concat(
        [
            pd.DataFrame.from_dict(proteins_and_taxonomy, orient="index"),
            pd.DataFrame.from_dict(extracted_attributes, orient="index"),
        ],
        axis=1,
    )

    df["entry"] = df["entry"].str.lower()
    df.sort_index(inplace=True)

    # not_date_cols = df.columns.difference(["release_date", "last_revised"])
    # df[not_date_cols] = df[not_date_cols].replace({"-": "_"}, regex=True)

    # Optionally aggregate multiple entities per entry
    if aggregate:

        def aggregate_values(series):
            """Combine multiple values, removing duplicates"""
            unique_values = {}
            for value in series:
                if not value:
                    continue
                for v in value.split("__"):
                    unique_values[v] = None  # keeps insertion order
            return "-".join(unique_values)
            # return "-".join(
            #     dict.fromkeys(v for value in series if value for v in value.split("__"))
            # )

        df = df.groupby("entry", as_index=True).agg(aggregate_values)
    else:
        df.replace({"__": "-"}, regex=True, inplace=True)

    # Convert numeric columns to appropriate types
    for column in df.columns:
        try:
            df[column] = pd.to_numeric(df[column], downcast="integer")
        except (ValueError, TypeError):
            pass  # Keep as string if conversion fails

    # Convert date columns to datetime
    for date_column in ("release_date", "last_revised"):
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce").dt.date

    # Apply custom column transformations
    for column_spec, transform_func in (functions_to_combine_columns or {}).items():
        # Parse "new_column = old_col1 + old_col2" format
        new_column_name, *source_columns = column_spec.split("=")
        df[new_column_name.strip()] = df.apply(transform_func, axis=1)

        # Drop source columns if specified
        if source_columns:
            columns_to_drop = [col.strip() for col in source_columns[0].split("+")]
            df.drop(columns=columns_to_drop, inplace=True)

    # Replace empty strings with NaN
    df.replace("", float("nan"), inplace=True)

    # Merge with existing DataFrame if provided
    if old_df is not None:
        df = df.combine_first(old_df)

    return df
