let
  # Get the config from local.nix which contains the username
  localConfig = import ./local.nix;
  currentUser = localConfig.username;  # Extract the username from the config

  defaultConfig = import ./default-user.nix;

  userConfigs = {
    petr = import ./petr-work.nix;  # Match your actual username
    petrlavrov = import ./petr-personal.nix;
  };

  selectedConfig =
    let
      config = userConfigs.${currentUser} or defaultConfig;
    in
    builtins.trace "Loading config for user: ${currentUser}, found: ${if userConfigs ? ${currentUser} then "yes" else "no"}"
    config;
in
selectedConfig