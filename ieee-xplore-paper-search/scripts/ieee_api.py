"""Shared IEEE Xplore API key loading and failover helpers."""

from __future__ import annotations

import os
from typing import Any

import requests

API_BASE = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

# Retry with backup key on inactive developer account or rate limiting.
RETRYABLE_STATUS = {403, 429}


def load_api_keys() -> list[str]:
    """Return ordered API keys: primary first, then backup, deduplicated."""
    keys: list[str] = []
    bulk = os.environ.get("IEEE_XPLORE_API_KEYS", "").strip()
    if bulk:
        keys.extend(part.strip() for part in bulk.replace(",", " ").split() if part.strip())

    primary = os.environ.get("IEEE_XPLORE_API_KEY", "").strip()
    backup = os.environ.get("IEEE_XPLORE_API_KEY_BACKUP", "").strip()

    if primary and primary not in keys:
        keys.insert(0, primary)
    if backup and backup not in keys:
        keys.append(backup)

    seen: set[str] = set()
    ordered: list[str] = []
    for key in keys:
        if key not in seen:
            seen.add(key)
            ordered.append(key)
    return ordered


def get_with_key_failover(
    params: dict[str, Any],
    *,
    base_url: str = API_BASE,
    timeout: int = 60,
) -> requests.Response:
    """GET from IEEE API, trying backup keys on inactive/rate-limited responses."""
    keys = load_api_keys()
    if not keys:
        msg = (
            "No IEEE API keys configured. Set IEEE_XPLORE_API_KEY in scripts/env.local.sh"
        )
        raise RuntimeError(msg)

    last_response: requests.Response | None = None
    for index, key in enumerate(keys):
        request_params = {**params, "apikey": key}
        response = requests.get(base_url, params=request_params, timeout=timeout)
        last_response = response
        if response.status_code == 200:
            return response
        if response.status_code in RETRYABLE_STATUS and index < len(keys) - 1:
            continue
        response.raise_for_status()

    if last_response is not None:
        last_response.raise_for_status()
    raise RuntimeError("IEEE API request failed")
