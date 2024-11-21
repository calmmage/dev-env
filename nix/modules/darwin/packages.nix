{ pkgs }:

with pkgs; [
  # General packages for development and system management
  # alacritty
  aspell
  aspellDicts.en
  bash-completion
  btop
  coreutils
  killall
  neofetch
  openssh
  wget
  zip

  # Encryption and security tools
  age-plugin-yubikey
  gnupg
  libfido2

  # Cloud-related tools and SDKs
  docker
  docker-compose

  # Media-related packages
  emacs-all-the-icons-fonts
  dejavu_fonts
  font-awesome
  hack-font
  noto-fonts
  noto-fonts-emoji
  meslo-lgs-nf

  ollama
  # Node.js development tools
  nodePackages.npm # globally install npm
  nodePackages.prettier
  nodePackages.pnpm
  nodejs

  # Text and terminal utilities
  hunspell
  iftop
  jetbrains-mono
  unrar
  unzip

  # Python packages
  python3
  virtualenv

  # mack-specific
  dockutil


    # CLI Tools
    # utils
    curl          # Command line tool for transferring data with URLs
    less          # Terminal pager for viewing file contents
    cmake           # Cross-platform build system generator
    dlib            # C++ toolkit for machine learning
    tree            # Directory listing in tree-like format
    ffmpeg          # Swiss army knife for audio/video processing

    # custom
    gh            # GitHub's official command line tool
    # docker        # CLI interface for Docker containers - conflicts with brew

    # style
    oh-my-zsh     # Framework for managing zsh configuration
    zsh-powerlevel10k  # Modern, fast zsh theme

    # new
    # new - to explore
    direnv        # Environment switcher for the shell
    devenv        # Development environment manager
    cachix        # Binary cache hosting service for Nix
    postman       # API development environment

    # new - clear
    awscli2           # AWS command line interface v2
    teams           # Microsoft Teams client

    # new - unclear
    nixfmt-classic     # Nix code formatter
    pgbadger        # PostgreSQL log analyzer
    inetutils       # Collection of common network utilities
    git-remote-codecommit  # Git remote helper for AWS CodeCommit
    gitflow         # Git branching model extension
    shntool         # Multi-purpose WAVE data processing tool
    age             # Simple, modern file encryption tool

    # via brew
    # slack
    poetry
    ripgrep # Fast grep alternative written in Rust

    # Suggestions from Claude
    jq              # Command-line JSON processor and manipulator
    htop            # Interactive process viewer and system monitor
    tmux            # Terminal multiplexer for multiple sessions
    bat             # Cat clone with syntax highlighting and git integration
    eza             # Modern replacement for ls with git integration (fork of exa)
    # ncdu            # NCurses disk usage analyzer
    duf             # Disk usage/free utility with better UI
    tldr            # Simplified and community-driven man pages

    # Adding from snapshot analysis
    pkg-config      # Build tool to help compile applications and libraries
    openssl        # SSL/TLS toolkit for secure communication
    readline       # Library for command-line editing
    sqlite         # Self-contained SQL database engine
    xz             # Data compression utility and library
    zstd           # Fast real-time compression algorithm
    SDL2           # Multimedia library for audio, video, input and more
    gettext        # Internationalization and localization system
    libuv          # Multi-platform support library with focus on asynchronous I/O
    # gcc is in brew instead
    # python versions are in brew instead

    # Navigation & File Management
    zoxide          # Better alternative to z/autojump
    broot          # Interactive tree view with fuzzy search
    fd             # User-friendly alternative to find
    fzf            # Command-line fuzzy finder
    trash-cli      # Safer alternative to rm

    # Process & System Monitoring
    bottom         # System resource monitor (btop)
    procs         # Modern replacement for ps

    # Text Processing & Viewing
    sd            # Simpler syntax for sed
    most          # More feature-rich pager than less
    dust          # More intuitive du
    gping         # Ping with graphs
    mtr           # Better traceroute

    # File Operations
    rsync         # Advanced file copying
    delta           # Syntax highlighting pager for git diffs
]
