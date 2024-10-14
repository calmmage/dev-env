import pytest
from pathlib import Path
from dev_env.core.launchd_utils import get_launchd_plist


@pytest.fixture
def temp_script(tmp_path):
    return tmp_path / "test_script.py"


def test_get_launchd_plist_python(temp_script):
    plist = get_launchd_plist(temp_script)

    assert "<key>Label</key>" in plist
    assert "<string>test_script.py</string>" in plist
    assert "<key>ProgramArguments</key>" in plist
    assert "calmmage/dev_env/venv/bin/python</string>" in plist
    assert f"<string>{temp_script}</string>" in plist
    assert "<key>RunAtLoad</key>" in plist
    assert "<true/>" in plist
    assert "<key>StandardErrorPath</key>" in plist
    assert "<string>/tmp/test_script.py.stderr</string>" in plist
    assert "<key>StandardOutPath</key>" in plist
    assert "<string>/tmp/test_script.py.stdout</string>" in plist


def test_get_launchd_plist_shell(temp_script):
    shell_script = temp_script.with_suffix(".sh")
    plist = get_launchd_plist(shell_script)

    assert "<string>/bin/zsh</string>" in plist
    assert f"<string>{shell_script}</string>" in plist


def test_get_launchd_plist_custom_job_name(temp_script):
    plist = get_launchd_plist(temp_script, job_name="custom_job")

    assert "<string>custom_job</string>" in plist
    assert "<string>/tmp/custom_job.stderr</string>" in plist
    assert "<string>/tmp/custom_job.stdout</string>" in plist


def test_get_launchd_plist_custom_paths(temp_script):
    stderr_path = "/custom/path/error.log"
    stdout_path = "/custom/path/output.log"
    plist = get_launchd_plist(temp_script, stderr_path=stderr_path, stdout_path=stdout_path)

    assert f"<string>{stderr_path}</string>" in plist
    assert f"<string>{stdout_path}</string>" in plist


@pytest.mark.parametrize("script_name", ["test.py", "test.sh"])
def test_get_launchd_plist_executable(temp_script, script_name):
    script = temp_script.with_name(script_name)
    plist = get_launchd_plist(script)

    if script_name.endswith(".py"):
        assert "calmmage/dev_env/venv/bin/python</string>" in plist
    elif script_name.endswith(".sh"):
        assert "<string>/bin/zsh</string>" in plist


def test_get_launchd_plist_expands_user_path():
    home_dir = Path.home()
    script = Path("~/test_script.py").expanduser()
    plist = get_launchd_plist(script)

    assert str(home_dir) in plist
