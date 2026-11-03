"""Synchronize Day 02 to the existing main /docs GitHub Pages site."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def sync_pages():
    destination = ROOT / "docs/02"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "02/outputs/waterfront_walks_preview.html", destination / "index.html")
    print("Synchronized Day 02:", destination)


if __name__ == "__main__":
    sync_pages()
