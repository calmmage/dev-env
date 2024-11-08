{ pkgs, lib, ... }:

{
  nix.settings = {
    trusted-users = [ "root" "petr" ];
  };

  networking = {
    computerName = "Petr's MacBook Pro";
    hostName = "petrs-macbook-pro";
    localHostName = "petrs-macbook-pro";
  };

  home-manager.users.petr = { pkgs, lib, ... }: {
    home.packages = with pkgs; [
      # Your desired packages
      ollama
    ];

    # Machine-specific Cursor extensions (if needed)
    programs.vscode = {
      enable = true;
      userSettings = {
        "aws.telemetry" = false;
        "sqltools.dependencyManager" = {
          "packageManager" = "npm";
          "installArgs" = [ "install" ];
          "runScriptArgs" = [ "run" ];
          "autoAccept" = false;
        };
        "sqltools.useNodeRuntime" = true;
        "window.zoomLevel" = 1;
        "redhat.telemetry.enabled" = false;
        "markdown-pdf.executablePath" = "/Applications/Google Chrome.app";
        "files.associations" = { "*.py" = "python"; };
        "[typescript]" = { };
        "[nix]" = { "editor.defaultFormatter" = "brettm12345.nixfmt-vscode"; };
        "github.copilot.editor.enableAutoCompletions" = false;
        "dev.containers.dockerPath" =
          "/etc/profiles/per-user/petr/bin/docker";
        "direnv.path.executable" =
          "/etc/profiles/per-user/petr/bin/direnv";
        "css.enabledLanguages" = "nunjucks html";
        "amazonQ" = {
          "shareContentWithAWS" = false;
          "telemetry" = false;
        };
        "continue.enableTabAutocomplete" = false;
      };
      extensions = with pkgs.vscode-extensions;
        [
          # Add any bflhair-specific VSCode extensions here
        ] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [
          # Add any marketplace extensions here if needed
        ];
    };

    programs.git.extraConfig = {
      user.email = lib.mkForce "petr@superlinear.com";
    };
  };

  home-manager.backupFileExtension = "backup";
}
