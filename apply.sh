# bash script to reapply nix files
source ~/.zshrc

# a) check the .zshrc.new file. migrate all new code from it
# todo: update 'aa' command to use the new .zshrc.new file
echo "Applying nix files for user $USER"

# b) cd to the right dir
cd $DEV_ENV_PATH/nix

# c) git pull / push
git stash
git pull

# d) nix update
nix flake update

# e) nix switch
darwin-rebuild switch --flake .#default
