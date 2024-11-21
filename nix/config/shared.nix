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
      # "poetry"
      # "ripgrep"
      #  "python@3.11"
      #  "python@3.12"
      "node"
      "git-lfs"
      "gcc"
      "yarn"
      "pinentry-mac"
    ];

    casks = [
        # Development
        "docker"  # docker desktop app
        "jetbrains-toolbox"
        "pycharm"
        # - sourcetree
        "github" # github desktop app
        "launchcontrol"
        "warp"
        # - mitmproxy
        "cursor"
        # "zed"
        "karabiner-elements"
        "sublime-text"

        # Browsers & Communication
        "google-chrome"
        "slack"
        "telegram"

        # Productivity & Utils
        "raycast"
        "rectangle" # window manager
        # "dropbox"
        "obsidian"
        "notion"
        "chatgpt"
        # - shottr # Alternative: CleanShot X - installed through setapp
        # - bartender # through setapp

        # App marketplace
        "setapp"
        # todo: add instructions for user to install apps manually
        # paste
        # cleanshotX
        # bartender
        # popclip
        # hazeover

        # Creative

        # Suggestions from Claude

        # Media Processing & Conversion
        # "ffmpeg"          # Swiss army knife for audio/video processing
        # "imagemagick"     # Powerful image manipulation tool
        # "handbrake"       # Video transcoder
        # "yt-dlp"          # Download videos from YouTube and other sites

        # # Development Tools
        # "neovim"          # Modern, extensible text editor
        # "tmux"            # Terminal multiplexer for multiple sessions
        # "httpie"          # User-friendly HTTP client
        # "mkcert"          # Make locally-trusted development certificates

        # # System Monitoring & Performance
        # "glances"         # System monitoring tool

        # # Network Tools
        # "nmap"            # Network exploration and security scanning
        # "wireshark"       # Network protocol analyzer
        # "netcat"         # Networking utility for reading/writing network connections
        # "mtr"             # Network diagnostic tool

        # # Security & Encryption
        # "gnupg"           # GNU Privacy Guard encryption
        # "bitwarden"       # Password manager
        # "1password"      # Popular password manager alternative
        # "veracrypt"       # Disk encryption software

        # # Productivity
        # "taskwarrior"     # Command-line task management
        # "pandoc"          # Universal document converter
        # "asciinema"       # Terminal session recorder

        # # Database Tools
        # - pgcli           # PostgreSQL CLI with auto-completion
        # - mycli           # MySQL/MariaDB CLI with auto-completion
        # "dbeaver"         # Universal database tool
        # "mongodb-compass" # MongoDB GUI

        # # Cloud & Infrastructure
        # - terraform       # Infrastructure as code
        # - kubernetes-cli  # Kubernetes command-line tool
        # "helm"            # Kubernetes package manager
        # "vagrant"         # Development environment creation

        # # File Management
        # "ranger"          # Console file manager with VI keybindings
        # "fzf"             # Command-line fuzzy finder
        # "rsync"           # Fast file copying tool
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

    # Development Tools
    nixfmt-classic
    pgbadger
    git-remote-codecommit
    gitflow

    # System Tools
    inetutils

    # Additional Utils
    age
    shntool

    # AWS & Cloud
    awscli2

    # Development
    cmake
    dlib

    # System Monitoring
    bottom
    procs
    htop
    duf

    # Additional Utils
    sd
    dust
    gping
    mtr

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