from pathlib import Path
import gemmi
import pandas as pd

from cstf.update import utils

ALIGNMENT_FILENAME = "structure_sequence_alignment.txt"
ALIGNMENT_HEADER = (
    "This is the alignment of sequence in the pdb_file and the reference genome.\n"
    "For the alignment the python tool gemmi "
    "[https://gemmi.readthedocs.io/en/latest/index.html] was used.\n\n"
)


def sequence_alignment(
    df: pd.DataFrame,
    start: str,
    end: str,
    repo_path: str | Path,
    fasta_paths: list[str | Path],
) -> None:
    """
    Performs sequence alignment between PDB/CIF structures which need to have been downloaded and
    reference genomes which need to be provided.

    This function aligns the sequences of :class:`~cstf.update.config.CustomTypes.entry_id`
    against reference genomes, and writes alignment reports to text files.

    Two types of sequence comparisons are made:

    1. Chain-to-reference alignment:
    Individual protein chain sequences extracted from PDB structures are aligned
    against reference protein sequences provided in fasta files.

    2. Deposited-to-structure alignment:
    The full sequence derived from the deposited CIF file is aligned against the
    sequence reconstructed from the PDB structure.

    It handles multiple chains per protein and uses gemmi for sequence extraction and alignment.
    See :ref:`this section <usage-align>`.

    Args:
        df: Output from :func:`~cstf.update.query.get_df` with aggregate=True and columns
            "protein", "taxonomy", path_in_repo, and "relevant_chains"
            which can be made using :func:`~cstf.update.config.Presets.functions`.
        start: Start date (inclusive), ISO format: YYYY-MM-DD.
        end: End date (inclusive), ISO format: YYYY-MM-DD.
        repo_path: Root path to the repository containing structure files.
        fasta_paths: Path to the FASTA file containing reference protein sequences.
    Notes:
        - Creates or appends to "structure_sequence_alignment.txt" files in the structure directories (repo_path / pdb / protein / taxonomy)
        - First and last chains are anchored to their respective protein names.
        - Handles ambiguous middle chains by matching against all protein names.
        - Generates alignments for individual chains and overall structure sequences.
    """
    df = utils.get_current_df(df, start, end)
    fasta_sequences: list[(str, str)] = utils.get_protein_seq_from_fastas(fasta_paths)

    for _, group in df.groupby(["protein", "taxonomy"]):
        path = Path(repo_path, group.path_in_repo.iloc[0]).parent / ALIGNMENT_FILENAME
        if not path.exists():
            path.write_text(ALIGNMENT_HEADER)

        for entry_id, row in group.iterrows():
            _process_entry(entry_id, row, repo_path, fasta_sequences, path)


def _process_entry(
    entry_id: str, row: pd.Series, repo_path: Path, fasta_sequences: list, out: Path
):
    """Write alignment results for one entry_id."""
    base = Path(repo_path, row.path_in_repo, entry_id)
    pdb = gemmi.read_pdb(f"{base}.pdb").entities
    cif = gemmi.read_structure(f"{base}.cif").entities

    if not pdb:
        print(f"No sequences found for {entry_id}")
        return

    chain_idxs = _parse_chains(row.relevant_chains, len(pdb))
    chain_seqs = _extract_sequences(pdb, chain_idxs)
    protein_names = row.protein.split("-")
    _remove_rna_sequences(chain_idxs, chain_seqs, protein_names)

    candidates = _build_candidates(protein_names, len(chain_seqs))

    with open(out, "a") as doc:
        doc.write(f">>>{entry_id}:\n")

        for c, seq, cand in zip(chain_idxs, chain_seqs, candidates):
            best_result, best_ref_seq, best_name = _best_alignment(
                seq, cand, fasta_sequences
            )
            if best_result:
                label = chr(c + ord("A"))
                doc.write(f">Reference ({best_name}) vs chain {label}:\n")
                _write_seq_report(doc, best_result, best_ref_seq, seq)

        _write_structure_alignment(doc, pdb, cif)


