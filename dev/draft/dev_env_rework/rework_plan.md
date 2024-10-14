# Broad rework plan

1) abandon class paradygm - we don't have a state so we don't need a class. Rework to a collection of functions,scripts, tools and modules.
2) update project folders structure
3) add a readme to setup and to use
4) implement scripts to handle daily and monthly tasks
5) set up all the scripts to launchd
6) bonus: set up raycast stuff.

# Detailed rework plan

## 1) abandon class paradygm - we don't have a state so we don't need a class. Rework to a collection of functions,scripts, tools and modules.

Essentially: 
rework each class into a folder:
- modules with utils
- settings.py
- scripts go into tools folder

## 2) update project folders structure

~/work/ (env var, default ~/work/)
├── seasonal/

├── experiments/ (all new) 
├── projects/ (shortlist + actual)
├── archive/ (all / all old)

├── contexts/


seasonal/
├── yy-mm-mmm
├── ── dev-yy-mm (git, poetry)
├── ── ── draft [THIS IS MAIN ENTRY POINT]
├── ── ── wip
├── ── ── paused
├── ──p1 (git, poetry)
├── ──p2 ...
├── yy-mm-mmm
├── latest

~/contexts

├── libs
├── dev
├── templates

---