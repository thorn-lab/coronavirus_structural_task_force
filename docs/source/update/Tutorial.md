# Tutorial

## Installation

To clone the repo with everything except the pdb folder do 

```
bash
git clone --filter=blob:none --sparse [https://github.com/jnt18/coronavirus_structural_task_force.git](https://github.com/jnt18/coronavirus_structural_task_force.git)
cd coronavirus_structural_task_force
git sparse-checkout init --cone
git sparse-checkout set $(git ls-tree -d --name-only HEAD \vert{} grep -v '^pdb$')
```

If git checkout fails with an NTFS protection error due to special characters in file paths, run:
```
git config core.protectNTFS false
git checkout master
git config core.protectNTFS true
```

Then run

```
uv sync
```

Then import the modules from the update package:
```
from cstf.update import config, query, io, report, align, RMSD, utils
```

In addition to the Python packages installed by `uv`, the structural-validation tools require the CCTBX `chem_data` reference dataset. This data is downloaded automatically by `scripts/setup_chem_data.py`, verified against the expected CCTBX release checksum, and linked into the virtual environment so that CCTBX/mmtbx can discover it. To download the data run

```
uv run --with zstandard python scripts/setup_chem_data.pys
```

## Example

(usage-get-ids)=
### Getting ids {py:func}`query.get_ids() <cstf.update.query.get_ids>`

Let's say we are interested in the latest structures of two subtypes of Influenza A.
To get the associated rcsb queries do 
```
preset = config.Presets()
rcsb_queries = preset.queries("H1N1", "H3N2")
```

Set the start and end values in ISO format: "YYYY-MM-DD".
If you want the previous Wednesday as the start date and next Wednesday as the end date you can do 
start, end = str(utils.get_time()), str(utils.get_time(next_week=True))

Now we are ready to get the entity_ids associated to these queries that were released or revised within the start and end date.

```
ids_by_taxonomy = query.get_ids(start, end, rcsb_queries)
```

(usage-get-proteins)=
### Getting proteins {py:func}`query.get_proteins() <cstf.update.query.get_proteins>`
If you have fasta files of a reference proteom you can get the protein each entity_id is most similar to.
If you do not have such files you can skip this step.

First get your fasta file paths. For example: 

```
from pathlib import Path
fasta_path = Path.cwd() / "data" / "fasta"
fasta_paths = [fasta_path / "seq_H1N1.fasta", fasta_path / "seq_H3N2.fasta"]
```

Now you can do 

```
ids_by_taxonomy_and_protein = query.get_proteins(ids_by_taxonomy, fasta_paths)
```

(usage-get-df)=
### Getting Metadata in a dataframe {py:func}`query.get_df() <cstf.update.query.get_df>`

For the query.get_df function you can choose if you want to group by entry ids (aggregate=True). Do this to
use the remaining modules in the package.

You can get a dataframe with just the release date, revision date and taxonomy by doing

```
df = query.get_df(ids_by_taxonomy)
```

If you got the proteins in the previous step, they can be added as well:

```
df = query.get_df(ids_by_taxonomy_and_protein)
```

When you run this function again, for example next week, you can provide the current df as an argument and
it will get updated with the new ids inplace. 

#### Additional attributes
You can provide additional rcsb_data_attributes as an argument.
To find such attributes for example relating to the word "title" run

```
from rcsbapi.data import DataSchema
schema = DataSchema()
schema.find_paths("polymer_entities", "title")
```

You might have to try a few of the results before you find the one you are looking for. 
In this case 'entry.struct.title'.
To add a column named "title with all the titles create a dictionary with column names as keys:

```
attributes =  {'title': 'entry.struct.title'}
```

Now run 

```
df = query.get_df(ids_by_taxonomy_and_protein, attributes)
```

To use the attributes the cstf has used do for example
```
preset = config.Presets()
attributes = preset.attributes("title", "version_1", "version_2")
```

In this case we might combine the major version (e.g. version_1: 3) and the minor version (e.g. version_2: 4) in version: 3.4

Do to this write a function f that would work as input to df.apply(f, axis=1).
In this case we can use 

```
functions = preset.functions("version=version_1+version_2")
```

and then do 

```
df = query.get_df(ids_by_taxonomy_and_protein, attributes, functions)
```


#### Set download paths in the dataframe

To use the following modules, include the path_in_repo function. 
```
functions = preset.functions("path_in_repo")
df = query.get_df(ids_by_taxonomy_and_protein, attributes, functions)
```

(usage-download)=
### Downloading files {py:func}`io.download_files() <cstf.update.io.download_files>`

Make sure your dataframe contains data paths for each entry_id (see above).
Then choose a repo_path. Inside this root directory there will be a directory called 'pdb' to
which structure data (cif, mtz, pdb) can be downloaded.
For example

```
repo_path = Path.cwd() / "data" 
io.download_files(df, start, end, repo_path)
```

If you only want for example pdb files you can do 

```
io.download_files(df, start, end, repo_path, extensions=["pdb"])
```

(usage-superseded)=
#### Delete superseded files {py:func}`io.delete_superseded() <cstf.update.io.delete_superseded>`

Next time you download files, a new id might have superseded an old id which you downloaded just now.
To delete the superseded files and update the dataframe run

```
io.delete_superseded(df, start, end, repo_path)
```

(usage-report)=
### Write reports {py:func}`report.write_reports() <cstf.update.report.write_reports>`

To write weekly reports of structures that got released or revised that week run

```
report.write_reports(df, start, end, repo_path)
```

This will write reports in a directory called weekly_reports inside your chosen repo_path. 
There will also be a report summarising the full period, which is overwritten the next time you call the function.

(usage-align)=
### Sequence Alignment {py:func}`align.sequence_alignment() <cstf.update.align.sequence_alignment>`

If you have fasta files of a reference proteom you can do sequence alignment between each chain that was relevant for 
one of the queries, and the sequence of the protein it was assigned. 

To get the relevant chains you need the attribute 'relevant_chains' and the function 'relevant_chains':

```
preset = config.Presets()
attributes = preset.attributes("relevant_chains")
functions = preset.functions("path_in_repo", "relevant_chains")
df = query.get_df(ids_by_taxonomy_and_protein, attributes, functions)
```

You also need to have downloaded pdb and cif files. Then do 

```
align.sequence_alignment(df, start, end, repo_path, fasta_paths)
```

(usage-rmsd)=
### RMSD calculation {py:func}`RMSD.calculate_rmsd() <cstf.update.RMSD.calculate_rmsd>`

To compare structures that were assigned the same proteins (across taxonomies) do

```
RMSD.calculate_rmsd(df, start, end, repo_path)
````

As this does pairwise comparisons and keeps track of the best chain combination it is recommended to 
have the column relevant_chains in the data frame i.e., doing 

```
preset = config.Presets()
attributes = preset.attributes("relevant_chains")
functions = preset.functions("path_in_repo", "relevant_chains")
df = query.get_df(ids_by_taxonomy_and_protein, attributes, functions)
```

Now only relevant chains will be compared with each other. 