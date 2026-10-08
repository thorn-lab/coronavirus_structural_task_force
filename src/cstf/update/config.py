from rcsbapi.search import search_attributes as attrs
from rcsbapi.search.search_query import AttributeQuery
import pandas as pd

from typing import Callable, Any


# Type hints
class CustomTypes:
    """Classes created purely for documentation purposes."""

    class entry_id(str):
        """A lowercase rcsb entry id, e.g. 6lks"""

        pass

    class entity_id(str):
        """A lowercase rcsb entity id, e.g. 6lks_1"""

        pass

    pass


class Presets:
    """These are rcsb queries, data attributes and dataframe functions that were
    used by the cstf. Example usage::

        preset = config.Presets()
        queries = preset.queries('H1N1', 'H3N2')
        attributes = preset.attributes('resolution', 'title')
        functions = preset.functions('path_in_repo', 'exp_method')

    If you provide no argument the entire dictionary is returned"""

    def __init__(self):
        self.taxonomy_query = taxonomy_query
        self.rcsb_data_attributes = rcsb_data_attributes
        self.functions_to_combine_columns = functions_to_combine_columns

    def queries(self, *names):
        """Can be used as input to :func:`~cstf.update.query.get_ids`.
        Available queries are SARS-CoV, SARS-CoV-2, H1N1, H3N2, H5N1, H5N8."""
        if not names:
            return self.taxonomy_query
        return {k: self.taxonomy_query[k] for k in names}

    def attributes(self, *names):
        """Can be used as input to :func:`~cstf.update.query.get_df`.
        Available attributes are version_1, version_2, exp_method,
        resolution, title, gene_1, gene_2, common_names, scientific_name, relevant_chains.
        """
        if not names:
            return self.rcsb_data_attributes
        return {k: self.rcsb_data_attributes[k] for k in names}

    def functions(self, *names):
        """Can be used as input to :func:`~cstf.update.query.get_df`.
        Can be used to combine attributes. For example version=version_1+version_2
        would combine major version 3 and minor version 4 into version 3.4 and drop the
        columns version_1 and version_2.
        Available functions to combine columns are version=version_1+version_2,
        gene, gene=gene_1+gene_2, path_in_repo, exp_method, superseded_by, relevant_chains
        """
        if not names:
            return self.functions_to_combine_columns
        return {k: self.functions_to_combine_columns[k] for k in names}


taxonomy_query: dict[str, AttributeQuery] = {
    "SARS-CoV": (
        attrs.rcsb_entity_source_organism.taxonomy_lineage.name
        == "Severe acute respiratory syndrome-related coronavirus"
    )
    & (
        attrs.rcsb_entity_source_organism.taxonomy_lineage.name
        != "Severe acute respiratory syndrome coronavirus 2"
    ),
    "SARS-CoV-2": (
        attrs.rcsb_entity_source_organism.taxonomy_lineage.name
        == "Severe acute respiratory syndrome coronavirus 2"
    )
    & (attrs.rcsb_entity_source_organism.taxonomy_lineage.name != "Octopus"),
    "H1N1": (attrs.rcsb_entity_source_organism.taxonomy_lineage.name == "H1N1"),
    "H3N2": (attrs.rcsb_entity_source_organism.taxonomy_lineage.name == "H3N2"),
    "H5N1": (attrs.rcsb_entity_source_organism.taxonomy_lineage.name == "H5N1"),
    "H5N8": (attrs.rcsb_entity_source_organism.taxonomy_lineage.name == "H5N8"),
}


rcsb_data_attributes: dict[str, str] = {
    "version_1": "entry.rcsb_accession_info.major_revision",
    "version_2": "entry.rcsb_accession_info.minor_revision",
    "exp_method": "entry.exptl.method",
    "resolution": "entry.rcsb_entry_info.resolution_combined",
    "title": "entry.struct.title",
    "gene_1": "uniprots.rcsb_uniprot_protein.gene.name.value",
    "gene_2": "rcsb_entity_source_organism.rcsb_gene_name.value",
    "common_names": "rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",
    "scientific_name": "polymer_entities.rcsb_entity_source_organism.scientific_name",
    "relevant_chains": "rcsb_id",
    # "author_chains": "polymer_entity_instances.rcsb_polymer_entity_instance_container_identifiers.auth_asym_id",
}


functions_to_combine_columns: dict[str, Callable[[pd.Series], Any]] = {
    "version=version_1+version_2": lambda x: float(
        f"{str(x.version_1)}.{str(0 if pd.isna(x.version_2) else int(x.version_2))}"
    ),
    "gene=gene_1+gene_2": lambda x: "-".join(
        sorted((set(x.gene_1.split("-")) | set(x.gene_2.split("-"))))
    ),
    "gene": lambda x: x.gene[1:] if x.gene.startswith("-") else x.gene,
    "path_in_repo": lambda x: f"pdb/{'-'.join(sorted(x.protein.split('-')))}/{'-'.join(sorted(x.taxonomy.split('-')))}/{x.name}",
    "exp_method": lambda x: "; ".join(
        x.exp_method.replace("X-RAY", "X_RAY").split("-")
    ),
    "superseded_by": lambda x: float("NaN"),
    "relevant_chains": lambda row: ", ".join(
        [chr(int(x.split("_")[1]) + 64) for x in row.relevant_chains.split("-")]
    ),
    # "author_chains": lambda row: ", ".join([x for x in row.author_chains.split("-")]),
}
