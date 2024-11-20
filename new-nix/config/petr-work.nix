{
  username = "petr";
  email = "petr@superlinear.com";
  computer_name = "Petr's MacBook Pro";
  host_name = "petrs-macbook-pro";

  default_browser = "chrome";

  dock = {
    settings = {
      # Visual settings
      autohide = true;
      magnification = true;
      tile_size = 36;
      large_size = 128;
      position = "bottom";  # Can be "bottom", "left", or "right"
      mru_spaces = false; # disable reordering spaces automatically based on recent usage (I hate them chaotically reordering)

      # Behavior settings
      expose_group_by_app = true;
      minimize_to_application = true;
      show_recent_apps = true;
      show_process_indicators = true;
    };

    apps = [
      "/Applications/Raycast.app"
      "/System/Applications/System Settings.app"
    ];
  };

  homebrew = {
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
      # add fkill? how?
    ];

  };

}