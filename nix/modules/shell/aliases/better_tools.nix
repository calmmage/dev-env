{ config, lib, pkgs, ... }:

{
  programs.zsh.shellAliases = {
    # Navigation
    ls = "exa";  # Modern ls with git integration and colors
    # ls = "ls --color=auto -F";
    tree_ = "broot";  # Interactive tree view with fuzzy search
    
    # Search
    find = "fd";  # User-friendly, fast alternative to find
    grep = "rg";  # Fast grep with better syntax and git integration
    locate = "plocate";  # Much faster locate
    
    # Process Management
    top = "btop";  # Interactive process viewer
    ps = "procs";  # Modern replacement for ps
    # kill = "fkill";  # Interactive process killer
    
    # File Operations
    cp = "rsync -ah --progress";  # Advanced copy with progress
    cat = "bat";  # Cat with syntax highlighting
    less = "most";  # More feature-rich pager
    
    # System Monitoring
    df = "duf";  # Disk usage with better UI
    # du = "dust";  # Interactive disk usage analyzer
    free = "bottom";  # System resource monitor
    
    # Text Processing
    sed = "sd";  # Simpler syntax for sed
    diff = "delta";  # Git diff with syntax highlighting
    
    # Network
    ping = "gping";  # Ping with graph
    traceroute = "mtr";  # Better network diagnostics
    netstat = "ss";  # Modern netstat replacement
    
    # File Management
    rm = "trash";  # Safer alternative that moves to trash
    mkdir = "mkdir -p";  # Create parent directories automatically
  };
} 