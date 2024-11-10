{ config, lib, pkgs, ... }:

{
  imports = [
    ./aliases
    ./scripts
    # ./config
  ];

  # Define help message that was previously in zshrc
  programs.zsh.initExtra = ''
    export HELP="This is a help message by Petr Lavrov, on Jan 2024

    calmlib aliases:
    np, new_project, pm, project_manager
    cdl, cds, cdp - cd to latest, structured and playground
    cd1, 2, 3 - same
    cdr, lsr, cdf - fuzzy match cd and ls

    personal aliases:
    hetzner - ssh to hetzner server

    fp - find project (find dir / file name in ~/work)
    find_ \$text \$path - find text in file (grep all text instances in dir)
    mva - move the dir to new location and leave a symlink instead

    pro cli libs:
    ghc / gh copilot - github copilot cli
    aie - gh copilot explain
    ais - gh copilot suggest

    tree
    awk, grep"
  '';
} 