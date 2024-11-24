Main things I'm trying to do:
- display relevant info about projects
  - github name, if different
  - github org, if not personal
  - date, if interesting
- improve project sorting algorithms / rules
  - based on date
  - hardcode more rules
- do actual sorting
  - arrive at a state where I'm happy with the result (key projects not removed)
  - move dirs around (with confirmation?)

something else?
- merge with clone_all_projects script

Refactoings
- [ ] return the reason for group selection together with ... group
- [ ] change everything to return instance of Group
- [ ] Add a new 'destination' class or something
  - dict? group_name -> dir? configurable somehow? 
- [ ] Resolve python config warnings about types of fields (config.py, BaseSettings)

- [x] print project date info 
  - if edited > 1 month ago -> print that
  - if edited recently but created long ago -> print both
  - if edited recently and created recently -> print only when edited
- [ ] Add a flag to show 1) date or 2) reason for group selection 
  - in brackets to the right of the project
- [ ] Sort projects by recency within groups.

- add new tech - github info
  - [ ] merge with clone_all_projects script
  - [ ] init github client
  - [ ] see github remote for the repo
  - [ ] if remote project name 
  - [ ] see all remote projects
    - configure which remote sources (orgs) to use
  - [ ] merge remote and local lists 
    - [ ] handle "a project that is cloned several times" scenario
    - [ ] handle "a project that is cloned under a different name" scenario. Ask user:
      - rename local
      - rename remote? 
      - keep as is

Plan:




- [ ] handle 'clone from start' scenario
  - [ ] use old 'clone_all_projects' script - deduplicate and reuse
    - copy code to project arranger
    - use in the script to reproduce behavior
    - merge old and new code to remove duplicate functionality

- [ ] handle 'already cloned, now sort'
  - [ ] non-dry-run
    -  [ ] move projects
    -  [ ] projects that are to be deleted (ignored but present on disk) - move to 'to_remove' folder
  - debug / research tools
    - a) view project sizes
      - notice big ignored projects
      - notice small non-ignored projects (except recent) 
    - b) view project dates


- [ ] Better project sorting
  - [ ] Anomaly decetion - analysis / research tools
  - [ ] make it so secondary projects can't be ignored (if ignored -> move to archive instead?)
    - or not? 1) templates - yes 2) cool - no (will distract me?)
  - [ ] automatic sorting: 
    - sticky groups (don't change groups for no reason)
      - if recently modified -> stays in 'actual' even if not hardcoded
    - by date -> 
      - if created this month - stays in experiments
      - if before
        - if modified this month -> actual
        - if before
          - if big -> archive
          - if not -> ignore (to_remove)
  - [ ] auto-commit? warn? Block? 
    - [ ] 1) before removing
    - [ ] 2) before moving? 


- [ ] ai features
  - ai categorization (to which primary / secondary to move?)
  - ai summary of the project
  - ai ... 








# Done
- [x] fix 'ignore' and 'ignored' issue
- [ ] handle 'already cloned, now sort'
  - [x] determine current group based on path
  - [x] add two view options:
    - show only changes
    - show all

- [x] primary and secondary groups - sort, print
- [x] print group size (in brackets?)
  - [x] make cached?
  - [x] make cached all properties - last modified