#trigger

import requests
from datetime import datetime
import pytz


def get_today_matches():
    today = datetime.now(pytz.timezone("Africa/Lagos")).strftime('%Y-%m-%d')
    print(f"[get_today_matches] Today's date: {today}")

    url = f"https://api.football-data.org/v4/matches?dateFrom={today}&dateTo={today}"

    headers = {
        "X-Auth-Token": API_TOKEN
    }

    response = requests.get(url, headers=headers)

    print(f"[get_today_matches] Status code: {response.status_code}")

    if response.status_code != 200:
        print("[get_today_matches] ERROR:", response.text)
        return []
    
    data = response.json()
    print(f"[get_today_matches] Total matches found: {len(data.get('matches', []))}")

    return data.get("matches", [])

def format_matches(matches):
    print(f"[format_matches] Formatting {len(matches)} matches...")

    top_matches = []

    for match in matches:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        competition = match["competition"]["name"]

        utc_time = match["utcDate"]

        kickoff = datetime.fromisoformat(utc_time.replace('Z', '+00:00')) \
            .astimezone(pytz.timezone("Africa/Lagos")) \
            .strftime('%H:%M')
        
        match_text = f"{home} vs {away} ({competition}) at {kickoff} NG"
        print(f"[format_matches] Match: {match_text}")

        top_matches.append(match_text)

    return top_matches[:5]

def send_telegram_message(message):
    print("[send_telegram_message] Sending message to telegram...")
    print("[sned_telegram_message] Message content:\n", message)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)

    print(f"[send_telegram_message] Response status: {response.status_code}")

def main():
    print("[main] Starting script...")
    matches = get_today_matches()

    if matches: 
        message = "*Today's Top Football Matches* \n\n" + "\n".join(format_matches(matches))
    else: 
        message = "No top matches today."

    send_telegram_message(message)
    print("[main] Done.")

if __name__ == "__main__":
    main()