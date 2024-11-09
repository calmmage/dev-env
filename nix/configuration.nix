{ pkgs, lib, userConfig, ... }:

{
  nix.settings = {
    trusted-users = [ "root" userConfig.username ];
  };

  # networking = {
  #   computerName = userConfig.computer_name;
  #   hostName = userConfig.host_name;
  #   localHostName = userConfig.local_host_name;
  # };

  home-manager.users.${userConfig.username} = { pkgs, lib, ... }: {
    home.packages = with pkgs; [
      ollama
    ];

    # Machine-specific Cursor extensions (if needed)
    # programs.vscode = {
    #   enable = true;
    #   userSettings = {
    #     "aws.telemetry" = false;
    #     "sqltools.dependencyManager" = {
    #       "packageManager" = "npm";
    #       "installArgs" = [ "install" ];
    #       "runScriptArgs" = [ "run" ];
    #       "autoAccept" = false;
    #     };
    #     "sqltools.useNodeRuntime" = true;
    #     "window.zoomLevel" = 1;
    #     "redhat.telemetry.enabled" = false;
    #     "markdown-pdf.executablePath" = "/Applications/Google Chrome.app";
    #     "files.associations" = { "*.py" = "python"; };
    #     "[typescript]" = { };
    #     "[nix]" = { "editor.defaultFormatter" = "brettm12345.nixfmt-vscode"; };
    #     "github.copilot.editor.enableAutoCompletions" = false;
    #     "dev.containers.dockerPath" =
    #       "/etc/profiles/per-user/petr/bin/docker";
    #     "direnv.path.executable" =
    #       "/etc/profiles/per-user/petr/bin/direnv";
    #     "css.enabledLanguages" = "nunjucks html";
    #     "amazonQ" = {
    #       "shareContentWithAWS" = false;
    #       "telemetry" = false;
    #     };
    #     "continue.enableTabAutocomplete" = false;
    #   };
    #   extensions = with pkgs.vscode-extensions;
    #     [
    #       # Add any bflhair-specific VSCode extensions here
    #     ] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [
    #       # Add any marketplace extensions here if needed
    #     ];
    # };

    programs.git.extraConfig = {
      user.email = lib.mkForce userConfig.email;
    };
  };

  home-manager.backupFileExtension = "backup";
}
