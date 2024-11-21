{ pkgs }:
{
  username = "petr";
  full_name = "Petr Lavrov";
  email = "petr@superlinear.com";
  computer_name = "Petr's MacBook Pro";
  host_name = "petrs-macbook-pro";
  secrets_repo_url = "git+ssh://git@github.com/petrlavrov-sl/nix-secrets.git";

  homebrew = {
    brews = [
      "sonar-scanner"
    ];

    casks = [
      # Development
      "cursor"
      "karabiner-elements"
      "launchcontrol"
      
      # Communication
      "microsoft-teams"
      
      # Productivity
      "adobe-creative-cloud"
    ];
  };

  packages = with pkgs; [
    # Development Tools
    nixfmt-classic
    pgbadger
    git-remote-codecommit
    gitflow
    
    # AWS & Cloud
    awscli2
    
    # System Tools
    inetutils
    
    # Additional Utils
    age
    shntool
  ];
}