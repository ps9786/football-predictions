for i in $(cat teams.csv | grep -v "Team1" | perl -pe "s{,}{\n}g" | perl -pe "s{ }{_}g" | sort -u)  
do
./check_teams.sh $i
sleep 5
done | tee check.txt



