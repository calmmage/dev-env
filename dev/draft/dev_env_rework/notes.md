# launchd
- how to add command to launchd?  -> LaunchControl
    - option 1: use LaunchControl.
      - shell script needs to source zshrc
      - Note: add StdOut ts flag
    - create a plist file in ~/Library/LaunchAgents
    
- bonus: how to check from a script if a command is already in launchd?
  - launchctl list | grep -q "com.example.myprogram" && echo "running" || echo "not running"

# raycast
## how to add command to raycast?
- /// add to ~/dev/draft/dev_env_rework/raycast/calmmage-dev-env.py