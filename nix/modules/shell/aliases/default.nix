{ config, lib, pkgs, ... }:

{
  imports = [
    ./git.nix
    ./navigation.nix
    ./python.nix
    ./tools.nix
    ./better_tools.nix
  ];
} 