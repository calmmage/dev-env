# Project Manager Implementation Checklist

## Progress Tracking
- [x] Initial Project Setup
  - [x] Basic file structure
  - [x] Core configuration files
  - [x] Destination concept defined

- [ ] Code Migration from Project Arranger
  - [x] Move Destination concept to shared utils
  - [ ] Port GitHub integration utils
  - [ ] Port project discovery logic
  - [ ] Adapt project sorting algorithms
  - [ ] Update project arranger to use shared code

## Core Scenarios
- [ ] New Project
  - [ ] Config Integration
    - [ ] Create shared ProjectManagerConfig class
    - [ ] Add Destinations config subclass
    - [ ] Add shared utils config subclass
    - [ ] Load from yaml
  - [ ] Name Processing
    - [ ] Prompt if no name provided
    - [ ] Validate with AI (query_gpt)
    - [ ] Generate concise name if needed
    - [ ] Check GitHub conflicts
  - [ ] Template Selection
    - [ ] Fuzzy-match template name
    - [ ] Use default if none provided
  - [ ] Project Creation
    - [ ] Create GitHub repo from template
    - [ ] Clone to Experiments destination
    - [ ] Copy path to clipboard
    - [ ] Print confirmation
- [ ] New Mini Project
  - [ ] init: list all points from the user scenario file
- [ ] New Todo
  - [ ] init: list all points from the user scenario file
- [ ] New Feature
  - [ ] init: list all points from the user scenario file
- [ ] Destinations:
  - [ ] list all points from the user scenario file

## Features
- [ ] GitHub Template Name Parsing and Integration
  - [ ] init: list all points from the user scenario file
- [ ] Nix Command Aliases
  - [ ] init: list all points from the user scenario file
- [ ] Project Auto-detection
  - [ ] init: list all points from the user scenario file
- [ ] Timed Confirmation Defaults
  - [ ] init: list all points from the user scenario file
- [ ] Project Search
  - [ ] init: list all points from the user scenario file

## Sanity Checks & Auto-jobs
- [ ] Job Timing System
  - [ ] init: list all points from the user scenario file
- [ ] Project Discovery Cache
  - [ ] init: list all points from the user scenario file
- [ ] Seasonal Folder Management
  - [ ] init: list all points from the user scenario file
