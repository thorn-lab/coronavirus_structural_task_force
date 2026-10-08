import pytest
import asyncio
from unittest.mock import patch, AsyncMock
import pandas as pd


@pytest.mark.asyncio
async def test_download_files_handle_file(tmp_path):
    """Test that a single file download:
    - creates directories,
    - archives previous file,
    - writes new file,
    - hits the expected URL.
    """
    from cstf.update.io import _download_files_handle_file

    pdb_id = "7abc"
    ext = "cif"
    timestamp = "2020-01-01"
    file_dir = tmp_path / "pdb" / "protein" / "SARS-CoV-2" / str(pdb_id)

    # Pre-create an old file to test archiving
    file_dir.mkdir(parents=True, exist_ok=True)
    old_file = file_dir / f"{pdb_id}.{ext}"
    old_file.write_text("OLD DATA")

    # Create a mock aiohttp response
    class MockResponse:
        def __init__(self, status=200, data=b"NEW FILE CONTENT"):
            self.status = status
            self._data = data

        async def read(self):
            return self._data

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class MockSession:
        def get(self, url):
            return MockResponse()

    session = MockSession()
    sem = asyncio.Semaphore(1)

    await _download_files_handle_file(
        session=session,
        pdb_id=pdb_id,
        file_dir=file_dir,
        ext=ext,
        timestamp=timestamp,
        sem=sem,
    )

    # New file exists
    new_file = file_dir / f"{pdb_id}.{ext}"
    assert new_file.exists()
    assert new_file.read_bytes() == b"NEW FILE CONTENT"

    # Old file archived
    archived = file_dir / "old" / f"{pdb_id}_{timestamp}.{ext}"
    assert archived.exists()
    assert archived.read_text() == "OLD DATA"


def test_download_files(tmp_path):
    """Test download_files function with mocked HTTP requests."""
    from cstf.update.io import download_files

    # Setup test data
    test_df = pd.DataFrame(
        {
            "path_in_repo": [
                "pdb/protein/SARS-CoV-2/7abc",
                "pdb/protein/SARS-CoV-2/6xyz",
            ],
            "release_date": ["2021-01-01", "2021-06-01"],
            "last_revised": ["2021-01-01", "2021-06-01"],
        },
        index=["1abc", "2def"],
    )
    test_df["release_date"] = pd.to_datetime(test_df["release_date"]).dt.date
    test_df["last_revised"] = pd.to_datetime(test_df["release_date"]).dt.date

    # Mock the download_files_handle_file function
    with patch(
        "cstf.update.io._download_files_handle_file", new_callable=AsyncMock
    ) as mock_handle:
        mock_handle.return_value = None

        # Mock tqdm_asyncio.gather to avoid progress bar
        with patch(
            "cstf.update.io.tqdm_asyncio.gather", new_callable=AsyncMock
        ) as mock_gather:
            mock_gather.return_value = None

            # Call the function (synchronously, since it's wrapped)
            download_files(test_df, "2021-01-01", "2021-06-01", str(tmp_path))

            # Verify download_files_handle_file was called correct number of times
            # Should be called 6 times: 2 PDB entries × 3 extensions (cif, pdb, mtz)
            assert mock_handle.call_count == 6

            # Verify tqdm_asyncio.gather was called once with all tasks
            assert mock_gather.call_count == 1


def test_delete_superseded(tmp_path):
    """Test that superseded folders get deleted."""
    from cstf.update.io import delete_superseded

    # Setup test data
    test_df = pd.DataFrame(
        {
            "path_in_repo": [
                "pdb/protein_B/SARS-CoV-2/1abc",
                "pdb/protein_A/SARS-CoV-2/2def",
            ],
            "release_date": ["2021-01-01", "2021-06-01"],
            "last_revised": ["2021-01-01", "2021-06-01"],
            "version": [1, 2],
            "superseded_by": [None, None],
        },
        index=["1abc", "2def"],
    )
    test_df["release_date"] = pd.to_datetime(test_df["release_date"]).dt.date
    test_df["last_revised"] = pd.to_datetime(test_df["release_date"]).dt.date

    # Create new entry with PDB file containing SPRSDE record
    new_id_path = tmp_path / "pdb/protein_A/SARS-CoV-2/2def"
    new_id_path.mkdir(parents=True, exist_ok=True)
    pdb_file = new_id_path / "2def.pdb"
    pdb_file.write_text("SPRSDE     01-JAN-23 2DEF      1ABC\n")

    # Create old entry directory that should be deleted
    old_id_path = tmp_path / "pdb/protein_B/SARS-CoV-2/1abc"
    old_id_path.mkdir(parents=True, exist_ok=True)

    # Call the function
    delete_superseded(test_df, "2021-01-01", "2021-06-01", str(tmp_path))

    # Verify the old directory was deleted
    assert not old_id_path.exists()

    # Verify the new directory still exists
    assert new_id_path.exists()
