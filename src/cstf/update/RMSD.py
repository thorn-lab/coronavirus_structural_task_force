import seaborn as sb
from matplotlib import pyplot as plt
import numpy as np
import gemmi as gm
from pathlib import Path
import pandas as pd
import re

from cstf.update import utils


def calculate_rmsd(
    df: pd.DataFrame, start: str, end: str, repo_path: str | Path
) -> None:
    """
    Calculate RMSD (Root Mean Square Deviation) between new and old protein structures.
    This function compares protein structures from between the given dates against each other
    and against the other proteins in the dataframe, computing pairwise RMSD values for all chain combinations.
    Results are saved to a CSV file and a heatmap visualization is generated. See :ref:`this section <usage-rmsd>`.

    Args:
        df: Output from :func:`~cstf.update.query.get_df` with aggregate=True and columns "protein", "path_in_repo"
            and optionally relevant_chains, which can be made using :func:`~cstf.update.config.Presets.functions`.
        start: Start date (inclusive), ISO format: YYYY-MM-DD.
        end: End date (inclusive), ISO format: YYYY-MM-DD.
        repo_path: Path to the repository root directory containing structure files.
    Raises:
        KeyError: If required columns are missing from the DataFrame or polymer data.
        FileNotFoundError: If structure files are not found at the specified paths.
    Notes:
        - Compares each new protein structure against all old structures for the same protein.
        - Uses superposition calculation with CaP atoms for alignment.
        - Tracks the maximum RMSD and best chain pair for each comparison.
        - Results are saved as RMSD.csv in the protein's parent directory.
        - Generates a heatmap visualization of RMSD values.
    """

    new_df = utils.get_current_df(df, start, end)
    old_df = df.loc[list(set(df.index) - set(new_df.index)), :]
    for protein, new_df_protein in new_df.groupby("protein"):
        results_df_protein = pd.DataFrame(
            columns=[
                "PDB-1",
                "PDB-2",
                "Chain-1",
                "Chain-2",
                "RMSD",
                "Aligned_Atoms",
            ]
        )
        for id_1, row_1 in new_df_protein.iterrows():
            polymers_1 = _get_polymers(id_1, row_1, repo_path)
            for id_2, row_2 in old_df[old_df.protein == protein].iterrows():
                polymers_2 = _get_polymers(id_2, row_2, repo_path)
                max_rmsd = 0.0
                for chain_1, polymer_1 in polymers_1.items():
                    for chain_2, polymer_2 in polymers_2.items():
                        ptype = polymer_1.check_polymer_type()
                        sup = gm.calculate_superposition(
                            polymer_1, polymer_2, ptype, gm.SupSelect.CaP
                        )
                        rmsd = sup.rmsd
                        if rmsd >= max_rmsd:
                            max_rmsd, aligned_atoms = rmsd, sup.count
                            best_pair = (chain_1, chain_2)

                results_df_protein.loc[len(results_df_protein), :] = (
                    id_1,
                    id_2,
                    best_pair[0],
                    best_pair[1],
                    round(max_rmsd, 3),
                    aligned_atoms,
                )

            old_df.loc[id_1, :] = row_1

        folder_path = Path(repo_path, new_df_protein.loc[id_1, "path_in_repo"]).parents[
            1
        ]
        _save_file(results_df_protein, Path(folder_path, "RMSD.csv"))
        _heat_map(folder_path, protein)


def _get_polymers(id: str, row: pd.Series, repo_path: str | Path):
    """Extracts polymer chains from a PDB structure file.
    Args:
        id: The identifier of the PDB structure file (without extension).
        row: A data row containing 'path_in_repo' and 'relevant_chains' columns.
            - path_in_repo: Relative path to the structure file within the repository.
            - relevant_chains: Comma-separated list of chain identifiers (e.g., "A, B, C").
                If not available or AttributeError occurs, all chains in the structure are used.
        repo_path: The base path to the repository containing the structure files.
    Returns:
        dict: A dictionary mapping chain indices (int) to polymer objects.
            Keys are zero-based chain indices, values are polymer objects from BioPython.
            If a chain is missing, an error message is printed and the chain is skipped.
    """

    structure = gm.read_structure(f"{repo_path}/{row.path_in_repo}/{id}.pdb")[0]
    try:
        chains = [ord(chain) - 65 for chain in row.relevant_chains.split(", ")]
    except AttributeError:
        chains = range(len(structure))
    structure_by_chain = {}
    for chain in chains:
        try:
            structure_by_chain.update({chain: structure[chain].get_polymer()})
        except IndexError:
            print(f"error for {id}, no chain {chain}")
    return structure_by_chain


def _save_file(results_df_protein: pd.DataFrame, rmsd_path: str | Path) -> None:
    """Saves RMSD results to a CSV file.
    Creates a new CSV file with a header describing the RMSD data if it doesn't exist,
    then appends the protein RMSD results to the file.
    Args:
        results_df_protein (pandas.DataFrame): DataFrame containing RMSD values for protein chains.
            Each column represents a different metric or chain combination.
        rmsd_path (pathlib.Path): Path object pointing to the output CSV file where results
            will be saved or appended.
    """

    if not rmsd_path.exists():
        header = (
            f"This document contains the RMSD of the best combination of chains of entries in this folder \n\n"
            + ",".join(results_df_protein.columns)
            + "\n"
        )
        with open(rmsd_path, "w") as doc:
            doc.write(header)

    results_df_protein.to_csv(rmsd_path, header=None, mode="a", index=False)


def _heat_map(folder_path: str | Path, protein) -> None:
    """Generates and saves a heatmap visualization of RMSD values.
    Args:
        folder_path: The directory path containing the RMSD.csv file
            and where the heatmap.png output will be saved.
        protein: The name of the protein being analyzed. Used in the
            heatmap title to identify the protein structure comparisons.
    Notes:
        - heatmap is only generated if there are more than 1 RMSD values.
    """
    rmsd_path = Path(folder_path, "RMSD.csv")
    rmsd_df = pd.read_csv(rmsd_path, header=1)[["PDB-1", "PDB-2", "RMSD"]]
    if len(rmsd_df) > 1:
        hmap = _get_distance_matrix(rmsd_df)
        fig, ax = plt.subplots()
        sb.heatmap(
            hmap,
            cmap="viridis",
            cbar=True,
            cbar_kws={"label": "[Å]", "orientation": "vertical"},
            xticklabels=True,
            yticklabels=True,
        )
        ax.set_title(protein + " best RMSD")
        plt.savefig(Path(folder_path, "heatmap.png"), dpi=800)
        plt.close(fig)


def _get_distance_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Generates a symmetric distance matrix from RMSD data.
    Takes a DataFrame with pairwise RMSD values between PDB structures and creates
    a symmetric distance matrix by including both directions of each pair.
    Args:
        df: A DataFrame containing columns "PDB-1", "PDB-2", and "RMSD".
        Each row represents the RMSD distance between two PDB structures.
    Returns:
        pd.DataFrame: A pivot table with PDB-1 identifiers as index, PDB-2 identifiers
        as columns, and RMSD values as entries. The matrix is symmetric,
        including both directions of each pairwise comparison.
    """

    inv_df = df.copy().rename(columns={"PDB-1": "PDB-2", "PDB-2": "PDB-1"})
    full_rmsd_df = pd.concat([df, inv_df]).drop_duplicates()
    return full_rmsd_df.pivot(index="PDB-1", columns="PDB-2", values="RMSD")
