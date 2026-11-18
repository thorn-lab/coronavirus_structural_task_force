import logging
from pathlib import Path
from cstf.validate.base import Entry, ValidationStep
import re
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://cmm.minorlab.org/static/neighborhood_temp"


class CheckMyMetalStep(ValidationStep):
    """Fetch available CheckMyMetal neighborhood images for one entry."""

    name = "checkmymetal"

    def output_dir(self, entry: Entry) -> Path:
        return entry.validation_dir / "checkmymetal"

    def execute(self, entry: Entry) -> list[str]:
        return self._download(
            entry.pdb_id,
            self.output_dir(entry),
            skip_existing=self.skip_existing,
        )

    def format_result(self, result: list[str]) -> str:
        if result:
            return "done ({} files)".format(len(result))
        return "done (no metal sites listed)"

    def summarize(self, entry: Entry, result: list[str]) -> dict:
        return {
            "directory": entry.rel(self.output_dir(entry)),
            "files": [entry.rel(self.output_dir(entry) / name) for name in result],
            "source": "{}/{}/".format(BASE_URL, entry.pdb_id.lower()),
        }

    @staticmethod
    def _download(pdb_id, output_dir, skip_existing=True):
        """
        Discover and download all available CheckMyMetal PNG images for a given PDB entry
        by inspecting the static directory listing.

        Args:
            pdb_id: The PDB ID / entry identifier (normalized to lowercase for URL).
            output_dir: Path to the target 'checkmymetal' directory.
            skip_existing: If True, skip downloading files that already exist.

        Returns:
            list of successfully downloaded or skipped filenames.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        entry_key = str(pdb_id).lower()
        dir_url = f"{BASE_URL}/{entry_key}/"
        processed = []

        png_files = set()

        # Network/server failures propagate so they are recorded as errors
        # instead of being mistaken for "no metal sites".
        response = requests.get(dir_url, timeout=30)
        if response.status_code == 404:
            logger.info(
                "No CheckMyMetal directory found (404) for %s (entry likely has no metal sites)",
                entry_key,
            )
            return processed
        response.raise_for_status()
        # Extract all .png filenames from the directory listing HTML links
        links = re.findall(
            r'href=["\']([^"\']+\.png)["\']', response.text, re.IGNORECASE
        )
        png_files.update(Path(link).name for link in links if Path(link).name)

        if not png_files:
            logger.info("No PNG images found in CheckMyMetal directory for %s", entry_key)
            return processed

        # Download each discovered PNG file
        for filename in sorted(png_files):
            file_path = output_path / filename
            if skip_existing and file_path.exists():
                processed.append(filename)
                continue

            file_url = f"{dir_url}{filename}"
            try:
                file_resp = requests.get(file_url, timeout=30)
                if file_resp.status_code == 200:
                    file_path.write_bytes(file_resp.content)
                    processed.append(filename)
                elif file_resp.status_code == 404:
                    logger.warning(
                        "CheckMyMetal image not found (404) for %s: %s", entry_key, filename
                    )
                else:
                    file_resp.raise_for_status()
            except Exception as exc:
                logger.error(
                    "Failed to download %s for %s from %s: %s",
                    filename,
                    entry_key,
                    file_url,
                    exc,
                )

        return processed
