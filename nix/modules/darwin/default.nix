{ config, pkgs, lib, userConfig, ... }:

let
in
{
  networking = {
    computerName = userConfig.computer_name;
    hostName = userConfig.host_name;
    localHostName = userConfig.local_host_name;
  };

  # fonts.fontDir.enable = true; # DANGER
  fonts.packages = [ (pkgs.nerdfonts.override { fonts = [ "Meslo" ]; }) ];
  services = { nix-daemon = { enable = true; }; };

  documentation.enable = false;
  nixpkgs.config.allowUnfree = true;

}
