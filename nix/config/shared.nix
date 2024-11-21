{ pkgs }:
{
  username = "";# "petrlavrov";
  full_name = "";# "Petr Lavrov";
  email = "";# "petr.b.lavrov@gmail.com";
  computer_name = "";# "Petr's MacBook Pro 2";
  host_name = "";# "petrs-macbook-pro-2";
  secrets_repo_url = "";# "git+ssh://git@github.com/calmmage/nix-secrets.git";

  default_browser = "chrome";

  homebrew = {
    brews = [
      # Development essentials
      "python@3.11"
      "python@3.12"
      "node"
      "git-lfs"
      "gcc"
      "yarn"
      "pinentry-mac"
    ];

    casks = [
      # Development
      "docker"
      "jetbrains-toolbox"
      "pycharm"
      "github"
      "warp"
      "sublime-text"

      # Browsers & Communication
      "google-chrome"
      "slack"
      "telegram"

      # Productivity & Utils
      "raycast"
      "rectangle"
      "obsidian"
      "notion"
      "chatgpt"
      "setapp"
    ];


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

  packages = with pkgs; [
    # CLI Tools & Utils
    curl
    less
    tree
    ffmpeg
    gh
    
    # Shell & Environment
    oh-my-zsh
    zsh-powerlevel10k
    direnv
    devenv
    
    # Development Tools
    pkg-config
    openssl
    readline
    sqlite
    
    # Navigation & File Management
    zoxide
    fd
    fzf
    trash-cli
    
    # Text Processing & Viewing
    bat
    ripgrep
    jq
    delta
  ];
}