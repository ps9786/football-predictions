cp matchup_summary.csv ../pl-predictions
cp team_form_summary.csv ../pl-predictions
bash ./make_games_text.sh
cp games.txt ../pl-predictions
