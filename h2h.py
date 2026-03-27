import os
import requests
import csv
import time

# 1. Configuration
API_KEY = os.getenv("SPORTSDB", "123")
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"
INPUT_FILE = "teams.csv"
H2H_OUTPUT = "matchup_summary.csv"
FORM_OUTPUT = "team_form_summary.csv"
SEASONS = ["2023-2024", "2024-2025", "2025-2026"]

def get_team_id(team_name):
    url = f"{BASE_URL}/searchteams.php?t={team_name}"
    try:
        response = requests.get(url)
        if response.status_code == 429:
            print(f"  [!] Rate limit hit (ID lookup). Sleeping 30s...")
            time.sleep(30)
            return None
        data = response.json()
        if data.get('teams'):
            return data['teams'][0]['idTeam']
    except: pass
    return None

def fetch_h2h_iteration(t1, t2, season):
    url = f"{BASE_URL}/searchevents.php?e={t1}_vs_{t2}&s={season}"
    try:
        response = requests.get(url)
        if response.status_code == 429:
            print(f"  [!] ERROR 429: Throttled. Pausing for 30s...")
            time.sleep(30)
            return None
        return response.json().get('event')
    except: return None

def get_full_h2h(t1_csv, t2_csv):
    all_found = []
    for season in SEASONS:
        # Check Home vs Away
        res_a = fetch_h2h_iteration(t1_csv, t2_csv, season)
        if res_a: all_found.extend(res_a)
        # Check Away vs Home (Reverse Lookup)
        res_b = fetch_h2h_iteration(t2_csv, t1_csv, season)
        if res_b: all_found.extend(res_b)
        time.sleep(0.8)

    if not all_found:
        print(f"  [-] No H2H data for {t1_csv} vs {t2_csv}")
        return [""] * 5

    all_found.sort(key=lambda x: x.get('dateEvent', ''), reverse=True)

    aligned = []
    for event in all_found[:5]:
        h_score = event.get('intHomeScore')
        a_score = event.get('intAwayScore')
        status = event.get('strStatus', '')

        if status == "Match Postponed":
            aligned.append("P")
            continue

        if h_score is None or a_score is None: continue
        
        api_home = event.get('strHomeTeam', '').strip().lower()
        if api_home == t1_csv.lower():
            aligned.append(f"{h_score}-{a_score}")
        else:
            aligned.append(f"{a_score}-{h_score}")
    
    while len(aligned) < 5: aligned.append("")
    return aligned

def get_form_list(team_id, team_name):
    if not team_id: return [""] * 5
    url = f"{BASE_URL}/eventslast.php?id={team_id}"
    try:
        response = requests.get(url)
        if response.status_code == 429:
            print(f"  [!] ERROR 429: Throttled (Form). Sleeping...")
            time.sleep(30)
            return [""] * 5
            
        events = response.json().get('results')
        if not events: return [""] * 5

        res = []
        for e in events[:5]:
            status = e.get('strStatus', '')
            
            # --- Specific Status Checks ---
            if status == "Match Postponed":
                res.append("P")
                continue
            if status == "Match Cancelled":
                res.append("C")
                continue

            h_s = e.get('intHomeScore')
            a_s = e.get('intAwayScore')
            if h_s is None or a_s is None:
                res.append("?") # Unknown result
                continue
            
            h, a = int(h_s), int(a_s)
            if e.get('idHomeTeam') == team_id:
                res.append("W" if h > a else ("L" if h < a else "D"))
            else:
                res.append("W" if a > h else ("L" if a < h else "D"))
        
        while len(res) < 5: res.append("")
        return res
    except: return [""] * 5

def run_analysis():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    h2h_rows = []
    form_results = {} 

    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Team1') or not row.get('Team2'): continue
            t1, t2 = row['Team1'].strip(), row['Team2'].strip()
            
            print(f"Processing: {t1} vs {t2}")

            # 1. H2H Processing
            scores = get_full_h2h(t1, t2)
            h2h_rows.append([t1, t2] + scores)

            # 2. Form Processing
            for t_name in [t1, t2]:
                if t_name not in form_results:
                    tid = get_team_id(t_name)
                    f_list = get_form_list(tid, t_name)
                    # Game 1 (Latest) on right
                    form_results[t_name] = [t_name, f_list[4], f_list[3], f_list[2], f_list[1], f_list[0]]
            
            time.sleep(0.5)

    with open(H2H_OUTPUT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Home Team', 'Away Team', 'Score 1', 'Score 2', 'Score 3', 'Score 4', 'Score 5'])
        writer.writerows(h2h_rows)

    with open(FORM_OUTPUT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Team', 'Game 5', 'Game 4', 'Game 3', 'Game 2', 'Game 1'])
        writer.writerows(list(form_results.values()))

    print(f"\nProcessing complete.\nFiles created: {H2H_OUTPUT}, {FORM_OUTPUT}")

if __name__ == "__main__":
    run_analysis()
