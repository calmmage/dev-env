_:
let
  shared = import ./shared.nix;
  petrWork = import ./petr-work.nix;
  petrPersonal = import ./petr-personal.nix;
in
{
  userconfigs = {
    petr = shared // petrWork;
    petrlavrov = shared // petrPersonal;
    default = shared;
  };
}
