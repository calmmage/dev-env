{ config, pkgs, lib, home-manager, userConfig, ... }:

let
  user = userConfig.username;
  # Define the content of your file as a derivation
#  myEmacsLauncher = pkgs.writeScript "emacs-launcher.command" ''
#    #!/bin/sh
#    emacsclient -c -n &
#  '';

# todo: re-enable files.nix when it's populated
#  disable for now
#  files = import ./files.nix { inherit user config pkgs; };
in
{
  imports = [
    ./dock
  ];

  # It me
  users.users.${user} = {
    name = "${user}";
    home = "/Users/${user}";
    isHidden = false;
    shell = pkgs.zsh;
  };

  homebrew = {
    caskArgs.no_quarantine = true;
    global.brewfile = true;
    enable = true;

    brews = userConfig.homebrew.brews;
    casks = pkgs.callPackage ./casks.nix {} ++ userConfig.homebrew.casks;
    masApps = userConfig.homebrew.masApps;

    onActivation = {
      autoUpdate = true;
      cleanup = "uninstall";
      upgrade = true;
    };
  };

  # Enable home-manager
  home-manager = {
    useGlobalPkgs = true;
    useUserPackages = true;
    backupFileExtension = "backup";
    # todo: use config here
    #  extraSpecialArgs = specialArgs;  # Pass specialArgs to home-manager modules
    extraSpecialArgs = {
      inherit userConfig;
    };
    #  users.${userConfig.username} = import ./modules/home-manager;
    # todo: unify username and use config
    users.${user} = { pkgs, config, lib, ... }: {
      home = {
        enableNixpkgsReleaseCheck = false;
        packages = (pkgs.callPackage ./packages.nix {}) ++ userConfig.packages;
        # todo: for now, files.nix is disabled because it's empty.
        #  file = lib.mkMerge [
        #      files
        #    { "emacs-launcher.command".source = myEmacsLauncher; }
        #  ];
        stateVersion = "24.05"; # backup: "23.11";
      };
      programs = {} // import ./programs.nix { inherit config pkgs lib userConfig; };

      # Marked broken Oct 20, 2022 check later to remove this
      # https://github.com/nix-community/home-manager/issues/3344
      manual.manpages.enable = false;
      imports = [ ../shell ];
    };
    # users.${user}.imports = [ ../shell ];

  };

  # Fully declarative dock using the latest from Nix Store
  local = { 
    dock = {
      enable = true;
      entries = [
      # todo: update a list of apps
        { path = "/System/Applications/System Settings.app/"; }
        { path = "/Applications/Raycast.app/"; }
        # { path = "${pkgs.alacritty}/Applications/Alacritty.app/"; }
#        {
#          path = toString myEmacsLauncher;
#          section = "others";
#        }
        {
          path = "${config.users.users.${user}.home}/.local/share/";
          section = "others";
          options = "--sort name --view grid --display folder";
        }
        {
          path = "${config.users.users.${user}.home}/.local/share/downloads";
          section = "others";
          options = "--sort name --view grid --display stack";
        }
      ];
    };
  };
}
