from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
from pydantic_settings import BaseSettings
from dev_env.core.repo_discovery import discover_local_projects
import subprocess
import toml
import yaml

class QualityThresholds(BaseSettings):
    flake8_max_violations: int = 10  # Allow up to 10 style violations
    vulture_min_confidence: int = 80
    coverage_min_percent: float = 70.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class GitHooksConfig(BaseSettings):
    default_hooks: Dict[str, Dict] = {
        "nbstripout": {
            "repo": "https://github.com/kynan/nbstripout",
            "rev": "0.5.0",
            "hooks": [{"id": "nbstripout", "files": r"\.ipynb$"}]
        },
        "quality-report": {
            "repo": "local",
            "hooks": [{
                "id": "code-quality-report",
                "name": "Code Quality Report",
                "entry": "python -m tools.git_hooks_manager.quality_report",
                "language": "system",
                "always_run": True,
                "pass_filenames": False,
                "stages": ["commit"]
            }]
        }
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def create_quality_report_script(repo_path: Path, thresholds: QualityThresholds) -> None:
    """Create a script that runs quality checks and generates a report."""
    script_dir = repo_path / "tools" / "git_hooks_manager"
    script_dir.mkdir(parents=True, exist_ok=True)
    
    script_content = f"""
import subprocess
from pathlib import Path
from loguru import logger

def run_flake8():
    try:
        result = subprocess.run(["flake8", "."], capture_output=True, text=True)
        violations = len(result.stdout.splitlines())
        return violations <= {thresholds.flake8_max_violations}, result.stdout
    except Exception as e:
        logger.error(f"Flake8 check failed: {{e}}")
        return True, "Flake8 check failed"

def run_vulture():
    try:
        result = subprocess.run(
            ["vulture", ".", f"--min-confidence={thresholds.vulture_min_confidence}"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        logger.error(f"Vulture check failed: {{e}}")
        return True, "Vulture check failed"

def run_coverage():
    try:
        result = subprocess.run(["coverage", "report"], capture_output=True, text=True)
        coverage = float(result.stdout.splitlines()[-1].split()[-1].rstrip('%'))
        return coverage >= {thresholds.coverage_min_percent}, result.stdout
    except Exception as e:
        logger.error(f"Coverage check failed: {{e}}")
        return True, "Coverage check failed"

def main():
    print("\\n=== Code Quality Report ===\\n")
    
    flake8_pass, flake8_output = run_flake8()
    vulture_pass, vulture_output = run_vulture()
    coverage_pass, coverage_output = run_coverage()
    
    print("Flake8 Report:")
    print(flake8_output)
    print("\\nVulture Report:")
    print(vulture_output)
    print("\\nCoverage Report:")
    print(coverage_output)
    
    # Return 0 (success) even if checks fail - we just want the report
    return 0

if __name__ == "__main__":
    exit(main())
"""
    
    script_path = script_dir / "quality_report.py"
    script_path.write_text(script_content)

def setup_pre_commit_config(repo_path: Path, config: GitHooksConfig) -> None:
    """Create or update .pre-commit-config.yaml with our hooks."""
    config_path = repo_path / ".pre-commit-config.yaml"
    
    # Load existing config or create new
    if config_path.exists():
        current_config = yaml.safe_load(config_path.read_text())
    else:
        current_config = {"repos": []}
    
    # Update/add our hooks
    for hook_config in config.default_hooks.values():
        if hook_config not in current_config["repos"]:
            current_config["repos"].append(hook_config)
    
    # Write updated config
    config_path.write_text(yaml.dump(current_config, sort_keys=False))
    logger.info(f"Updated pre-commit config in {repo_path}")

def check_pre_commit_config(repo_path: Path) -> bool:
    """Check if pre-commit config exists in the repository."""
    config_path = repo_path / ".pre-commit-config.yaml"
    return config_path.exists()

def check_pre_commit_installed(repo_path: Path) -> bool:
    """Check if pre-commit hooks are installed in .git/hooks."""
    pre_commit_hook = repo_path / ".git" / "hooks" / "pre-commit"
    return pre_commit_hook.exists() and "pre-commit" in pre_commit_hook.read_text()

def setup_pre_commit(repo_path: Path) -> None:
    """Install pre-commit in the repository."""
    try:
        subprocess.run(["pre-commit", "install"], cwd=repo_path, check=True)
        logger.info(f"Installed pre-commit hooks in {repo_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install pre-commit in {repo_path}: {e}")

def update_pyproject_toml(repo_path: Path) -> None:
    """Add required dev dependencies to pyproject.toml."""
    pyproject_path = repo_path / "pyproject.toml"
    if not pyproject_path.exists():
        logger.warning(f"No pyproject.toml found in {repo_path}")
        return
    
    try:
        config = toml.load(pyproject_path)
        
        # Ensure tool.poetry section exists
        if "tool" not in config:
            config["tool"] = {}
        if "poetry" not in config["tool"]:
            config["tool"]["poetry"] = {}
            
        # Add dev dependencies if they don't exist
        dev_deps = config["tool"]["poetry"].get("group", {}).get("dev", {}).get("dependencies", {})
        required_deps = {
            "pre-commit": "^3.5.0",
            "nbstripout": "^0.6.1",
            "vulture": "^2.10"
        }
        
        dev_deps.update(required_deps)
        config["tool"]["poetry"]["group"]["dev"]["dependencies"] = dev_deps
        
        # Write back to file
        with open(pyproject_path, 'w') as f:
            toml.dump(config, f)
        logger.info(f"Updated dev dependencies in {pyproject_path}")
        
    except Exception as e:
        logger.error(f"Failed to update pyproject.toml in {repo_path}: {e}")

def main():
    config = GitHooksConfig()
    thresholds = QualityThresholds()
    repos = discover_local_projects()
    
    for repo_path in repos:
        logger.info(f"Setting up quality checks in {repo_path}")
        
        # Create quality report script
        create_quality_report_script(repo_path, thresholds)
        
        # Update pre-commit config
        setup_pre_commit_config(repo_path, config)
        
        # Install pre-commit if needed
        if not check_pre_commit_installed(repo_path):
            setup_pre_commit(repo_path)

if __name__ == "__main__":
    main()
