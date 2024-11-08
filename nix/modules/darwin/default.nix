{ pkgs, ... }:
let
  username = "petr";
in
{
  # here go the darwin preferences and config items
  programs.zsh.enable = true;
  environment = {
    shells = [ pkgs.bash pkgs.zsh ];
    loginShell = pkgs.zsh;
    systemPackages = [ pkgs.coreutils ];
    systemPath = [ "/opt/homebrew/bin" ];
    pathsToLink = [ "/Applications" ];
  };
  nix = {
    settings = { trusted-users = [ "root" "${username}" ]; };
    extraOptions = ''
      experimental-features = nix-command flakes
    '';
  };
  system = {
    keyboard.enableKeyMapping = true;
    keyboard.remapCapsLockToEscape = false;
    stateVersion = 4;
    defaults = {
      finder = {
        AppleShowAllExtensions = true;
        _FXShowPosixPathInTitle = true;
        FXPreferredViewStyle = "Nlsv";
      };
      NSGlobalDomain = {
        AppleInterfaceStyle = "Dark";
        AppleInterfaceStyleSwitchesAutomatically = true;
        AppleShowAllExtensions = true;
        InitialKeyRepeat = 14;
        KeyRepeat = 1;
        AppleShowAllFiles = true;
        NSNavPanelExpandedStateForSaveMode = true;
        "com.apple.mouse.tapBehavior" = 1;
      };
      dock = {
        autohide = true;
        largesize = 128;
        magnification = true;
        # tilesize = 36;
        # expose-group-apps = true;
        mru-spaces = false; # disable reordering spaces automatically based on recent usage (I hate them chaotically reordering)
        minimize-to-application = true; # minimize to application instead separate windows
      };
    };
    activationScripts.postActivation.text = ''
      # Allow Karabiner-Elements to receive keyboard events
      /usr/bin/sudo /usr/bin/security authorizationdb write system.privilege.taskport allow
      
      # Ensure Homebrew directories have correct permissions
      if [ -d "/opt/homebrew" ]; then
        echo "Setting proper permissions for Homebrew directories..."
        /usr/bin/sudo /bin/chmod -R 755 /opt/homebrew
        /usr/bin/sudo /usr/sbin/chown -R ${username}:admin /opt/homebrew
      fi
    '';
  };
  networking = {
    # computerName = "mbpr1619";
    # hostName = "mbpr1619";
    # localHostName = "mbpr1619";
  };

  security.pam.enableSudoTouchIdAuth = false;
  # fonts.fontDir.enable = true; # DANGER
  fonts.packages = [ (pkgs.nerdfonts.override { fonts = [ "Meslo" ]; }) ];
  services = { nix-daemon = { enable = true; }; };

  documentation.enable = false;

  nixpkgs.config.allowUnfree = true;

  homebrew = {
    enable = true;
    caskArgs.no_quarantine = true;
    global.brewfile = true;
    onActivation = {
      autoUpdate = true;
      cleanup = "zap"; # Removes all unmanaged packages
    };
    masApps = { };
    brews = [
      "poetry"
      "ripgrep"
      "sonar-scanner"
    ];

    casks = [
      # Development
      "docker" # docker desktop app
      "jetbrains-toolbox"
      "pycharm"
      "sourcetree"
      "github" # github desktop app
      "launchcontrol"
      "warp"
      "mitmproxy"
      "cursor"
      # "shottr" # Alternative: CleanShot X - installed through setapp
      "karabiner-elements"
      "sublime-text"
      
      # Browsers & Communication
      "google-chrome"
      "slack" 
      "telegram"

      # Productivity & Utils
      "raycast"
      "rectangle"
      # "bartender" # through setapp
      "dropbox"
      "obsidian"
      "notion"
      "chatgpt"

      # App marketplace
      "setapp"
      # todo: install apps manually
      # paste
      # cleanshotX
      # bartender
      # popclip
      # hazeover

      # Creative
      "adobe-creative-cloud"
    ];
  };
}
