# launchd
- how to add command to launchd?  -> LaunchControl
    - create a plist file in ~/Library/LaunchAgents
    - launchctl load ~/Library/LaunchAgents/com.example.myprogram.plist
    - launchctl start com.example.myprogram
    - launchctl stop com.example.myprogram
    - launchctl unload ~/Library/LaunchAgents/com.example.myprogram.plist
    - launchctl list | grep "com.example.myprogram"
- bonus: how to check from a script if a command is already in launchd?
  - launchctl list | grep -q "com.example.myprogram" && echo "running" || echo "not running"

# how to 