import os
import requests
from datetime import datetime, timedelta

# Configuration
API_KEY = os.getenv("API_FOOTBALL")
BASE_URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-apisports-key': API_KEY}

def get_upcoming_fixtures(league_id):
    # Calculate date range (Today to 30 days from now)
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    params = {
        'league': league_id,
        'season': 2025,  # Update to current season year
        'from': start_date,
        'to': end_date
    }
    
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    print(response.json())
    data = response.json()
    
    if not data.get('response'):
        print("No fixtures found for this range.")
        return []

    print(f"{'Fixture ID':<12} | {'Home Team':<20} | {'Away Team':<20} | {'Date'}")
    print("-" * 70)
    
    fixture_list = []
    for item in data['response']:
        f_id = item['fixture']['id']
        home = item['teams']['home']['name']
        away = item['teams']['away']['name']
        date = item['fixture']['date'][:10]
        
        print(f"{f_id:<12} | {home:<20} | {away:<20} | {date}")
        fixture_list.append(f_id)
    
    return fixture_list

if __name__ == "__main__":
    # Example: Premier League (ID: 39)
    upcoming_ids = get_upcoming_fixtures(39)
