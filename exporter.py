#!/usr/bin/env python3
"""MangaDex to ComicK library exporter.

This script reads the list of manga followed by a MangaDex account and
attempts to mark the same manga as followed on ComicK.  Both services
require authentication tokens which must be supplied by the user.

The script is intentionally lightweight; it performs a best‑effort
search for each MangaDex title on ComicK and adds the first match to the
ComicK library.  The search and export endpoints used here are based on
public API documentation at the time of writing and may need to be
updated if either service changes their API.

Example usage::

    python exporter.py --md-username myuser --md-password secret \
        --comick-token COMICKTOKEN

A dry run mode is provided for verifying the titles that would be
exported without modifying the ComicK library.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Iterable, Dict, Any

import requests

MANGADEX_API = "https://api.mangadex.org"
COMICK_API = "https://api.comick.app"

logger = logging.getLogger("exporter")


def login_mangadex(username: str, password: str) -> str:
    """Authenticate against MangaDex and return a session token."""
    resp = requests.post(
        f"{MANGADEX_API}/auth/login",
        json={"username": username, "password": password},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["token"]["session"]


def iter_mangadex_library(session_token: str, limit: int = 100) -> Iterable[Dict[str, Any]]:
    """Yield all manga followed by the authenticated MangaDex user."""
    offset = 0
    headers = {"Authorization": f"Bearer {session_token}"}
    while True:
        params = {"limit": limit, "offset": offset}
        resp = requests.get(
            f"{MANGADEX_API}/user/follows/manga",
            headers=headers,
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        for item in payload.get("data", []):
            yield item
        offset += limit
        if offset >= payload.get("total", 0):
            break


def search_comick(title: str) -> Dict[str, Any] | None:
    """Return the first ComicK search result for *title*.

    The search API is unauthenticated.  If no result is found ``None`` is
    returned.
    """
    resp = requests.get(
        f"{COMICK_API}/search",
        params={"q": title, "limit": 1},
        timeout=30,
    )
    if resp.status_code != 200:
        logger.warning("ComicK search for %s failed: %s", title, resp.text)
        return None
    results = resp.json().get("data")
    if not results:
        return None
    return results[0]


def add_to_comick_library(comic_id: Any, token: str) -> None:
    """Add a comic to the authenticated ComicK user's library."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{COMICK_API}/user/library",
        headers=headers,
        json={"comic": comic_id},
        timeout=30,
    )
    resp.raise_for_status()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export MangaDex library to ComicK")
    parser.add_argument("--md-username", help="MangaDex username")
    parser.add_argument("--md-password", help="MangaDex password")
    parser.add_argument("--md-token", help="Existing MangaDex session token")
    parser.add_argument("--comick-token", required=True, help="ComicK API token")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify ComicK library")
    parser.add_argument("--limit", type=int, default=100, help="Batch size for MangaDex API")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if not args.md_token:
        if not (args.md_username and args.md_password):
            parser.error("--md-username and --md-password required if --md-token not provided")
        md_token = login_mangadex(args.md_username, args.md_password)
    else:
        md_token = args.md_token

    for entry in iter_mangadex_library(md_token, limit=args.limit):
        title_map = entry.get("attributes", {}).get("title", {})
        title = title_map.get("en") or next(iter(title_map.values()), None)
        if not title:
            logger.warning("Skipping title with no name: %s", entry.get("id"))
            continue
        result = search_comick(title)
        if not result:
            logger.warning("No ComicK match for %s", title)
            continue
        comic_id = result.get("id")
        if args.dry_run:
            logger.info("Would add '%s' (ComicK id %s)", title, comic_id)
        else:
            try:
                add_to_comick_library(comic_id, args.comick_token)
                logger.info("Added '%s'", title)
            except requests.HTTPError as exc:  # pragma: no cover - network errors
                logger.error("Failed to add %s: %s", title, exc)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
