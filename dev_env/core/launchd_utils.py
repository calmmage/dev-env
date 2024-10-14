from pathlib import Path
import os

launchd_plist_template = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>{job_name}</string>
	<key>ProgramArguments</key>
	<array>
		<string>{executable}</string>
		<string>{script_path}</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>StandardErrorPath</key>
	<string>{stderr_path}</string>
	<key>StandardOutPath</key>
	<string>{stdout_path}</string>
</dict>
</plist>
"""

# option 1: zsh
executable_sh = "/bin/zsh"
# script_path = "some_script.sh"

# option 2: python
executable_py = "~/.calmmage/dev_env/venv/bin/python"  # do i need to activate?

# script_path = "some_script.py"


def get_launchd_plist(script, job_name=None, stderr_path=None, stdout_path=None, executable=None):
    script = Path(script)
    job_name = job_name or script.name
    stderr_path = stderr_path or f"/tmp/{job_name}.stderr"
    stdout_path = stdout_path or f"/tmp/{job_name}.stdout"
    if executable is None:
        if script.suffix == ".sh":
            executable = executable_sh
        elif script.suffix == ".py":
            executable = Path(executable_py).expanduser()
        else:
            raise ValueError("Unknown script type and executable not provided")

    return launchd_plist_template.format(
        job_name=job_name,
        executable=str(executable),
        script_path=str(script),
        stderr_path=stderr_path,
        stdout_path=stdout_path,
    )


launchd_plist_dir = Path("~/Library/LaunchAgents").expanduser()

if __name__ == "__main__":
    print(os.getenv("CALMMAGE_DEV_ENV_PATH"))  # returns None - doesn't work without source.

    for k in launchd_plist_dir.glob("*"):
        print(k)
