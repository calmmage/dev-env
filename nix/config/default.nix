{ pkgs }:
let
  shared = import ./shared.nix { inherit pkgs; };
  petrWork = import ./petr-work.nix { inherit pkgs; };
  petrPersonal = import ./petr-personal.nix { inherit pkgs; };
  
  # Helper function for deep merging
  recursiveMerge = attr1: attr2:
    let
      f = attrPath:
        let
          set1 = builtins.getAttr attrPath attr1;
          set2 = builtins.getAttr attrPath attr2;
        in
        if builtins.isAttrs set1 && builtins.isAttrs set2
        then set1 // set2
        else if builtins.isList set1 && builtins.isList set2
        then set1 ++ set2
        else set2;
    in
    builtins.zipAttrsWith (name: values: f name) [ attr1 attr2 ];
in
{
  userconfigs = {
    # use this for shallow merge - to OVERRIDE shared configs with personal
    #    petr = shared // petrWork;
    #    petrlavrov = shared // petrPersonal;
    # use this for deep merge - to merge the internal list and dicts
    petr = recursiveMerge shared petrWork;
    petrlavrov = recursiveMerge shared petrPersonal;
    default = shared;
  };
}
