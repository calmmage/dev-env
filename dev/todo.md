- [x] 1) Move home-manager home.packages = with pkgs; [
 to ... config user.yaml

2) 
   - setup user config
   - delete my apps
   - apply nix 

- [x] 3) Move brew packages list to user.yaml


4) Invent a better structure for specific configs:
   - user-specific aliases?
   - user-specific bashrc / zshrc values - e.g. local? 

5) create a private personal.nix file with local settings, aliases etc.. 
   
6) learning tools
- create aliases for useful tools
- make a list of common actions and tools for them (accompanied by aliases)
- a tool for used /aliased and unused / unaliased tools (three categories: used, unused, ingored)


- [x] deduplicate brew and home-manager packages with preference to home-manager
- [x] add brew tools from brew dump
- [ ] add tools from claude suggested tools (and aliases)
- [ ] figure out how to better store aliases: in nix-file or in .aliases file?
- [ ] add aliases for better tool replacements