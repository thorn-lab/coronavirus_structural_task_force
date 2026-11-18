"""Result persistence and README rendering, without network or cctbx runs."""

from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from cstf.validate.readme import WriteReadmeStep


class FakeLinks:
    """Link checker that accepts only the URLs it was given."""

    def __init__(self, existing=()):
        self.existing = set(existing)
        self.checked = []

    def exists(self, url, probe=None):
        self.checked.append(probe or url)
        return (probe or url) in self.existing


class Score(ValidationStep):
    name = "score"

    def __init__(self, value=None, fail=False, **kw):
        super().__init__(**kw)
        self.value, self.fail = value, fail

    def execute(self, entry):
        if self.fail:
            raise RuntimeError("boom")
        return self.value

    def summarize(self, entry, result):
        return {"value": result}


class EmOnly(ValidationStep):
    name = "em_only"

    def check_input(self, entry):
        return None if entry.is_em else "not_applicable: EM only"


def make_entry(tmp_path: Path) -> Entry:
    path = tmp_path / "pdb" / "some_protein" / "SARS-CoV-2" / "1abc"
    path.mkdir(parents=True)
    (path / "1abc.pdb").write_text("")
    return Entry("1abc", path, exp_method="X-RAY DIFFRACTION", files={"pdb": path / "1abc.pdb"})


def test_summary_is_persisted_and_merged_across_runs(tmp_path):
    entry = make_entry(tmp_path)
    assert Score(value=1).run(entry) == "done"
    entry.record("other", "done", {"x": 2})

    store = entry.load_summary()
    assert store["score"]["data"] == {"value": 1}
    assert store["other"]["data"] == {"x": 2}


def test_failure_never_replaces_earlier_success(tmp_path):
    entry = make_entry(tmp_path)
    Score(value=1).run(entry)
    assert Score(fail=True, skip_existing=False).run(entry).startswith("error")
    assert entry.load_summary()["score"]["data"] == {"value": 1}


def test_complete_output_without_summary_is_rerun(tmp_path):
    entry = make_entry(tmp_path)

    class Done(Score):
        def is_complete(self, entry):
            return True

    assert Done(value=3).run(entry) == "done"  # no stored summary yet
    assert Done(value=4).run(entry) == "skipped"
    assert entry.load_summary()["score"]["data"] == {"value": 3}


def test_readme_lists_missing_steps_and_keeps_old_results(tmp_path):
    entry = make_entry(tmp_path)
    readme = WriteReadmeStep(
        step_classes={"score": Score, "em_only": EmOnly},
        link_checker=FakeLinks(),
    )

    readme.run(entry)
    text = (entry.path / "README.md").read_text()
    assert "- **score**: not run yet" in text
    assert "em_only" not in text  # not applicable to X-ray entries

    Score(value=7).run(entry)
    readme.run(entry)
    text = (entry.path / "README.md").read_text()
    assert "## Validation not performed" not in text
    assert "**Protein name**: some protein" in text


def test_unverified_links_are_left_out(tmp_path):
    entry = make_entry(tmp_path)
    links = FakeLinks({"https://data.rcsb.org/rest/v1/core/entry/1abc"})
    WriteReadmeStep(step_classes={}, link_checker=links).run(entry)
    text = (entry.path / "README.md").read_text()
    assert "**PDBr**: https://www.rcsb.org/structure/1abc" in text
    assert "PDBe" not in text
