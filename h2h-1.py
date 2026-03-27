import os
import requests
import csv
import time

# 1. Configuration
API_KEY = os.getenv("SPORTSDB", "123")
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/searchevents.php"
INPUT_FILE = "teams.csv"
OUTPUT_FILE = "matchup_summary.csv"
SEASONS = ["2022-2023","2023-2024", "2024-2025", "2025-2026"]

def fetch_data(query, season):
    params = {'e': query, 's': season}
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 429:
            print("  [!] Rate limit hit. Sleeping 30s...")
            time.sleep(30)
            return None
        if response.status_code != 200:
            return None
        return response.json().get('event')
    except Exception:
        return None

def get_aligned_scores(t1_csv, t2_csv):
    """Fetches matches both ways and aligns scores to the CSV order."""
    all_matches = []
    
    for season in SEASONS:
        # Search both directions
        queries = [f"{t1_csv}_vs_{t2_csv}", f"{t2_csv}_vs_{t1_csv}"]
        for q in queries:
            events = fetch_data(q, season)
            if events:
                all_matches.extend(events)
        time.sleep(0.5) # Throttling

    if not all_matches:
        print(f"  [-] No results found for '{t1_csv}' vs '{t2_csv}'.")
        return None

    # Sort Newest First
    all_matches.sort(key=lambda x: x.get('dateEvent', ''), reverse=True)

    aligned_scores = []
    for event in all_matches[:5]:
        api_home = event.get('strHomeTeam', '').strip().lower()
        h_score = event.get('intHomeScore')
        a_score = event.get('intAwayScore')
        
        if h_score is None or a_score is None:
            continue

        # If API Home is the same as CSV Team1, order is H-A
        # If API Home is the same as CSV Team2, order is A-H (Flipped)
        if api_home == t1_csv.lower():
            aligned_scores.append(f"{h_score}-{a_score}")
        else:
            aligned_scores.append(f"{a_score}-{h_score}")
    
    while len(aligned_scores) < 5:
        aligned_scores.append("")
        
    return aligned_scores

def process_teams():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    results_to_save = []
    with open(INPUT_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get('Team1') or not row.get('Team2'):
                continue
                
            t1, t2 = row['Team1'].strip(), row['Team2'].strip()
            print(f"Processing: {t1} vs {t2}")
            
            scores = get_aligned_scores(t1, t2)
            if scores:
                results_to_save.append([t1, t2] + scores)

    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Home Team', 'Away Team', 'Score 1', 'Score 2', 'Score 3', 'Score 4', 'Score 5'])
        writer.writerows(results_to_save)
    print(f"\nDone. Results aligned to CSV order and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_teams()
