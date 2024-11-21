{ pkgs }:
let
  shared = import ./shared.nix { inherit pkgs; };
  petrWork = import ./petr-work.nix { inherit pkgs; };
  petrPersonal = import ./petr-personal.nix { inherit pkgs; };
in
{
  userconfigs = {
    petr = shared // petrWork;
    petrlavrov = shared // petrPersonal;
    default = shared;
  };
}
