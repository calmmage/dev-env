# GitHub Repository Management Tools

## 1. Git Hooks Manager
Tool to check and setup git hooks across repositories
- [ ] Create discover_local_projects in shared lib.py
- [ ] Implement check for vulture and other tools in git hooks
- [ ] Add functionality to setup missing git hooks
- [ ] Add configuration for which hooks should be checked/added

## 2. PyProject.toml Standardizer
Tool to standardize pyproject.toml files across repositories
- [ ] Create tool to parse existing pyproject.toml
- [ ] Implement template format checker with 5 groups:
  - main
  - dev
  - extras
  - tests
  - docs
- [ ] Add functionality to reorganize dependencies
- [ ] Add logic to move most dependencies to extras by default
- [ ] Add backup functionality before making changes

## 3. CodeCov Setup Checker
Tool to verify CodeCov configuration
- [ ] Check pyproject.toml for codecov settings
- [ ] Verify GitHub Actions workflow file for codecov
- [ ] Add missing codecov configurations where needed
- [ ] Generate coverage reports configuration

## Shared Infrastructure
- [ ] Create lib.py with shared utilities
- [ ] Implement discover_local_projects function
- [ ] Add logging and error handling
- [ ] Create common configuration management 