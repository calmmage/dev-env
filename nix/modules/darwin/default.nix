{ config, pkgs, lib, userConfig, ... }:
{
  # here go the darwin preferences and config items
  programs.zsh.enable = true;
  environment = {
    shells = [ pkgs.bash pkgs.zsh ];
    systemPackages = with pkgs; [ 
      coreutils 
      (pkgs.poetry2nix.mkPoetryEnv {
        projectDir = ../../..;
        preferWheels = true;
        python = python311;
        # Add overrides to handle git dependencies
        overrides = pkgs.poetry2nix.overrides.withDefaults (final: prev: {
          calmlib = prev.calmlib.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ 
              pkgs.poetry
              final.poetry-core
            ];
          });
        });
        # Add extra packages that might be needed for building
        extraPackages = ps: with ps; [
          pip
          setuptools
          wheel
          poetry
          poetry-core
        ];
      })
    ];
    systemPath = [
      "/opt/homebrew/bin"
      # "$DEV_ENV_PATH/tools/" - remove for now - can't get it to work
    ];
    pathsToLink = [ "/Applications" ];
  };
  nix = {
    settings = { trusted-users = [ "root" userConfig.username ]; };
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
      # dock = {
      #   autohide = true;
      #   largesize = 128;
      #   magnification = true;
      #   # tilesize = 36;
      #   # expose-group-apps = true;
      #   mru-spaces = false; # disable reordering spaces automatically based on recent usage (I hate them chaotically reordering)
      #   minimize-to-application = true; # minimize to application instead separate windows
      # };
    };
    activationScripts.postActivation.text = ''
      # Allow Karabiner-Elements to receive keyboard events
      /usr/bin/sudo /usr/bin/security authorizationdb write system.privilege.taskport allow
      
      # Ensure Homebrew directories have correct permissions
      if [ -d "/opt/homebrew" ]; then
        echo "Setting proper permissions for Homebrew directories..."
        /usr/bin/sudo /bin/chmod -R 755 /opt/homebrew
        /usr/bin/sudo /usr/sbin/chown -R ${userConfig.username}:admin /opt/homebrew
      fi
    '';
  };

  networking = {
    computerName = userConfig.computer_name;
    hostName = userConfig.host_name;
    localHostName = userConfig.local_host_name;
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
    
    # Use brew packages from user config
    brews = userConfig.homebrew.brews;
    casks = userConfig.homebrew.casks;
  };
}
