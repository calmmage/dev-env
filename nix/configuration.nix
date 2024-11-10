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
    # programs.vscode = {
    #   enable = true;
    #   enableUpdateCheck = false;
    #   enableExtensionUpdateCheck = false;
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
    #     "[python]" = {
    #       "editor.formatOnType" = true;
    #       "editor.defaultFormatter" = "charliermarsh.ruff";
    #     };
    #     "github.copilot.editor.enableAutoCompletions" = false;
    #     "dev.containers.dockerPath" = "/etc/profiles/per-user/petr/bin/docker";
    #     "direnv.path.executable" = "/etc/profiles/per-user/petr/bin/direnv";
    #     "css.enabledLanguages" = "nunjucks html";
    #     "amazonQ" = {
    #       "shareContentWithAWS" = false;
    #       "telemetry" = false;
    #     };
    #     "continue.enableTabAutocomplete" = false;
    #   };
    #   extensions = with pkgs.vscode-extensions; [
    #     ms-vscode.cpptools-extension-pack
    #     mkhl.direnv
    #     bbenoist.nix
    #     brettm12345.nixfmt-vscode
    #     ms-python.python
    #     ms-python.debugpy
    #     charliermarsh.ruff
    #     ms-toolsai.jupyter
    #     ms-vscode-remote.remote-containers
    #     ecmel.vscode-html-css
    #     redhat.vscode-yaml
    #     foxundermoon.shell-format
    #   ];
    # };

    programs.git.extraConfig = {
      user.email = lib.mkForce userConfig.email;
    };
  };

  home-manager.backupFileExtension = "backup";
}
