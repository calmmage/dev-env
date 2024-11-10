{
  description = "Darwin System Configuration";

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
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    home-manager = {
      url = "github:nix-community/home-manager/release-24.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    darwin = {
      url = "github:LnL7/nix-darwin/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    homebrew-bundle.url = "github:homebrew/homebrew-bundle";
    homebrew-bundle.flake = false;
    homebrew-core.url = "github:homebrew/homebrew-core";
    homebrew-core.flake = false;
    homebrew-cask.url = "github:homebrew/homebrew-cask";
    homebrew-cask.flake = false;
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, nixpkgs-unstable, home-manager, darwin, poetry2nix, ... }@inputs:
    let
      system = "aarch64-darwin";
      
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };

      # Import user config
      userConfig = import ./config/user.nix;

      # Create specialArgs to pass to all modules
      specialArgs = {
        inherit userConfig;
      };
      
    in {
      darwinConfigurations.default = darwin.lib.darwinSystem {
        inherit system specialArgs;
        
        modules = [
          # Base configuration
          {
            nixpkgs.overlays = [ 
              (final: prev: {
                unstable = nixpkgs-unstable.legacyPackages.${prev.system};
              })
              poetry2nix.overlays.default
            ];
            nixpkgs.config.allowUnfree = true;
          }

          # User configuration
          {
            users.users.${userConfig.username}.home = "/Users/${userConfig.username}";
          }

          # Import modules
          ./modules/darwin
          ./configuration.nix

          # Home Manager configuration
          home-manager.darwinModules.home-manager
          {
            home-manager = {
              useGlobalPkgs = true;
              useUserPackages = true;
              extraSpecialArgs = specialArgs;  # Pass specialArgs to home-manager modules
              users.${userConfig.username} = import ./modules/home-manager;
            };
          }
        ];
      };
    };
}
