"""Tests for .env discovery in `cdisc_mcp.server`.

Over stdio the server is launched by the MCP client, so its working directory is
the *client's* project. If any existing `.env` counted as a hit, an unrelated
project file would shadow `~/.cdisc-mcp/.env` and the server would come up
without credentials.
"""

from cdisc_mcp.server import _defines_cdisc_settings, _load_env_file, _pick_env_file


def _write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class TestPickEnvFile:
    def test_unrelated_env_in_cwd_does_not_stop_the_search(self, tmp_path):
        cwd = _write(tmp_path / "cwd" / ".env", "DATABASE_URL=postgres://x\nDEBUG=1\n")
        home = _write(tmp_path / "home" / ".cdisc-mcp" / ".env", "CDISC_API_KEY=from-home\n")

        assert _pick_env_file([cwd, home]) == home

    def test_first_file_declaring_cdisc_settings_wins(self, tmp_path):
        cwd = _write(tmp_path / "cwd" / ".env", "CDISC_API_KEY=from-cwd\n")
        home = _write(tmp_path / "home" / ".cdisc-mcp" / ".env", "CDISC_API_KEY=from-home\n")

        assert _pick_env_file([cwd, home]) == cwd

    def test_non_secret_cdisc_setting_counts_as_a_hit(self, tmp_path):
        # base_url / cache config without a key still identifies a CDISC env file.
        cwd = _write(tmp_path / "cwd" / ".env", "DATABASE_URL=postgres://x\n")
        project = _write(tmp_path / "proj" / ".env", "CDISC_BASE_URL=https://example.invalid/api\n")

        assert _pick_env_file([cwd, project]) == project

    def test_returns_none_when_no_file_owns_the_config(self, tmp_path):
        cwd = _write(tmp_path / "cwd" / ".env", "DEBUG=1\n")

        assert _pick_env_file([cwd, tmp_path / "missing" / ".env"]) is None

    def test_directory_named_env_is_skipped(self, tmp_path):
        (tmp_path / "cwd" / ".env").mkdir(parents=True)
        home = _write(tmp_path / "home" / ".cdisc-mcp" / ".env", "CDISC_API_KEY=from-home\n")

        assert _pick_env_file([tmp_path / "cwd" / ".env", home]) == home

    def test_unreadable_file_is_skipped_not_fatal(self, tmp_path, monkeypatch):
        cwd = _write(tmp_path / "cwd" / ".env", "CDISC_API_KEY=from-cwd\n")
        home = _write(tmp_path / "home" / ".cdisc-mcp" / ".env", "CDISC_API_KEY=from-home\n")

        real_is_file = type(cwd).is_file

        def boom(self):
            if self == cwd:
                raise OSError("permission denied")
            return real_is_file(self)

        monkeypatch.setattr(type(cwd), "is_file", boom)
        assert _pick_env_file([cwd, home]) == home


class TestDefinesCdiscSettings:
    def test_detects_prefixed_keys_only(self, tmp_path):
        assert _defines_cdisc_settings(_write(tmp_path / "a" / ".env", "CDISC_API_KEY=k\n"))
        assert not _defines_cdisc_settings(_write(tmp_path / "b" / ".env", "API_KEY=k\n"))
        assert not _defines_cdisc_settings(tmp_path / "nope" / ".env")

    def test_recognises_non_utf8_files(self, tmp_path):
        """Detection reads bytes; a GBK-commented file must not be skipped."""
        path = tmp_path / "gbk" / ".env"
        path.parent.mkdir(parents=True)
        path.write_bytes("# 中文注释：CDISC 配置\nCDISC_API_KEY=k\n".encode("gbk"))
        assert _defines_cdisc_settings(path)

    def test_comments_and_substrings_are_not_declarations(self, tmp_path):
        assert not _defines_cdisc_settings(
            _write(tmp_path / "c" / ".env", "# CDISC_API_KEY=doc only\nOTHER=1\n")
        )
        assert not _defines_cdisc_settings(_write(tmp_path / "d" / ".env", "myCDISC_API_KEY=k\n"))
        assert _defines_cdisc_settings(_write(tmp_path / "e" / ".env", "  export CDISC_BASE_URL=x\n"))


class TestLoadEnvFile:
    def test_loads_the_selected_file(self, tmp_path, monkeypatch):
        cwd = _write(tmp_path / "cwd" / ".env", "UNRELATED=1\n")
        home = _write(tmp_path / "home" / ".cdisc-mcp" / ".env", "CDISC_API_KEY=loaded-key\n")
        picked = []

        monkeypatch.chdir(cwd.parent)
        monkeypatch.delenv("CDISC_API_KEY", raising=False)
        monkeypatch.setattr(
            "cdisc_mcp.server._pick_env_file",
            lambda candidates=None: (picked.append(candidates), home)[1],
        )

        _load_env_file()
        assert picked == [None], "default candidate list must be used when not supplied"

        from cdisc_mcp.config import CDISCConfig

        assert CDISCConfig.from_env().api_key == "loaded-key"

    def test_noop_without_any_env_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CDISC_API_KEY", raising=False)
        monkeypatch.setattr("cdisc_mcp.server._pick_env_file", lambda candidates=None: None)

        _load_env_file()  # must not raise
