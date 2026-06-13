from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Protocol

CACHE_DIR = Path("evals/cache")


def cache_key(model: str, prompt: str) -> str:
    raw = f"{model}\x00{prompt}".encode()
    return hashlib.sha256(raw).hexdigest()[:24]


class LLM(Protocol):
    def complete(self, model: str, prompt: str) -> str: ...


class CacheReplayLLM:
    """Offline: serve responses from committed cache files. Miss => fail closed."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        self.cache_dir = cache_dir

    def complete(self, model: str, prompt: str) -> str:
        path = self.cache_dir / f"{cache_key(model, prompt)}.json"
        if not path.exists():
            raise KeyError(f"offline cache miss for {model}: {path.name}")
        data = json.loads(path.read_text())
        return str(data["response"])


class LiveLLM:
    """Live: call OpenAI and record the response into the cache for later replay."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        from openai import OpenAI  # imported lazily; only needed for live runs

        self.client = OpenAI()
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def complete(self, model: str, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.choices[0].message.content or ""
        path = self.cache_dir / f"{cache_key(model, prompt)}.json"
        path.write_text(json.dumps({"model": model, "prompt": prompt, "response": text}))
        return text


def make_llm(cache_dir: Path = CACHE_DIR) -> LLM:
    """KYCEVAL_OFFLINE=1 (default) => replay; =0 => live OpenAI."""
    offline = os.environ.get("KYCEVAL_OFFLINE", "1") != "0"
    return CacheReplayLLM(cache_dir) if offline else LiveLLM(cache_dir)
