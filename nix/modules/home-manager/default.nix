{ pkgs, lib, userConfig, ... }:

let
  dockApps = userConfig.dock.apps;
in
{
  # Don't change this when you change package input. Leave it alone.
  home.stateVersion = "23.11";
  
  # Use packages from user config
  home.packages = map (name: pkgs.${name}) userConfig.home_manager.packages;

  home.sessionVariables = {
    PAGER = "less";
    CLICOLOR = 1;
    EDITOR = "subl";
    # PATH = "$PATH:$HOME/bin";
    PATH = "$PATH:$HOME/bin:$DEV_ENV_PATH/.venv/bin";  # Add Poetry env to PATH
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
        nixnix= "nix flake update; darwin-rebuild switch --flake .#default";
        nixswitch = "darwin-rebuild switch --flake $DEV_ENV_PATH/nix/.#default";
        nixup = "pushd $DEV_ENV_PATH/nix; nix flake update; nixswitch; popd";
        # nixapply  = "$DEV_ENV_PATH/apply.sh";
        # runp = "$DEV_ENV_PATH/.venv/bin/python";
        # ipy = "$DEV_ENV_PATH/.venv/bin/ipython";
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
      /usr/bin/defaults write com.apple.dock expose-group-by-app -bool ${toString userConfig.dock.settings.expose_group_by_app}
      /usr/bin/defaults write com.apple.dock autohide -bool ${toString userConfig.dock.settings.autohide}
      /usr/bin/defaults write com.apple.dock magnification -bool ${toString userConfig.dock.settings.magnification}
      /usr/bin/defaults write com.apple.dock largesize -int ${toString userConfig.dock.settings.magnification_size}
      /usr/bin/defaults write com.apple.dock tilesize -int ${toString userConfig.dock.settings.tile_size}
      /usr/bin/defaults write com.apple.dock minimize-to-application -bool ${toString userConfig.dock.settings.minimize_to_application}
      /usr/bin/defaults write com.apple.dock show-recents -bool ${toString userConfig.dock.settings.show_recent_apps}
      /usr/bin/defaults write com.apple.dock show-process-indicators -bool ${toString userConfig.dock.settings.show_process_indicators}
      /usr/bin/defaults write com.apple.dock orientation -string ${userConfig.dock.settings.position}

    '';
    dock = lib.hm.dag.entryAfter ["writeBoundary"] ''
      # Remove all apps from dock first
      ${pkgs.dockutil}/bin/dockutil --remove all \
        --no-restart \
        "$HOME/Library/Preferences/com.apple.dock.plist"

      # Add apps from our config
      ${lib.concatMapStringsSep "\n" (app: ''
        ${pkgs.dockutil}/bin/dockutil --add "${app}" \
          "$HOME/Library/Preferences/com.apple.dock.plist"
      '') userConfig.dock.apps}

      # Restart dock to apply changes
      /usr/bin/killall Dock
    '';
  };
}
