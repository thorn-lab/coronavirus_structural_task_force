"""This module provides functions for downloading structure files and managing superseded entries."""

import asyncio
import aiofiles
import aiohttp
import shutil
import gemmi
import zlib
import os
from datetime import date, datetime, time as dt_time, timezone
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio
import pandas as pd
from typing import Iterable
from .utils import async_wrapper, get_current_df

EMDB_FTP = "https://ftp.ebi.ac.uk/pub/databases/emdb/structures"
RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry"

HTML_STUB = """<html>
   <body>
      <script type="text/javascript">
    window.location.href = "ftp://ftp.wwpdb.org/pub/emdb/structures/{emd}/map/";
      </script>
   </body>
</html>
"""


@async_wrapper
async def download_files(
    df: pd.DataFrame,
    start: str,
    end: str,
    repo_path: str | Path,
    extensions: list[str] = ["cif", "pdb", "mtz"],
    download_cyro_em: bool = True,
) -> None:
    """Download structure files for all PDB entries in the dataframe that were released
    or revised between the given dates.

    Uses asyncio for concurrent downloads and aiohttp for async HTTP requests. See :ref:`this section <usage-download>`.

    Args:
        df: Output from :func:`~cstf.update.query.get_df` with aggregate=True.
        start: Start date (inclusive), ISO format: YYYY-MM-DD.
        end: End date (inclusive), ISO format: YYYY-MM-DD.
        repo_path: Downloaded files will be stored in a folder called "pdb" in this directory.
        extensions: File types that will be downloaded.
    """

    ids = list(get_current_df(df, start, end).index)

    # Boolean mask: which of these ids are cryo-EM entries
    is_em = (
        (
            df.loc[ids, "exp_method"].astype(str).str.strip().str.upper()
            == "ELECTRON MICROSCOPY"
        ).tolist()
        if download_cyro_em
        else [False] * len(ids)
    )

    sem = asyncio.Semaphore(20)
    connector = aiohttp.TCPConnector(limit=50)
    repo_path = Path(repo_path)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for pdb_id, em in zip(ids, is_em):
            directory = repo_path / Path(df.loc[pdb_id, "path_in_repo"])
            timestamp = df.loc[pdb_id, "release_date"]

            if em:
                tasks.append(
                    _download_em_files(
                        session=session,
                        pdb_id=pdb_id,
                        file_dir=directory,
                        timestamp=timestamp,
                        sem=sem,
                    )
                )

            for ext in extensions:
                tasks.append(
                    _download_files_handle_file(
                        session=session,
                        pdb_id=pdb_id,
                        file_dir=directory,
                        ext=ext,
                        timestamp=timestamp,
                        sem=sem,
                    )
                )

        await tqdm_asyncio.gather(*tasks, return_exceptions=True)


async def _get_emdb_ids(session, pdb_id, sem):
    """Look up the EMDB ids linked to a PDB entry via the RCSB data API."""
    async with sem:
        async with session.get(f"{RCSB_ENTRY}/{pdb_id.upper()}") as r:
            r.raise_for_status()
            data = await r.json()
    return data.get("rcsb_entry_container_identifiers", {}).get("emdb_ids", [])


async def _download_to(session, url, dest: Path, sem):
    """Stream url to dest atomically (via .part file)."""
    partial_path = dest.with_suffix(dest.suffix + ".part")
    try:
        async with sem:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(partial_path, "wb") as out_file:
                    async for chunk in response.content.iter_chunked(1 << 20):
                        out_file.write(chunk)
        partial_path.replace(dest)
    except BaseException:
        partial_path.unlink(missing_ok=True)
        raise


def _inflate_and_write(decompressor, out_file, chunk):
    out_file.write(decompressor.decompress(chunk))


def _inflate_flush(decompressor, out_file):
    out_file.write(decompressor.flush())


async def _download_gunzip_to(session, url, dest: Path, sem):
    """Stream a .gz url, decompress on the fly, write dest atomically."""
    partial_path = dest.with_suffix(dest.suffix + ".part")
    try:
        async with sem:
            async with session.get(url) as response:
                response.raise_for_status()
                decompressor = zlib.decompressobj(wbits=31)  # 16 + 15 = gzip container
                with open(partial_path, "wb") as out_file:
                    async for chunk in response.content.iter_chunked(1 << 20):
                        # zlib + disk write run off the event loop; awaiting each
                        # call keeps chunks in order
                        await asyncio.to_thread(
                            _inflate_and_write, decompressor, out_file, chunk
                        )
                    await asyncio.to_thread(_inflate_flush, decompressor, out_file)
                if not decompressor.eof:
                    raise IOError(f"truncated gzip stream: {url}")
        partial_path.replace(dest)
    except BaseException:
        partial_path.unlink(missing_ok=True)  # never leave a partial file behind
        raise


def _to_epoch_seconds(value) -> float:
    """Convert a date / datetime / pandas Timestamp to epoch seconds."""
    if isinstance(value, datetime):  # pandas.Timestamp is a datetime subclass
        return value.timestamp()
    if isinstance(value, date):
        # date has no time of day, so use midnight (local time)
        return datetime.combine(value, dt_time.min).timestamp()
    raise TypeError(f"unsupported timestamp type: {type(value)!r}")


