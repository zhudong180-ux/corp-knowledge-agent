import os

from src.config import Settings, get_settings, reset_settings_cache


def test_settings_loads_from_env(monkeypatch):
    reset_settings_cache()
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    settings = get_settings()
    assert settings.llm_mode == "mock"
    assert settings.llm_base_url == "https://example.com/v1"
    assert settings.llm_api_key == "test-key"
    assert settings.llm_model == "test-model"
    reset_settings_cache()


def test_settings_max_react_steps_default():
    reset_settings_cache()
    os.environ.pop("MAX_REACT_STEPS", None)
    s = get_settings()
    assert s.max_react_steps == 3
    reset_settings_cache()


def test_settings_instantiation():
    s = Settings()
    assert s.llm_model == "deepseek-chat"
    assert s.max_react_steps >= 1