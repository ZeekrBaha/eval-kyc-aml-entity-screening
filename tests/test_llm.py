import pytest
from sut.llm import CacheReplayLLM, cache_key


def test_cache_key_is_stable_and_model_sensitive():
    a = cache_key("gpt-4o", "hello")
    b = cache_key("gpt-4o", "hello")
    c = cache_key("gpt-4o-mini", "hello")
    assert a == b
    assert a != c


def test_offline_replay_returns_cached_response(tmp_path):
    key = cache_key("gpt-4o", "PROMPT")
    (tmp_path / f"{key}.json").write_text(
        '{"model": "gpt-4o", "prompt": "PROMPT", "response": "CACHED"}'
    )
    llm = CacheReplayLLM(cache_dir=tmp_path)
    assert llm.complete("gpt-4o", "PROMPT") == "CACHED"


def test_offline_replay_misses_fail_closed(tmp_path):
    llm = CacheReplayLLM(cache_dir=tmp_path)
    with pytest.raises(KeyError):
        llm.complete("gpt-4o", "UNSEEN PROMPT")
