"""
Tests for config_gen.py — MCP config generation, merge, create, skip, edge cases.

Covers:
  P0-03-1: merge-into-existing (preserves user servers, idempotent)
  P0-03-2: create-new, skip, manual print
  P0-03-3: invalid JSON + --force, unknown platform, empty detection, edge cases
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config_gen

MATRIX = config_gen.load_matrix()
SRC = Path(__file__).parent.parent / "src"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class TestMergeIntoExisting:
    """P0-03-1: merge-into-existing-json — preserve user servers, add gitnexus+cgc, idempotent."""

    def test_merge_preserves_existing_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = {"mcpServers": {"my-server": {"command": "node", "args": ["server.js"]}}}
            write_json(root / ".mcp.json", existing)

            status, msg = config_gen.write_mcp_config("claude-code", root)
            assert status == "merged"
            result = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            assert "my-server" in result["mcpServers"]
            assert "gitnexus" in result["mcpServers"]
            assert "codegraphcontext" in result["mcpServers"]

    def test_merge_idempotent_second_run_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = {"mcpServers": {}}
            write_json(root / ".mcp.json", existing)

            status1, _ = config_gen.write_mcp_config("claude-code", root)
            assert status1 == "merged"
            status2, _ = config_gen.write_mcp_config("claude-code", root)
            assert status2 == "skipped"

    def test_merge_idempotent_with_existing_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = {"mcpServers": {"my-server": {"command": "echo", "args": ["hello"]}}}
            write_json(root / ".mcp.json", existing)

            config_gen.write_mcp_config("claude-code", root)
            config_gen.write_mcp_config("claude-code", root)
            config_gen.write_mcp_config("claude-code", root)
            result = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            assert len(result["mcpServers"]) == 3

    def test_merge_with_cgc_path_substitution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = {"mcpServers": {}}
            write_json(root / ".mcp.json", existing)

            cgc_path = str(root / "cgc-install")
            config_gen.write_mcp_config("claude-code", root, cgc_path=cgc_path)
            result = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            assert result["mcpServers"]["codegraphcontext"]["cwd"] == cgc_path

    def test_merge_mcp_family_kilo_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kilo_dir = root / ".kilo"
            kilo_dir.mkdir()
            existing_config = {"mcp": {"existing-tool": {"type": "local", "command": ["echo"]}}}
            write_json(kilo_dir / "kilo.json", existing_config)

            status, _ = config_gen.write_mcp_config("kilo", root)
            assert status == "merged"
            result = json.loads((kilo_dir / "kilo.json").read_text(encoding="utf-8"))
            assert "existing-tool" in result["mcp"]
            assert "gitnexus" in result["mcp"]
            assert "codegraphcontext" in result["mcp"]
            assert result["mcp"]["gitnexus"]["type"] == "local"

    def test_merge_servers_family_copilot_vscode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vscode_dir = root / ".vscode"
            existing_config = {"servers": {"my-lsp": {"type": "stdio", "command": "lsp"}}}
            write_json(vscode_dir / "mcp.json", existing_config)

            status, _ = config_gen.write_mcp_config("copilot-vscode", root)
            assert status == "merged"
            result = json.loads((vscode_dir / "mcp.json").read_text(encoding="utf-8"))
            assert "my-lsp" in result["servers"]
            assert "gitnexus" in result["servers"]
            assert "codegraphcontext" in result["servers"]
            assert result["servers"]["gitnexus"]["type"] == "stdio"

    def test_merge_continue_standalone_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            continue_dir = root / ".continue"
            continue_dir.mkdir()
            user_config = Path(tmp) / "config.yaml"
            user_config.write_text("models: []", encoding="utf-8")

            status, _ = config_gen.write_mcp_config("continue", root)
            assert status == "created"
            result = json.loads(
                (continue_dir / "mcpServers" / "gitnexus-cgc.json").read_text(encoding="utf-8")
            )
            assert "mcpServers" in result
            assert "gitnexus" in result["mcpServers"]
            assert "codegraphcontext" in result["mcpServers"]
            assert user_config.read_text(encoding="utf-8") == "models: []"


class TestCreateAndSkip:
    """P0-03-2: create-new config, skip when configured, manual platforms."""

    def test_create_new_claude_code_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, _ = config_gen.write_mcp_config("claude-code", root)
            assert status == "created"
            assert (root / ".mcp.json").exists()
            result = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            assert result["mcpServers"]["gitnexus"]["command"] == "npx"
            assert result["mcpServers"]["codegraphcontext"]["command"] == "uv"

    def test_create_new_kilo_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, _ = config_gen.write_mcp_config("kilo", root)
            assert status == "created"
            assert (root / ".kilo" / "kilo.json").exists()
            result = json.loads((root / ".kilo" / "kilo.json").read_text(encoding="utf-8"))
            assert result["mcp"]["gitnexus"]["type"] == "local"
            assert result["mcp"]["codegraphcontext"]["type"] == "local"

    def test_create_new_cursor_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, _ = config_gen.write_mcp_config("cursor", root)
            assert status == "created"
            assert (root / ".cursor" / "mcp.json").exists()
            result = json.loads((root / ".cursor" / "mcp.json").read_text(encoding="utf-8"))
            assert "gitnexus" in result["mcpServers"]
            assert "codegraphcontext" in result["mcpServers"]

    def test_create_new_copilot_vscode_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, _ = config_gen.write_mcp_config("copilot-vscode", root)
            assert status == "created"
            result = json.loads((root / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
            assert result["servers"]["gitnexus"]["type"] == "stdio"

    def test_create_new_opencode_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, _ = config_gen.write_mcp_config("opencode", root)
            assert status == "created"
            result = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
            assert result["mcp"]["gitnexus"]["type"] == "local"

    def test_skip_when_all_servers_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            new_config = config_gen.generate_mcp_config("claude-code")
            write_json(root / ".mcp.json", new_config)

            status, _ = config_gen.write_mcp_config("claude-code", root)
            assert status == "skipped"

    def test_skip_when_all_servers_present_plus_extras(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            new_config = config_gen.generate_mcp_config("claude-code")
            new_config["mcpServers"]["extra-server"] = {"command": "extra"}
            write_json(root / ".mcp.json", new_config)

            status, _ = config_gen.write_mcp_config("claude-code", root)
            assert status == "skipped"

    def test_merge_when_partial_config_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial = {"mcpServers": {"gitnexus": {"command": "npx", "args": ["-y", "gitnexus@latest", "mcp"]}}}
            write_json(root / ".mcp.json", partial)

            status, _ = config_gen.write_mcp_config("claude-code", root)
            assert status == "merged"
            result = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            assert "codegraphcontext" in result["mcpServers"]
            assert "gitnexus" in result["mcpServers"]

    def test_manual_windsurf_returns_manual_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, msg = config_gen.write_mcp_config("windsurf", root)
            assert status == "manual"
            assert "Paste into" in msg
            assert "gitnexus" in msg

    def test_manual_augment_returns_manual_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, msg = config_gen.write_mcp_config("augment", root)
            assert status == "manual"
            assert "Paste into" in msg


class TestEdgeCases:
    """P0-03-3: invalid JSON, unknown platform, empty detection, force, print mode."""

    def test_invalid_json_existing_file_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mcp.json").write_text("not valid json {{{", encoding="utf-8")

            status, msg = config_gen.write_mcp_config("claude-code", root)
            assert status == "error"
            assert "not valid JSON" in msg

    def test_invalid_json_with_force_backs_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mcp.json").write_text("not valid json {{{", encoding="utf-8")

            status, msg = config_gen.write_mcp_config("claude-code", root, force=True)
            assert status == "created"
            backup = root / ".mcp.json.bak"
            assert backup.exists()
            assert backup.read_text(encoding="utf-8") == "not valid json {{{"
            result = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            assert "gitnexus" in result["mcpServers"]

    def test_unknown_platform_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, msg = config_gen.write_mcp_config("nonexistent-platform", root)
            assert status == "error"
            assert "Unknown platform" in msg

    def test_valid_platform_validation(self):
        valid, err = config_gen.validate_platform("kilo")
        assert valid
        assert err == ""

        valid, err = config_gen.validate_platform("cursor")
        assert valid

        valid, err = config_gen.validate_platform("invalid")
        assert not valid
        assert "Unknown platform" in err

    def test_detection_on_empty_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            detected = config_gen.detect_platforms(root)
            assert detected == []

    def test_detection_kilo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".kilo").mkdir()
            detected = config_gen.detect_platforms(root)
            assert "kilo" in detected

    def test_detection_kilo_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "kilo.json").write_text("{}", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "kilo" in detected

    def test_detection_claude_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mcp.json").write_text("{}", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "claude-code" in detected

    def test_detection_claude_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("# Project", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "claude-code" in detected

    def test_detection_cursor_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".cursor").mkdir()
            detected = config_gen.detect_platforms(root)
            assert "cursor" in detected

    def test_detection_cursorrules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".cursorrules").write_text("# rules", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "cursor" in detected

    def test_detection_multiple_platforms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".kilo").mkdir()
            (root / ".cursor").mkdir()
            (root / "CLAUDE.md").write_text("# Project", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "kilo" in detected
            assert "cursor" in detected
            assert "claude-code" in detected

    def test_detection_cline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".clinerules").write_text("# rules", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "cline" in detected

    def test_detection_roo_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".roorules").write_text("# rules", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "roo-code" in detected

    def test_detection_continue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.yaml").write_text("models: []", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "continue" in detected

    def test_detection_copilot_vscode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".vscode").mkdir()
            (root / ".vscode" / "mcp.json").write_text("{}", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "copilot-vscode" in detected

    def test_detection_windsurf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".windsurf").mkdir()
            detected = config_gen.detect_platforms(root)
            assert "windsurf" in detected

    def test_detection_opencode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "opencode.json").write_text("{}", encoding="utf-8")
            detected = config_gen.detect_platforms(root)
            assert "opencode" in detected


class TestGenerateMCPConfig:
    def test_generate_claude_code_mcpServers_format(self):
        config = config_gen.generate_mcp_config("claude-code")
        assert "mcpServers" in config
        assert config["mcpServers"]["gitnexus"]["command"] == "npx"
        assert config["mcpServers"]["gitnexus"]["args"] == ["-y", "gitnexus@latest", "mcp"]
        assert config["mcpServers"]["codegraphcontext"]["command"] == "uv"
        assert config["mcpServers"]["codegraphcontext"]["args"] == ["run", "cgc", "mcp"]

    def test_generate_kilo_mcp_format(self):
        config = config_gen.generate_mcp_config("kilo")
        assert "mcp" in config
        assert config["mcp"]["gitnexus"]["type"] == "local"
        assert isinstance(config["mcp"]["gitnexus"]["command"], list)
        assert config["mcp"]["gitnexus"]["command"] == ["npx", "-y", "gitnexus@latest", "mcp"]

    def test_generate_copilot_vscode_servers_format(self):
        config = config_gen.generate_mcp_config("copilot-vscode")
        assert "servers" in config
        assert config["servers"]["gitnexus"]["type"] == "stdio"
        assert config["servers"]["codegraphcontext"]["type"] == "stdio"

    def test_generate_unknown_platform_returns_none(self):
        config = config_gen.generate_mcp_config("nonexistent")
        assert config is None

    def test_generate_with_cgc_path_sets_workdir_kilo(self):
        config = config_gen.generate_mcp_config("kilo", cgc_path="/path/to/cgc")
        assert config["mcp"]["codegraphcontext"]["workdir"] == "/path/to/cgc"

    def test_generate_with_cgc_path_sets_cwd_claude(self):
        config = config_gen.generate_mcp_config("claude-code", cgc_path="/path/to/cgc")
        assert config["mcpServers"]["codegraphcontext"]["cwd"] == "/path/to/cgc"

    def test_generate_all_supported_platforms(self):
        for pid in MATRIX["platforms"]:
            config = config_gen.generate_mcp_config(pid)
            assert config is not None


class TestMergeIntoExistingFunction:
    def test_merge_adds_new_server_to_empty(self):
        existing = {"mcpServers": {}}
        new = {"mcpServers": {"gitnexus": {"command": "npx"}}}
        result = config_gen.merge_into_existing(existing, new)
        assert result["mcpServers"]["gitnexus"] == {"command": "npx"}

    def test_merge_preserves_existing_server(self):
        existing = {"mcpServers": {"my-server": {"command": "echo"}}}
        new = {"mcpServers": {"gitnexus": {"command": "npx"}}}
        result = config_gen.merge_into_existing(existing, new)
        assert result["mcpServers"]["my-server"] == {"command": "echo"}
        assert result["mcpServers"]["gitnexus"] == {"command": "npx"}

    def test_merge_does_not_overwrite_existing(self):
        existing = {"mcpServers": {"gitnexus": {"command": "custom"}}}
        new = {"mcpServers": {"gitnexus": {"command": "npx"}}}
        result = config_gen.merge_into_existing(existing, new)
        assert result["mcpServers"]["gitnexus"] == {"command": "custom"}

    def test_merge_adds_wrapper_key_if_missing(self):
        existing = {}
        new = {"mcpServers": {"gitnexus": {"command": "npx"}}}
        result = config_gen.merge_into_existing(existing, new)
        assert "mcpServers" in result
        assert result["mcpServers"]["gitnexus"] == {"command": "npx"}


class TestCLIIntegration:
    def test_cli_list_platforms(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--list-platforms"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "kilo" in result.stdout
        assert "cursor" in result.stdout
        assert "windsurf" in result.stdout

    def test_cli_detect_on_this_project(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--detect", "--project-path", str(Path(__file__).parent.parent)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "kilo" in result.stdout

    def test_cli_unknown_platform_exits_1(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--platform", "invalid"],
            capture_output=True, text=True,
        )
        assert result.returncode == 1

    def test_cli_missing_project_path(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--detect", "--project-path", "/nonexistent/path"],
            capture_output=True, text=True,
        )
        assert result.returncode == 1

    def test_cli_print_mode_claude(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--platform", "claude-code", "--print"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "mcpServers" in result.stdout
        assert "gitnexus" in result.stdout
        assert "codegraphcontext" in result.stdout

    def test_cli_print_mode_windsurf(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--platform", "windsurf", "--print"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "gitnexus" in result.stdout

    def test_cli_print_with_cgc_path(self):
        import subprocess
        from pathlib import Path as P

        test_path = str(P("/test/path").resolve())
        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py"), "--platform", "kilo", "--print", "--cgc-path", test_path],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "workdir" in result.stdout
        assert test_path.replace("\\", "\\\\") in result.stdout

    def test_cli_detect_empty_project_exits_1(self):
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["uv", "run", "python", str(SRC / "config_gen.py"), "--detect", "--project-path", tmp],
                capture_output=True, text=True,
            )
            assert result.returncode == 1
            assert "No supported platforms detected" in result.stdout

    def test_cli_no_args_shows_help(self):
        import subprocess

        result = subprocess.run(
            ["uv", "run", "python", str(SRC / "config_gen.py")],
            capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "usage" in result.stdout.lower() or "arguments" in result.stdout.lower()