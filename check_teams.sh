RESULT=$(curl -s "https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=$1" | jq -r 'try .teams[] | [ .strTeam,.strLeague,.idTeam ] | @csv ')
echo "Checking $1 - $RESULT"
