"""Configuration tests for the Streamlit chat adapter."""
from unittest.mock import patch

from portfolio_lens.chat_ui import setting


def test_environment_setting_takes_precedence(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "env-model")
    assert setting("OPENAI_MODEL") == "env-model"


def test_reads_streamlit_secrets(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    with patch("portfolio_lens.chat_ui.st.secrets", {"OPENAI_MODEL": "secret-model"}):
        assert setting("OPENAI_MODEL") == "secret-model"


def test_missing_secrets_returns_default(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    with patch("portfolio_lens.chat_ui.st.secrets") as secrets:
        secrets.get.side_effect = FileNotFoundError
        assert setting("OPENAI_MODEL", "default-model") == "default-model"
