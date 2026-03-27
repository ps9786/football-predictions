cat teams.csv | grep -v "Team1" | awk -F, '{print $1 " - " $2}' > games.txt