async def _download_em_files(session, pdb_id, file_dir: Path, timestamp, sem):
    """For one EM entry: download map(s) + header XML, write HTML redirect stub."""
    try:
        file_dir.mkdir(parents=True, exist_ok=True)
        emd_ids = await _get_emdb_ids(session, pdb_id, sem)
        if not emd_ids:
            print(f"[{pdb_id}] no EMDB entry found")
            return
        for emd in emd_ids:  # e.g. "EMD-11994"
            emd_number = emd.split("-")[1]
            base_url = f"{EMDB_FTP}/{emd}"
            xml_path = file_dir / f"emd-{emd_number}.xml"
            map_path = file_dir / f"emd_{emd_number}.map"
            html_path = file_dir / f"{emd}.html"

            # header + map (decompressed in flight) downloaded concurrently
            await asyncio.gather(
                _download_to(
                    session, f"{base_url}/header/emd-{emd_number}.xml", xml_path, sem
                ),
                _download_gunzip_to(
                    session, f"{base_url}/map/emd_{emd_number}.map.gz", map_path, sem
                ),
            )
            html_path.write_text(HTML_STUB.format(emd=emd))

            epoch_seconds = _to_epoch_seconds(timestamp)
            for file_path in (xml_path, html_path, map_path):
                os.utime(file_path, (epoch_seconds, epoch_seconds))
    except Exception as e:
        print(f"[{pdb_id}] EM download failed: {e!r}")


def _convert_sf_cif_to_mtz(cif_path: Path, mtz_path: Path, pdb_id: str) -> None:
    """Blocking conversion of an RCSB structure-factor CIF to MTZ via gemmi."""
    doc = gemmi.cif.read(str(cif_path))
    rblocks = gemmi.as_refln_blocks(doc)
    if not rblocks:
        raise RuntimeError(
            f"No reflection data found in structure factor file for {pdb_id}"
        )

    # Most RCSB entries have one block, but some contain several data sets.
    # Pick the first block that actually has a usable reflection loop.
    cif2mtz = gemmi.CifToMtz()
    mtz = cif2mtz.convert_block_to_mtz(rblocks[0])
    mtz.write_to_file(str(mtz_path))


async def _download_files_handle_file(
    session: aiohttp.ClientSession,
    pdb_id: str,
    file_dir: Path,
    ext: str,
    timestamp: str,
    sem: asyncio.Semaphore,
):
    try:
        async with sem:
            file_dir.mkdir(parents=True, exist_ok=True)
            pdb_lower = pdb_id.lower()
            file_path = file_dir / f"{pdb_id}.{ext}"

            # Archive existing file if it already exists
            if file_path.exists():
                old_dir = file_dir / "old"
                old_dir.mkdir(exist_ok=True)
                archived_path = old_dir / f"{pdb_id}_{timestamp}.{ext}"
                file_path.replace(archived_path)

            if ext == "mtz":
                cif_url = f"https://files.rcsb.org/download/{pdb_lower}-sf.cif"
                cif_path = file_dir / f"{pdb_lower}-sf.cif"

                async with session.get(cif_url) as resp:
                    if resp.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=resp.request_info,
                            history=resp.history,
                            status=resp.status,
                            message=f"Failed to download structure factors for {pdb_id} from RCSB (Status: {resp.status})",
                        )
                    data = await resp.read()

                async with aiofiles.open(cif_path, "wb") as f:
                    await f.write(data)

                try:
                    await asyncio.to_thread(
                        _convert_sf_cif_to_mtz, cif_path, file_path, pdb_id
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"gemmi CIF->MTZ conversion failed for {pdb_id}: {e}"
                    ) from e

            else:
                url = f"https://files.rcsb.org/download/{pdb_id}.{ext}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=resp.request_info,
                            history=resp.history,
                            status=resp.status,
                            message=f"Failed to download {ext} for {pdb_id} from RCSB (Status: {resp.status})",
                        )
                    data = await resp.read()

                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(data)
        return True

    except:
        print(f"Error handling PDB {pdb_id} ({ext}): {e}")
        return False


def delete_superseded(
    df: pd.DataFrame, start: str, end: str, repo_path: str | Path
) -> None:
    """Delete directories of superseded PDB entries and update their status in the dataframe inplace.

    Use after downloading pdb files. Reads pdb files of the :class:`~cstf.update.config.CustomTypes.entry_id`
    that were released or revised between the given dates. If one of these new ids has superseded any old ids,
    the files of the old ids are deleted if they exist and the superseded_by column of the old_ids is updated to contain the new ids.
    See :ref:`this section <usage-superseded>`.

    Args:
        df: Output from :func:`~cstf.update.query.get_df` with aggregate=True and columns "path_in_repo" and "superseded_by"
            which can be made using :func:`~cstf.update.config.Presets.functions`.
        start: Start date (inclusive), ISO format: YYYY-MM-DD.
        end: End date (inclusive), ISO format: YYYY-MM-DD.
        repo_path: Path to the repository root directory containing PDB structure folders.
    Raises:
        FileNotFoundError: If a specified PDB file cannot be read (continues processing).
    """
    repo_path = Path(repo_path)

    ids = list(get_current_df(df, start, end).index)

    for pdb_id in ids:
        id_path = repo_path / Path(df.loc[pdb_id, "path_in_repo"])
        pdb_path = id_path / f"{pdb_id}.pdb"

        if not pdb_path.exists():
            print(f"File {pdb_path} not found.")
            continue

        with pdb_path.open("r") as f:
            for line in f:
                if line.startswith("SPRSDE"):
                    # lines have the form: SPRSDE ... old_ids ...
                    old_ids = line.split()[3:]
                    for old_id in old_ids:
                        old_id = old_id.lower()
                        if old_id in df.index:
                            # mark superseded
                            df.loc[old_id, "superseded_by"] = pdb_id
                            # remove the old file folder if it exists
                            old_path = repo_path / Path(df.loc[old_id, "path_in_repo"])
                            if old_path.exists() and old_path.is_dir():
                                shutil.rmtree(old_path)
                                print(
                                    f"deleted subdirectory for {old_id} as it was superseded by {pdb_id}"
                                )
