- [x] check if repo name in pyproject.toml is still 'project_name'
  - [ ] see if there's still a folder 'project_name' in the root
  -  if yes - ask user the project name and change it in pyproject.toml and in the folder name
- [ ] use project name to fill all .pre-commit-config.yaml values where it is required.
- [ ] remove duplicate --exclude flags in vulture pre-commit


- [ ] line 1-7 (nbstripout removal): Add a new function `_add_nbstripout(repo_path: Path)` with the original nbstripout config and call it in `_add_precommit()`

- [ ] line 8-14 (black config): Fix `_add_black()` function to use the original black config instead of black-jupyter:
  ```python
  content = dedent(
      """
      - repo: https://github.com/psf/black
        rev: 24.2.0
        hooks:
          - id: black
            args: [ --line-length=100 ]
            name: black
            description: "Black: The uncompromising Python code formatter"
      """
  )
  ```

- [x] line 23 (vulture exclude): Remove unnecessary exclude in `_add_vulture()` function:
  ```python
  args: [
      "--min-confidence", "80",
      "{source_dir_name}"  # project_name
  ]
  ```

- [ ] line 43 (flake8 path): Add back file path restriction in `_add_flake8()`:
  ```python
  files: ^{source_dir_name}/.*\.py$
  ```

- [ ] line 64 (isort path): Add back file path restriction in `_add_isort()`:
  ```python
  files: ^.*\.py$
  ```

- [ ] line 44 (exclude pattern): Add back .venv to exclusions in `_add_flake8()`:
  ```python
  "--exclude=.venv,.git,__pycache__,build,dist",
  ```