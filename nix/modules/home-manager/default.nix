{ pkgs, lib, userConfig, ... }:

let
  dockApps = userConfig.dock.apps;
in
{
  # Don't change this when you change package input. Leave it alone.
  home.stateVersion = "24.05";
  
  # Use packages from user config
  home.packages = map (name: pkgs.${name}) userConfig.home_manager.packages;

  home.sessionVariables = {
    PAGER = "less";
    CLICOLOR = 1;
    EDITOR = "subl";
    # PATH = "$PATH:$HOME/bin";
    PATH = "$PATH:$HOME/bin:$DEV_ENV_PATH/.venv/bin";  # Add Poetry env to PATH
  };

  imports = [
    ../shell
  ];

  programs = {
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
