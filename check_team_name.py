import sys
import os
from thefuzz import process, fuzz

# Configuration
OFFICIAL_FILE = "good_teams.txt"
INPUT_FILE = "newteams.txt"

def load_official_teams():
    if not os.path.exists(OFFICIAL_FILE):
        print(f"Error: {OFFICIAL_FILE} not found.")
        return []
    with open(OFFICIAL_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_best_match(target, official_list):
    # extractOne returns (match, score)
    best_match, score = process.extractOne(target, official_list, scorer=fuzz.token_sort_ratio)
    
    # 100% confidence check
    if score >= 50:
        return best_match, True
    return best_match, False

def process_teams():
    official_teams = load_official_teams()
    if not official_teams:
        return

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Processing {INPUT_FILE}...\n")

    with open(INPUT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or " v " not in line:
                continue

            # Split the line into two teams
            parts = line.split(" v ")
            if len(parts) != 2:
                print(f"[SKIP] Invalid format: {line}")
                continue

            team_a_raw, team_b_raw = parts[0].strip(), parts[1].strip()

            # Get matches
            match_a, confirmed_a = get_best_match(team_a_raw, official_teams)
            match_b, confirmed_b = get_best_match(team_b_raw, official_teams)

            # Build the output string
            # If 100% confident, use the match. If not, use the raw name.
            final_a = match_a if confirmed_a else team_a_raw
            final_b = match_b if confirmed_b else team_b_raw

            print(f"{final_a} v {final_b}")

            # Show alerts for low confidence
            if not confirmed_a:
                print(f"  [!] ALERT: '{team_a_raw}' is uncertain. Best guess: '{match_a}, {confirmed_a}'")
            if not confirmed_b:
                print(f"  [!] ALERT: '{team_b_raw}' is uncertain. Best guess: '{match_b}, {confirmed_b}'")

if __name__ == "__main__":
    process_teams()
