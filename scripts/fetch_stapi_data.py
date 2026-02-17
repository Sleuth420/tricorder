#!/usr/bin/env python3
# --- scripts/fetch_stapi_data.py ---
# Fetches Star Trek data from STAPI (https://stapi.co) and saves to data/stapi/ for the tricorder wiki view.
# Run from project root: python scripts/fetch_stapi_data.py
# Or trigger from Settings > Star Trek Data in the app.

import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# Project root (parent of scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "stapi"
STAPI_BASE = "https://stapi.co/api"

# Limit pages per entity to avoid hammering the API; increase if you want more data
MAX_PAGES_PER_ENTITY = 5
PAGE_SIZE = 50
REQUEST_DELAY_SEC = 0.5

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _get_search_url(version, entity, page=0):
    return f"{STAPI_BASE}/v{version}/rest/{entity}/search?pageNumber={page}&pageSize={PAGE_SIZE}"


def _fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Tricorder-STAPI/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _fetch_all_pages(version, entity, list_key, progress_callback=None):
    """Fetch up to MAX_PAGES_PER_ENTITY pages of search results. list_key is e.g. 'characters', 'spacecrafts'."""
    all_items = []
    page = 0
    total_pages = 1
    while page < MAX_PAGES_PER_ENTITY and page < total_pages:
        url = _get_search_url(version, entity, page)
        try:
            data = _fetch_json(url)
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            logger.warning("Fetch failed for %s page %s: %s", entity, page, e)
            break
        items = data.get(list_key, [])
        if not items:
            break
        all_items.extend(items)
        pagination = data.get("page", {})
        total_pages = pagination.get("totalPages", 1)
        total_elements = pagination.get("totalElements", 0)
        if progress_callback:
            progress_callback(entity, page + 1, total_pages, len(all_items), total_elements)
        page += 1
        time.sleep(REQUEST_DELAY_SEC)
    return all_items


def fetch_characters(progress_callback=None):
    # v1: character/search -> characters
    return _fetch_all_pages(1, "character", "characters", progress_callback)


def fetch_spacecraft(progress_callback=None):
    # v2: spacecraft/search -> spacecrafts
    return _fetch_all_pages(2, "spacecraft", "spacecrafts", progress_callback)


def fetch_species(progress_callback=None):
    # v2: species/search -> species
    return _fetch_all_pages(2, "species", "species", progress_callback)


def fetch_technology(progress_callback=None):
    # v2: technology/search -> technology
    return _fetch_all_pages(2, "technology", "technology", progress_callback)


def fetch_astronomical_objects(progress_callback=None):
    # v2: astronomicalObject/search -> astronomicalObjects
    return _fetch_all_pages(2, "astronomicalObject", "astronomicalObjects", progress_callback)


def run_fetch(progress_callback=None):
    """
    Fetch characters, spacecraft, species, technology, and astronomical objects from STAPI.
    Saves JSON files under data/stapi/. progress_callback(entity, page, total_pages, count, total) is optional.
    """
    _ensure_data_dir()
    results = {}

    entities = [
        ("characters", fetch_characters),
        ("spacecraft", fetch_spacecraft),
        ("species", fetch_species),
        ("technology", fetch_technology),
        ("astronomicalObjects", fetch_astronomical_objects),
    ]
    for name, fetch_fn in entities:
        logger.info("Fetching %s...", name)
        try:
            items = fetch_fn(progress_callback)
            results[name] = items
            out_path = DATA_DIR / f"{name}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            logger.info("Saved %s entries to %s", len(items), out_path)
        except Exception as e:
            logger.exception("Error fetching %s: %s", name, e)
            results[name] = []

    # Write a combined manifest with counts and timestamp
    manifest = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {k: len(v) for k, v in results.items()},
    }
    with open(DATA_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Manifest written: %s", manifest)
    return results


def main():
    run_fetch()
    return 0


if __name__ == "__main__":
    sys.exit(main())
