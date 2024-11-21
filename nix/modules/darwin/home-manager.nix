{ config, pkgs, lib, home-manager, ... }:

let
  user = "petr";
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

    # todo: Use brew packages from user config
    #  brews = userConfig.homebrew.brews;
    brews = [
      # Development essentials that work better with brew
      # "poetry"
      # "ripgrep"
      "python@3.11"
      "python@3.12"
      "node" # Node.js - often better to use brew for JS ecosystem
      "git-lfs" # Git Large File Storage
      "gcc" # GNU Compiler Collection
      "sonar-scanner"
      "yarn" # Adding yarn package manager
      "pinentry-mac"
      # add fkill? how?
    ];
    #  casks = userConfig.homebrew.casks;
    enable = true;
    casks = pkgs.callPackage ./casks.nix {};
    onActivation = {
      autoUpdate = true;
      cleanup = "uninstall";
      upgrade = true;
    };

    # These app IDs are from using the mas CLI app
    # mas = mac app store
    # https://github.com/mas-cli/mas
    #
    # $ nix shell nixpkgs#mas
    # $ mas search <app name>
    #
    # If you have previously added these apps to your Mac App Store profile (but not installed them on this system),
    # you may receive an error message "Redownload Unavailable with This Apple ID".
    # This message is safe to ignore. (https://github.com/dustinlyons/nixos-config/issues/83)

    masApps = {
      "flow" = 1423210932;
      #  "1password" = 1333542190;
      #  "wireguard" = 1451685025;
    };
  };

  # Enable home-manager
  home-manager = {
    useGlobalPkgs = true;
    useUserPackages = true;
    backupFileExtension = "backup";
    # todo: use config here
    #  extraSpecialArgs = specialArgs;  # Pass specialArgs to home-manager modules
    #  users.${userConfig.username} = import ./modules/home-manager;
    # todo: unify username and use config
    users.${user} = { pkgs, config, lib, ... }:{
      home = {
        enableNixpkgsReleaseCheck = false;
        packages = pkgs.callPackage ./packages.nix {};
        # todo: for now, files.nix is disabled because it's empty.
        #  file = lib.mkMerge [
        #      files
        #    { "emacs-launcher.command".source = myEmacsLauncher; }
        #  ];
        stateVersion = "23.11";
      };
      programs = {} // import ./programs.nix { inherit config pkgs lib; };

      # Marked broken Oct 20, 2022 check later to remove this
      # https://github.com/nix-community/home-manager/issues/3344
      manual.manpages.enable = false;
    };
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
