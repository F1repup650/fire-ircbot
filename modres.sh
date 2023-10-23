
if [[ "${1}." = "." ]]; then
echo ERROR
else 
rm -rf ~/${REPL_SLUG}/venv/${1}*
echo removed ${1}
fi