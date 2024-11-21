{
  description = "Darwin System Configuration with secrets for MacOS";

  nixConfig = {
    extra-substituters = [
      "https://nixpkgs-python.cachix.org"
      "https://devenv.cachix.org"
      "https://cache.nixos.org"
      "https://nix-community.cachix.org"
    ];
    extra-trusted-public-keys = [
      "nixpkgs-python.cachix.org-1:hxjI7pFxTyuTHn2NkvWCrAUcNZLNS3ZAvfYNuYifcEU="
      "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw="
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
    ];
  };

  inputs = {
#    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    agenix.url = "github:ryantm/agenix";
#    home-manager.url = "github:nix-community/home-manager";
    home-manager = {
      url = "github:nix-community/home-manager/release-24.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    darwin = {
      url = "github:LnL7/nix-darwin/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nix-homebrew = {
      url = "github:zhaofengli-wip/nix-homebrew";
    };
    homebrew-bundle = {
      url = "github:homebrew/homebrew-bundle";
      flake = false;
    };
    homebrew-core = {
      url = "github:homebrew/homebrew-core";
      flake = false;
    };
    homebrew-cask = {
      url = "github:homebrew/homebrew-cask";
      flake = false;
    }; 
    disko = {
      url = "github:nix-community/disko";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # todo: add secrets back
#    secrets = {
#      url = "git+ssh://git@github.com/petrlavrov-sl/nix-secrets.git";
#      flake = false;
#    };
  };
  outputs = { self, darwin, nix-homebrew, homebrew-bundle, homebrew-core, homebrew-cask, home-manager, nixpkgs, nixpkgs-unstable, disko, poetry2nix, agenix, ... } @inputs: # , secrets # todo: add secrets back
  let
    user = "petr";
    userConfig = (import ./config/default.nix).userconfigs.${user};
    darwinSystem = "default";
    system = "aarch64-darwin";

    # Define devShell for a single system
    devShell = let pkgs = nixpkgs.legacyPackages.${darwinSystem}; in {
      default = with pkgs; mkShell {
        nativeBuildInputs = [ bashInteractive git age age-plugin-yubikey ];
        shellHook = ''
          export EDITOR=vim
        '';
      };
    };

    # Define a single app wrapper
    mkApp = scriptName: {
      type = "app";
      program = "${(nixpkgs.legacyPackages.${darwinSystem}.writeScriptBin scriptName ''
        #!/usr/bin/env bash
        PATH=${nixpkgs.legacyPackages.${darwinSystem}.git}/bin:$PATH
        echo "Running ${scriptName} for ${darwinSystem}"
        exec ${self}/apps/aarch64-darwin/${scriptName}
      '')}/bin/${scriptName}";
    };

    # Define specific apps directly
    darwinApps = {
      "apply" = mkApp "apply";
      "build" = mkApp "build";
      "build-switch" = mkApp "build-switch";
      "copy-keys" = mkApp "copy-keys";
      "create-keys" = mkApp "create-keys";
      "check-keys" = mkApp "check-keys";
      "rollback" = mkApp "rollback";
    };
  in
  {
    darwinConfigurations.default = darwin.lib.darwinSystem {
      inherit system;
      specialArgs = inputs;
      modules = [
        {
          nixpkgs.config.allowUnfree = true;
          nixpkgs.config.allowBroken = true;
          nixpkgs.config.allowInsecure = false;
          nixpkgs.config.allowUnsupportedSystem = false;
        }
        home-manager.darwinModules.home-manager
        nix-homebrew.darwinModules.nix-homebrew
        {
          nix-homebrew = {
            inherit user;
            enable = true;
            taps = {
              "homebrew/homebrew-core" = homebrew-core;
              "homebrew/homebrew-cask" = homebrew-cask;
              "homebrew/homebrew-bundle" = homebrew-bundle;
            };
            mutableTaps = false;
            autoMigrate = true;
          };
        }
        ./hosts/darwin
      ];
    };

    devShells.default = devShell;
    apps.default = darwinApps;
  };
}
