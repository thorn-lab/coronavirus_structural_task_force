# Cryo-EM model-map validation

The `em_map_fit` step scores how well an electron-microscopy model fits its
map. It reproduces the *Atomic model validation* job of CCP-EM
(`pipeliner.atomic_model_validation`), which is what the Coronavirus
Structural Task Force used for its cryo-EM indicators:

| Score | Program | What it measures |
|---|---|---|
| FSCavg | servalcat | Model-map Fourier shell correlation, averaged up to the map resolution and weighted by the number of Fourier coefficients per shell, inside a soft-edged mask around the model. Also stored: over all shells, and up to FSC = 0.5. |
| CCC, MI, overlap | TEMPy (`TEMPy.scores`) | Real-space correlation, mutual information and overlap, with the map contoured at the recommended level. |
| SMOC outliers | TEMPy (`TEMPy.smoc`) | Share of residues whose local fit (SMOC) has a Z-score below −2.0 relative to residues within 12 Å. |

The contour is the author-recommended level from the entry's EMDB header
(`emd-XXXX.xml`). If there is none, it is 1.5 × the spread of map values above
the background peak, CCP-EM's default. The resolution comes from the model
file, then the EMDB header. If neither has one, pass a fallback (see below).

Results go to `validation/em_validation/` in each entry folder:
`model_map_validation.json` is the summary, and `tool_output/` holds the raw
program outputs, including `smoc_per_residue.tsv`.

## Options

```python
from cstf.validate.orchestrator import run_pipeline

run_pipeline(df, repo_path, steps=["em_map_fit"],
             step_options={"em_map_fit": {"resolution": 3.5, "timeout": 7200}})
```

`resolution` is used only when neither the model nor the EMDB header has
one. `timeout` is in seconds per program (default 3600). servalcat and
`biotempy` are dependencies of this package, so nothing else needs
installing, on Windows as well.

## Agreement with CCP-EM

On PDB 6nur (EMD-0520), CCP-EM's job (ccpem-pipeliner 1.6.1 with servalcat
0.4.131) and this step (servalcat 0.4.142) agreed on every reported number.
That covers all three FSCavg values, CCC, MI, overlap, the SMOC outlier
share, every per-residue SMOC Z-score, and the default contour. The
comparison used the pipeliner package from PyPI; a full CCP-EM installation
may bundle other program versions, and those can change the numbers.

## Differences from the original Task Force results

The Task Force ran CCP-EM 1.5 in 2021, which used REFMAC for the FSC and an
older TEMPy. Today's CCP-EM, and therefore this step, give the same
per-residue SMOC values as that run. Several other numbers do not match the
originals:

- **FSCavg:** servalcat agrees closely with REFMAC (0.746 vs 0.740 for 6nur
  with a hard model mask). With CCP-EM 2's soft-edged mask, used here,
  it is 0.718.
- **CCC and MI:** these come from a different TEMPy version and are not
  comparable to the 2021 values. In current TEMPy, MI with a contour is close
  to zero for maps in a large box, because the default (C) implementation
  counts every voxel outside the contour. CCP-EM 2 reports this value as it
  is, and so does this step.
- **SMOC outliers:** the 2021 Z-scores were calculated differently. Expect
  different outlier counts, even though the SMOC values match.

The thresholds in the Task Force paper (average FSC < 0.4, MI < 0.4, more than
10 % SMOC outliers) were set on the 2021 scales, so they do not carry over
directly.
