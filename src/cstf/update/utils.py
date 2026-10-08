"""Utility functions for updating packages in the coronavirus structural task force project."""

import asyncio
from datetime import date, timedelta
import json
from pathlib import Path
import functools
import pandas as pd
import re
from Bio import SeqIO

import time
import random
import functools
from typing import Callable, Any
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor


def get_current_df(df: pd.DataFrame, start: str, end: str):
    """Given a dataframe return only columns where release date or revision date
    fall between start and end dates."""
    try:
        start, end = date.fromisoformat(start), date.fromisoformat(end)
    except:
        TypeError
    released_mask = (start <= df.release_date) & (df.release_date <= end)
    revised_mask = (start <= df.last_revised) & (df.last_revised <= end)
    return df[released_mask | revised_mask]


def get_protein_seq_from_single_fasta(fasta_path: Path | str) -> list[tuple[str, str]]:
    """Get list of tuples of protein names and sequences."""
    # List to accomodate multiple sequences for one protein
    protein_sequences: list[tuple[str, str]] = []
    for protein in SeqIO.parse(fasta_path, "fasta"):
        if "OS" in protein.description:
            protein_name = protein.description[
                protein.description.find(" ") : protein.description.find("OS")
            ].strip()
        else:
            protein_name = protein.description.split(" ")[1]
            brackets = re.search(r"\((.*?)\)", protein_name)
            if brackets:
                protein_name = brackets.group(1)
        protein_name = protein_name.replace("-", "_").replace(" ", "_")
        protein_sequences.append((protein_name, str(protein.seq)))

    return protein_sequences


def get_protein_seq_from_fastas(fasta_paths: list[Path | str]):
    """Combine fasta files into one list of tuples of protein names and sequences."""
    names = []
    sequences = []
    for fasta_path in fasta_paths:
        for name, sequence in get_protein_seq_from_single_fasta(fasta_path):
            if sequence not in sequences:
                names.append(name)
                sequences.append(sequence)
    protein_sequences = [(name, sequence) for name, sequence in zip(names, sequences)]
    return protein_sequences


def retry_with_backoff(func):
    """
    Retry decorator with exponential backoff designed for heavy RCSB queries.
    """
    MAX_RETRIES = 3  # Increased from 3
    BASE_DELAY = 1.0  # Increased from 1.0 (gives server time to cool off)
    JITTER = 2.0  # Increased jitter to un-sync concurrent threads

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == MAX_RETRIES:
                    print(f"[ERROR] failed after {MAX_RETRIES} attempts: {e}")
                    raise

                delay = BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, JITTER)

                print(
                    f"[WARN] attempt {attempt} failed ({e}); "
                    f"retrying in {delay:.2f}s..."
                )

                time.sleep(delay)

    return wrapper


def async_wrapper(func):
    """wrapper for async functions"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def retrieve_nested_attribute(data, rcsb_data_path: str) -> str:
    """
    Extract values from nested data structures following a dot-notation path.

    Args:
        data: The data structure to search (dict or list)
        rcsb_data_path: Dot-separated path (e.g., "entry.rcsb_accession_info.date")

    Returns:
        String of unique values joined by "__", or empty string if none found
    """
    # Remove "polymer_entities" from path segments
    path_segments = [s for s in rcsb_data_path.split(".") if s != "polymer_entities"]
    found_values = set()

    def traverse(current_obj, remaining_segments):
        """Recursively walk through nested data structure."""
        if not remaining_segments or current_obj is None:
            return

        current_key = remaining_segments[0]
        remaining = remaining_segments[1:]

        # Handle lists by recursively checking each item
        if isinstance(current_obj, list):
            for item in current_obj:
                traverse(item, remaining_segments)

        # Handle dictionaries
        elif isinstance(current_obj, dict):
            value = current_obj.get(current_key)

            # If we've reached the end of the path, collect the value
            if not remaining and value:
                # Extract first item from lists
                if isinstance(value, list):
                    value = value[0]
                found_values.add(str(value))
            else:
                # Continue traversing deeper
                traverse(value, remaining)

    traverse(data, path_segments)
    return "_".join(sorted(found_values))


def get_time(day: str = None, next_week: bool = False) -> date:
    """Get the date of the most recent Wednesday, or optionally the Wednesday of the next week.

    If the passed in day is a Wednesday it returns it.

    Args:
        day (optional): ISO format date string (YYYY-MM-DD). Defaults to today's date if not provided.
        next_week (optional): If True, returns the Wednesday of the following week instead of the current week.
                              Defaults to False.
    Returns:
        date: A date object representing Wednesday of the specified week.
        If the input day is already a Wednesday, returns that day
        (or next week's Wednesday if next_week is True).
    Examples:
        >>> get_time("2024-01-10")  # Returns Wednesday of that week
        >>> get_time(next_week=True)  # Returns next week's Wednesday
    """

    day = date.fromisoformat(day) if day else date.today()
    offset = (day.weekday() - 2) % 7  # Wednesday = 2
    if offset == 0:
        return day
    return day - timedelta(offset) + next_week * timedelta(7)


def reset_index(df: pd.DataFrame) -> pd.DataFrame:
    """Used in tcp_manual, tcp_scan_results and analyse_and_fix_dataframe
    while transitioning to having the dataframe be indexed by pdb_ids.

    Args:
        df: Usually read from data/dataframes

    Returns:
        The same dataframe with index reset to integers.
    """
    if df.index.name == "pdb_id":
        return df.reset_index()
    return df
