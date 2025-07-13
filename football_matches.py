import requests
import os
from datetime import datetime
import pytz

API_TOKEN = os.getenv('API_TOKEN')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def delete_webhook():
    if not BOT_TOKEN:
        print("[delete_webhook] ERROR: BOT_TOKEN is not set")
        return False
    print("[delete_webhook] Deleting Telegram webhook...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    try:
        response = requests.get(url, timeout=10)
        print(f"[delete_webhook] Response: {response.json()}")
        return response.json().get('ok', False)
    except requests.RequestException as e:
        print(f"[delete_webhook] ERROR: Failed to delete webhook - {e}")
        return False

def get_today_matches():
    if not API_TOKEN:
        print("[get_today_matches] ERROR: API_TOKEN is not set")
        return []

    today = datetime.now(pytz.timezone("Africa/Lagos")).strftime('%Y-%m-%d')
    print(f"[get_today_matches] Today's date: {today}")

    url = f"https://api.football-data.org/v4/matches?dateFrom={today}&dateTo={today}"
    headers = {"X-Auth-Token": API_TOKEN}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"[get_today_matches] Status code: {response.status_code}")
        if response.status_code != 200:
            print("[get_today_matches] ERROR:", response.text)
            return []
        data = response.json()
        print(f"[get_today_matches] Full response: {data}")  # Debug full response
        matches = data.get('matches', [])
        print(f"[get_today_matches] Total matches found: {len(matches)}")
        return matches
    except requests.RequestException as e:
        print(f"[get_today_matches] ERROR: Failed to fetch matches - {e}")
        return []

def format_matches(matches):
    print(f"[format_matches] Formatting {len(matches)} matches...")
    top_matches = []

    for i, match in enumerate(matches, 1):
        home = match.get("homeTeam", {}).get("name", "Unknown")
        away = match.get("awayTeam", {}).get("name", "Unknown")
        competition = match.get("competition", {}).get("name", "Unknown")
        utc_time = match.get("utcDate", "")

        try:
            kickoff = datetime.fromisoformat(utc_time.replace('Z', '+00:00')) \
                .astimezone(pytz.timezone("Africa/Lagos")) \
                .strftime('%Y-%m-%d %I:%M %p NG')  # Updated to 12-hour with AM/PM
            match_text = f"{i}. {home} vs {away} ({competition}) at {kickoff}"
            print(f"[format_matches] Match: {match_text}")
            top_matches.append(match_text)
        except ValueError as e:
            print(f"[format_matches] ERROR: Invalid date format for {home} vs {away} - {e}")
            continue

    return top_matches[:5]

def send_telegram_message(message):
    print("[send_telegram_message] Sending message to Telegram...")
    print("[send_telegram_message] Message content:\n", message)

    if not BOT_TOKEN or not CHAT_ID:
        print("[send_telegram_message] ERROR: BOT_TOKEN or CHAT_ID is not set")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"[send_telegram_message] Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"[send_telegram_message] ERROR: {response.json()}")
    except requests.RequestException as e:
        print(f"[send_telegram_message] ERROR: Failed to send message - {e}")

def main():
    print("[main] Starting script...")
    if not all([API_TOKEN, BOT_TOKEN, CHAT_ID]):
        print("[main] ERROR: One or more environment variables are missing")
        return
    if 'message_sent' not in globals():  # Prevent duplicate sends
        global message_sent
        message_sent = True
        delete_webhook()
        matches = get_today_matches()
        if matches:
            message = "*Today's Top Football Matches* \n\n" + "\n".join(format_matches(matches))
        else:
            message = "No top matches today."
        send_telegram_message(message)
    print("[main] Done.")

if __name__ == "__main__":
    main()