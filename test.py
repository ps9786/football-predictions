import os
import requests
import csv

# 1. Configuration
API_KEY = os.getenv("API_FOOTBALL")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    'x-apisports-key': API_KEY
}

def get_team_id(team_name):
    """Searches for a team name and returns its unique ID."""
    url = f"{BASE_URL}/teams"
    params = {'search': team_name}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    
    if data['response']:
        # Returns the first match found
        team = data['response'][0]['team']
        print(f"Found: {team['name']} (ID: {team['id']})")
        return team['id']
    else:
        print(f"Team '{team_name}' not found.")
        return None

def get_h2h_data(id1, id2):
    """Gets historical match data between two specific team IDs."""
    url = f"{BASE_URL}/fixtures/headtohead"
    params = {'h2h': f"{id1}-{id2}", 'last': 10} # Get last 10 meetings
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()['response']

def save_to_csv(matches, filename="h2h_results.csv"):
    """Parses API response and saves to a CSV file."""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Header
        writer.writerow(['Date', 'Home Team', 'Away Team', 'Score', 'Winner'])
        
        for match in matches:
            fixture = match['fixture']
            teams = match['teams']
            goals = match['goals']
            
            winner = "Draw"
            if teams['home']['winner']: winner = teams['home']['name']
            elif teams['away']['winner']: winner = teams['away']['name']
            
            writer.writerow([
                fixture['date'][:10],
                teams['home']['name'],
                teams['away']['name'],
                f"{goals['home']}-{goals['away']}",
                winner
            ])
    print(f"Successfully saved results to {filename}")

# --- Execution Flow ---
if __name__ == "__main__":
    if not API_KEY:
        print("Error: API-FOOTBALL environment variable not set.")
    else:
        team_a_input = input("Enter first team: ")
        team_b_input = input("Enter second team: ")

        id_a = get_team_id(team_a_input)
        id_b = get_team_id(team_b_input)

        if id_a and id_b:
            print(f"Fetching head-to-head data...")
            h2h_results = get_h2h_data(id_a, id_b)
            save_to_csv(h2h_results)
