{ config, pkgs, lib, userConfig, ... }:

let
  # Add an overlay to disable tests for problematic Python packages
  pythonOverlay = final: prev: {
    python311 = prev.python311.override {
      packageOverrides = pyFinal: pyPrev: {
        dnspython = pyPrev.dnspython.overridePythonAttrs (old: {
          doCheck = false;  # Disable tests for dnspython
        });
      };
    };
  };
in
{
  # Add the overlay to nixpkgs
  nixpkgs.overlays = [ pythonOverlay ];

  # here go the darwin preferences and config items
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
          # Add poetry-bumpversion plugin
          poetry-bumpversion = prev.poetry-bumpversion.overridePythonAttrs (old: {
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
          poetry-bumpversion
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
        AppleInterfaceStyleSwitchesAutomatically = false;
        AppleShowAllExtensions = true;
        InitialKeyRepeat = 14;
        KeyRepeat = 1;
        AppleShowAllFiles = true;
        NSNavPanelExpandedStateForSaveMode = true;
        "com.apple.mouse.tapBehavior" = 1;
      };
      dock = {
        autohide = userConfig.dock.settings.autohide;
        largesize = userConfig.dock.settings.large_size;
        magnification = userConfig.dock.settings.magnification;
        tilesize = userConfig.dock.settings.tile_size;
        # position = userConfig.dock.settings.position;
        # expose-group-apps = userConfig.dock.settings.expose_group_by_app;
        mru-spaces = userConfig.dock.settings.mru_spaces;
        minimize-to-application = userConfig.dock.settings.minimize_to_application;
        show-recents = userConfig.dock.settings.show_recent_apps;
        show-process-indicators = userConfig.dock.settings.show_process_indicators;
      };
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
