import logging
import zipfile
from pathlib import Path

DRIVER_FOLDER = Path(__file__).parent / "drivers"
LOG_FILE = Path(__file__).parent / "driver_management.log"


def setup_logging():
    """Configure logging for driver management."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def list_driver_zips():
    """List all driver ZIP files in the driver folder."""
    return list(DRIVER_FOLDER.glob("*.zip"))


def is_already_extracted(marker_file):
    """Check if a driver ZIP file is already extracted."""
    return marker_file.exists()


def extract_driver_zip(zip_path):
    """Extract a driver ZIP file to a subdirectory."""
    extract_path = DRIVER_FOLDER / f"{zip_path.stem}_extracted"
    marker_file = extract_path / ".installed"

    if is_already_extracted(marker_file):
        logging.info("Skipping already extracted: %s", zip_path.name)
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        marker_file.touch()
        logging.info("Extracted: %s to %s", zip_path.name, extract_path)
    except zipfile.BadZipFile:
        logging.error("Failed to extract (corrupted): %s", zip_path.name)


def extract_all_drivers():
    """Extract all driver ZIP files in the driver folder."""
    driver_zips = list_driver_zips()
    if not driver_zips:
        logging.warning("No driver ZIP files found.")
        return

    for zip_path in driver_zips:
        extract_driver_zip(zip_path)


if __name__ == "__main__":
    setup_logging()
    extract_all_drivers()