def _remove_rna_sequences(
    chain_idxs: list[int], chain_seqs: list[str], protein_names: list[str]
):
    """Remove RNA chains (and their matching protein name) in-place."""
    try:  # No sequence alignment for rna sequences
        protein_names.remove("rna")
    except:
        ValueError
    for chain_idx, chain_seq in zip(chain_idxs, chain_seqs):
        if set(chain_seq).issubset({"A", "C", "G", "U", "I", "N"}):
            chain_idxs.remove(chain_idx)
            chain_seqs.remove(chain_seq)


def _parse_chains(chains: str, len_pdb: int) -> list[int]:
    """Convert a comma-separated chain string (e.g. "A, B, C") to 0-based
    integer indices. Falls back to the full entity range when the field is
    absent.
    """
    try:
        return [ord(c.strip()) - 65 for c in chains.split(",")]
    except AttributeError:
        return list(range(len_pdb))


def _build_candidates(protein_names: list[str], n_chains: int):
    """
    Map chain positions to candidate protein names for alignment.

    When the number of names matches the number of chains, each chain has a
    single candidate.  Otherwise the first and last chains are anchored to
    their respective names while every middle chain is matched against all
    names.
    """
    if len(protein_names) == n_chains:
        return [[name] for name in protein_names]
    if n_chains == 1:
        return [protein_names]
    return (
        [[protein_names[0]]] + [protein_names] * (n_chains - 2) + [[protein_names[-1]]]
    )


def _write_structure_alignment(doc, pdb: gemmi.EntityList, cif: gemmi.EntityList):
    pdb_seq = "".join(_extract_sequences(pdb, range(len(pdb))))
    cif_seq = "".join(_extract_sequences(cif, range(len(cif))))

    result = gemmi.align_string_sequences(list(cif_seq), list(pdb_seq), [])
    mismatches, gaps = _analyze_mismatches(result)

    doc.write(">Deposited vs structure:\n")
    _write_seq_report(doc, result, cif_seq, pdb_seq)
    doc.write(f"Mismatch in {mismatches}\nUnmodelled in {gaps}\n\n")


def _extract_sequences(entities, chain_idxs: list[int]) -> list[str]:
    """Return one-letter sequences for the specified chain indices."""

    def _entity_to_one_letter(entities, chain_idx: int) -> str:
        """Convert an entity's full sequence to one-letter codes, using X for unknowns."""
        sequence = entities[chain_idx].full_sequence
        letters = (
            gemmi.find_tabulated_residue(res).one_letter_code for res in sequence
        )
        return "".join(code if code.isupper() else "X" for code in letters)

    return [_entity_to_one_letter(entities, int(chain)) for chain in chain_idxs]


def _best_alignment(chain_seq: str, protein_names: list[str], fasta_sequences: list):
    """
    Find the highest-scoring alignment of chain_seq against the reference
    FASTA sequences for any of the given protein_names.

    Returns:
        (result, fasta_sequence, name) or (None, None, None)
        when no matching reference sequence exists.
    """
    best = (-float("inf"), None, None, None)

    for name in protein_names:
        for ref_seq in (v for k, v in fasta_sequences if k == name):
            result = gemmi.align_string_sequences(list(ref_seq), list(chain_seq), [])
            if result.score > best[0]:
                best = (result.score, result, ref_seq, name)

    return best[1:]


def _write_seq_report(doc, result, seq1: str, seq2: str) -> None:
    """Write identity score and formatted alignment to doc."""
    doc.write(
        f"Identity: {result.calculate_identity():.2f}\n"
        f"Score: {result.score:.2f}\n"
        f"{result.formatted(seq1, seq2)}\n"
    )


def _analyze_mismatches(result) -> tuple[list[int], list[int]]:
    """Parse the match string from an alignment result."""
    mismatches, gaps = [], []
    for i, letter in enumerate(result.match_string, start=1):
        if letter == ".":
            mismatches.append(i)
        elif letter != "|":
            gaps.append(i)
    return mismatches, gaps
