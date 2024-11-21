{ agenix, config, pkgs, lib, poetry2nix, userConfig, ... }:

let
  user = userConfig.username;
  inherit (lib) mkEnableOption mkOption types;
  # Add an overlay to disable tests for problematic Python packages
  pythonOverlay = final: prev: {
    # Disable ghostscript tests that are failing on Darwin
    ghostscript = prev.ghostscript.overrideAttrs (old: {
      doCheck = false;
    });
    
    python311 = prev.python311.override {
      packageOverrides = pyFinal: pyPrev: {
        dnspython = pyPrev.dnspython.overridePythonAttrs (old: {
          doCheck = false;  # Disable tests for dnspython
        });
        cherrypy = pyPrev.cherrypy.overridePythonAttrs (old: {
          doCheck = false;  # Disable tests for cherrypy
        });
        # Add matplotlib override to skip ghostscript dependency
        matplotlib = pyPrev.matplotlib.overridePythonAttrs (old: {
          doCheck = false;
          # Optionally disable ghostscript dependency if you don't need PDF support
          buildInputs = builtins.filter (p: p.pname or "" != "ghostscript") (old.buildInputs or []);
        });
      };
    };
  };
in
{
  # Extend the overlays
  nixpkgs.overlays = lib.mkAfter [
    pythonOverlay
    poetry2nix.overlays.default
  ];

  imports = [
  # todo: re-enable secrets
#    ../../modules/darwin/secrets.nix
    ../../modules/darwin/home-manager.nix
     agenix.darwinModules.default
  ];

  # Auto upgrade nix package and the daemon service.
  services.nix-daemon.enable = true;

  # todo: user config
#  networking = {
#    computerName = userConfig.computer_name;
#    hostName = userConfig.host_name;
#    localHostName = userConfig.local_host_name;
#  };

  # fonts.fontDir.enable = true; # DANGER
  fonts.packages = [ (pkgs.nerdfonts.override { fonts = [ "Meslo" ]; }) ];

  documentation.enable = false;

  # Setup user, packages, programs
  nix = {
    package = pkgs.nix;
    settings = {
      trusted-users = [ "root" "@admin" "${user}" ];
      substituters = [ "https://nix-community.cachix.org" "https://cache.nixos.org" ];
      trusted-public-keys = [ "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=" ];
    };

    gc = {
      user = "root";
      automatic = true;
      interval = { Weekday = 0; Hour = 2; Minute = 0; };
      options = "--delete-older-than 30d";
    };

    extraOptions = ''
      experimental-features = nix-command flakes
    '';
  };

  # Turn off NIX_PATH warnings now that we're using flakes
  system.checks.verifyNixPath = false;

  # Load configuration that is shared across systems
  environment = {
    shells = [ pkgs.bash pkgs.zsh ];
    systemPackages = with pkgs; [
      agenix.packages."${pkgs.system}".default
      coreutils
      defaultbrowser
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
    ] ++ (import ../../modules/darwin/packages.nix { inherit pkgs; });

    systemPath = [
      "/opt/homebrew/bin"
      # "$DEV_ENV_PATH/tools/" - remove for now - can't get it to work
    ];
    pathsToLink = [ "/Applications" ];
  };

#  launchd.user.agents.emacs.path = [ config.environment.systemPath ];
#  launchd.user.agents.emacs.serviceConfig = {
#    KeepAlive = true;
#    ProgramArguments = [
#      "/bin/sh"
#      "-c"
#      "/bin/wait4path ${pkgs.emacs}/bin/emacs && exec ${pkgs.emacs}/bin/emacs --fg-daemon"
#    ];
#    StandardErrorPath = "/tmp/emacs.err.log";
#    StandardOutPath = "/tmp/emacs.out.log";
#  };

  # Enable TouchID for sudo if option is enabled
  security.pam.enableSudoTouchIdAuth = lib.mkDefault true;

  system = {
    keyboard.enableKeyMapping = true;
    keyboard.remapCapsLockToEscape = false;
    stateVersion = 4;
    activationScripts.postActivation.text = ''
      # Allow Karabiner-Elements to receive keyboard events
      /usr/bin/sudo /usr/bin/security authorizationdb write system.privilege.taskport allow
    '';

    defaults = {
      NSGlobalDomain = {
        AppleShowAllExtensions = true;
        ApplePressAndHoldEnabled = false;

        # 120, 90, 60, 30, 12, 6, 2
        KeyRepeat = 2;

        # 120, 94, 68, 35, 25, 15
        InitialKeyRepeat = 15;

        "com.apple.mouse.tapBehavior" = 1;
        "com.apple.sound.beep.volume" = 0.0;
        "com.apple.sound.beep.feedback" = 0;

        AppleInterfaceStyle = "Dark";
        AppleInterfaceStyleSwitchesAutomatically = false;
        AppleShowAllFiles = true;
        NSNavPanelExpandedStateForSaveMode = true;
      };

      dock = {
        autohide = true;
        show-recents = true;
        launchanim = true;
        orientation = "bottom";
        tilesize = 36;
        largesize = 128;

        magnification = true;
        # expose-group-apps = userConfig.dock.settings.expose_group_by_app;
        mru-spaces = false; # disable reordering spaces
        minimize-to-application = true;
        show-process-indicators = true;

#        autohide = userConfig.dock.settings.autohide;
#        largesize = userConfig.dock.settings.large_size;
#        magnification = userConfig.dock.settings.magnification;
#        tilesize = userConfig.dock.settings.tile_size;
#        # orientation = userConfig.dock.settings.position;
#        # expose-group-apps = userConfig.dock.settings.expose_group_by_app;
#        mru-spaces = userConfig.dock.settings.mru_spaces;
#        minimize-to-application = userConfig.dock.settings.minimize_to_application;
#        show-recents = userConfig.dock.settings.show_recent_apps;
#        show-process-indicators = userConfig.dock.settings.show_process_indicators;
      };

      finder = {
        AppleShowAllExtensions = true;
        _FXShowPosixPathInTitle = true;
        FXPreferredViewStyle = "Nlsv";
  #     defaults write com.apple.finder ShowPathbar -bool true
  #     defaults write com.apple.finder ShowStatusBar -bool true
      };

      trackpad = {
        Clicking = true;
        TrackpadThreeFingerDrag = true;
      };
    };
  };
}
