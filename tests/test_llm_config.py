"""
Unit tests for LLM configuration helpers.
"""

from pathlib import Path

import pytest
import yaml

from agents.utils.llm_config import (
    LLMConfig,
    _mask,
    _read_key_file,
    get_llm_config,
    set_api_key,
    set_model,
    show_config,
)


class TestReadKeyFile:
    """Tests for _read_key_file."""

    def test_reads_and_strips(self, tmp_path: Path) -> None:
        key_file = tmp_path / "key.txt"
        key_file.write_text("  sk-abc123  \n")
        assert _read_key_file(str(key_file)) == "sk-abc123"

    def test_expands_tilde(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        key_file = tmp_path / "key.txt"
        key_file.write_text("mykey")
        monkeypatch.setenv("HOME", str(tmp_path))
        assert _read_key_file("~/key.txt") == "mykey"

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            _read_key_file("/nonexistent/path/key.txt")


class TestGetLlmConfig:
    """Tests for get_llm_config."""

    def test_loads_valid_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        key_file = tmp_path / "key.txt"
        key_file.write_text("sk-test123")

        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({
            "model": "openai/gpt-4o",
            "api_keys": {"openai": str(key_file)},
            "temperature": 0.5,
        }))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))

        cfg = get_llm_config()
        assert cfg.model == "openai/gpt-4o"
        assert cfg.api_key == "sk-test123"
        assert cfg.temperature == 0.5

    def test_missing_config_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(tmp_path / "missing.yaml"))
        with pytest.raises(FileNotFoundError):
            get_llm_config()

    def test_missing_model_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_keys": {}}))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))
        with pytest.raises(ValueError, match="model"):
            get_llm_config()

    def test_missing_provider_key_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({
            "model": "anthropic/claude-sonnet-4-20250514",
            "api_keys": {"openai": "/some/path"},
        }))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))
        with pytest.raises(ValueError, match="anthropic"):
            get_llm_config()


class TestSetModel:
    """Tests for set_model."""

    def test_sets_model(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"model": "old/model"}))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))

        set_model("anthropic/claude-sonnet-4-20250514")

        with open(config_file) as f:
            data = yaml.safe_load(f)
        assert data["model"] == "anthropic/claude-sonnet-4-20250514"


class TestSetApiKey:
    """Tests for set_api_key."""

    def test_literal_key_creates_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"model": "openai/gpt-4o"}))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))
        monkeypatch.setenv("HOME", str(tmp_path))

        set_api_key("openai", "sk-literal-key-value")

        with open(config_file) as f:
            data = yaml.safe_load(f)
        key_path = data["api_keys"]["openai"]
        assert Path(key_path).read_text().strip() == "sk-literal-key-value"

    def test_file_path_stored_directly(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"model": "openai/gpt-4o"}))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))

        key_file = tmp_path / "mykey.txt"
        key_file.write_text("sk-from-file")

        set_api_key("openai", str(key_file))

        with open(config_file) as f:
            data = yaml.safe_load(f)
        assert data["api_keys"]["openai"] == str(key_file)


class TestMask:
    """Tests for _mask helper."""

    def test_masks_long_key(self) -> None:
        assert _mask("sk-abcdefgh1234") == "•" * 11 + "1234"

    def test_short_key_returns_dots(self) -> None:
        assert _mask("short") == ""

    def test_empty_key(self) -> None:
        assert _mask("") == ""


class TestShowConfig:
    """Tests for show_config."""

    def test_no_config_prints_message(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(tmp_path / "missing.yaml"))
        show_config()
        captured = capsys.readouterr()
        assert "No configuration found" in captured.out

    def test_shows_model_and_masked_key(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        key_file = tmp_path / "key.txt"
        key_file.write_text("sk-verysecretkey1234")

        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({
            "model": "openai/gpt-4o",
            "api_keys": {"openai": str(key_file)},
        }))
        monkeypatch.setenv("AISAFETY_CONFIG_PATH", str(config_file))

        show_config()
        captured = capsys.readouterr()
        assert "openai/gpt-4o" in captured.out
        assert "1234" in captured.out
        assert "verysecret" not in captured.out


class TestLLMConfigDataclass:
    """Tests for LLMConfig dataclass."""

    def test_defaults(self) -> None:
        cfg = LLMConfig(model="test/model", api_key="key")
        assert cfg.temperature is None

    def test_with_temperature(self) -> None:
        cfg = LLMConfig(model="test/model", api_key="key", temperature=0.3)
        assert cfg.temperature == 0.3
