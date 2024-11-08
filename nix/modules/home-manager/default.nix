{ pkgs, lib, ... }:

let
  dockApps = [
    "/Applications/Raycast.app"
    # Add more applications here, for example:
    # "/Applications/Firefox.app"
    # "/System/Applications/Messages.app"
    "/Applications/Slack.app"
    # "/Applications/Visual Studio Code.app"
  ];
in
{
  # Don't change this when you change package input. Leave it alone.
  home.stateVersion = "23.11";
  # specify my home-manager configs
  home.packages = with pkgs; [
    curl
    less
    # slack # via brew
    direnv
    oh-my-zsh
    docker # cli docker 
    gh  # Adding GitHub CLI via Nix
    zsh-powerlevel10k
    nixfmt-classic
    awscli2
    devenv
    cachix
    postman
    pgbadger
    inetutils
    git-remote-codecommit
    gitflow
    teams
    shntool
    # postgresql_14
    # pgadmin4-desktopmode
    devcontainer
    tree
    age
    cmake  
    dlib   # Add dlib
    # poetry # via brew
    # ripgrep # via brew
  ];

  home.sessionVariables = {
    PAGER = "less";
    CLICOLOR = 1;
    EDITOR = "subl";
    PATH = "$PATH:$HOME/bin";
  };

  programs = {
    bat = {
      enable = true;
      config.theme = "TwoDark";
    };
    git = {
      enable = true;
      extraConfig = {
        init.defaultBranch = "master";
        user.name = "Petr Lavrov";
        merge.tool = "opendiff";
        diff.tool = "opendiff";
        difftool.prompt = false;
        difftool."opendiff" =
          ''cmd = /usr/bin/opendiff "$LOCAL" "$REMOTE" -merge "$MERGED" | cat'';
      };
    };
    vscode = {
      enable = true;
      enableUpdateCheck = false;
      enableExtensionUpdateCheck = false;
      userSettings = {
        "[python]" = {
          "editor.formatOnType" = true;
          "editor.defaultFormatter" = "charliermarsh.ruff";
        };
      };
      extensions = with pkgs.vscode-extensions; [
        ms-vscode.cpptools-extension-pack
        mkhl.direnv
        bbenoist.nix
        brettm12345.nixfmt-vscode
        ms-python.python
        ms-python.debugpy
        charliermarsh.ruff
        ms-toolsai.jupyter
        ms-vscode-remote.remote-containers
        ecmel.vscode-html-css
        redhat.vscode-yaml
        foxundermoon.shell-format
      ];
    };
    zsh = {
      enable = true;
      enableCompletion = true;
      autosuggestion.enable = true;
      syntaxHighlighting.enable = true;

      plugins = [{
        name = "powerlevel10k";
        src = pkgs.zsh-powerlevel10k;
        file = "share/zsh-powerlevel10k/powerlevel10k.zsh-theme";
      }];
      
      # Combined initExtra
      initExtra = ''
        # Any custom zsh code goes here
        source ~/.p10k.zsh
        source ~/.aliases
        source ~/.zshrc.local
        source ~/.zsh-custom-functions
      '';

      shellAliases = {
        ll = "ls -la";
        g = "git";
        dc = "docker-compose";
        # Add your aliases here
        ls = "ls --color=auto -F";
        nixswitch = "darwin-rebuild switch --flake ~/src/system-config/.#";
        nixup = "pushd ~/src/system-config; nix flake update; nixswitch; popd";
      };
      oh-my-zsh = {
        enable = true;
        theme = "robbyrussell";
        plugins = [ "git" "kubectl" "helm" "docker" ];
      };
    };
    direnv = { enable = true; };
  };
  home.file = {
    ".inputrc".source = ./dotfiles/inputrc;
    ".aliases".source = ./dotfiles/aliases;  # Add your aliases file
    ".zshrc.local".source = ./dotfiles/zshrc;  # Add your zshrc file
    ".zsh-custom-functions" = {
      text = ''
        function my_custom_function() {
          # function code here
        }
      '';
    };
  };

  # Add Finder settings
  # home.file.".finder-settings" = {
  #   text = ''
  #     # Set Finder preferences
  #     defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"
  #     defaults write com.apple.finder ShowPathbar -bool true
  #     defaults write com.apple.finder ShowStatusBar -bool true
  #   '';
  # };

  home.activation = {
    setDefaults = lib.hm.dag.entryAfter ["writeBoundary"] ''
      # Window Manager settings
      /usr/bin/defaults write com.apple.WindowManager EnableTopTilingByEdgeDrag -bool false
      /usr/bin/defaults write com.apple.WindowManager EnableTilingByEdgeDrag -bool false
      /usr/bin/defaults write com.apple.WindowManager EnableTilingOptionAccelerator -bool false
            
      # Dock settings
      /usr/bin/defaults write com.apple.dock expose-group-by-app -bool true
    '';
    dock = lib.hm.dag.entryAfter ["writeBoundary"] ''
      # Remove all apps from dock first
      ${pkgs.dockutil}/bin/dockutil --remove all \
        --no-restart \
        "$HOME/Library/Preferences/com.apple.dock.plist"

      # Add apps from our list
      ${lib.concatMapStringsSep "\n" (app: ''
        ${pkgs.dockutil}/bin/dockutil --add "${app}" \
          "$HOME/Library/Preferences/com.apple.dock.plist"
      '') dockApps}

      # Restart dock to apply changes
      /usr/bin/killall Dock
    '';
  };
}
