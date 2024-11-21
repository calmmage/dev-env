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
      # Communication
      "microsoft-teams"
    ];
  };

#  packages = with pkgs; [
#  ];
}