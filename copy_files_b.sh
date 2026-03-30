cp matchup_summary.csv ../pl-predictions/matchup_summary_b.csv
cp team_form_summary.csv ../pl-predictions/team_form_summary_b.csv
bash ./make_games_text.sh
cp games.txt ../pl-predictions/games_b.txt
