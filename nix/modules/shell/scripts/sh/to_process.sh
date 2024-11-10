
# todo: 
function add_alias() {
    echo "" >> ~/.alias
    echo "# $3" >> ~/.alias
    echo "alias $1=\"$2\"" >> ~/.alias
    source ~/.alias
}