import requests
import os
import json
import hmac
import hashlib
import base64
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
HISTORY_FILE = "scan_history.json"

# --- YOUR API CREDENTIALS ---

AUDD_TOKEN = os.getenv("AUDD_TOKEN")
ACR_HOST = os.getenv("ACR_HOST")
ACR_KEY = os.getenv("ACR_KEY")
ACR_SECRET = os.getenv("ACR_SECRET")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_to_history(file_name, result_data):
    history = load_history()
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "file": file_name,
        "result": result_data
    })
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_confidence(score):
    if score is None:
        return 75, "POSSIBLE MATCH"
    if score >= 90:
        return score, "HIGH CONFIDENCE MATCH"
    elif score >= 60:
        return score, "POSSIBLE MATCH"
    else:
        return score, "WEAK MATCH"

def check_audd(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.audd.io/',
            data={'api_token': AUDD_TOKEN, 'return': 'apple_music,spotify'},
            files={'file': f}
        )
    result = response.json()
    if result.get('status') == 'success' and result.get('result'):
        song = result['result']
        return {
            "found": True,
            "title": song.get('title', 'Unknown'),
            "artist": song.get('artist', 'Unknown'),
            "album": song.get('album', 'Unknown'),
            "label": song.get('label', 'Unknown'),
            "score": song.get('score', None)
        }
    return {"found": False}

def check_acr(file_path):
    timestamp = str(int(time.time()))
    string_to_sign = f"POST\n/v1/identify\n{ACR_KEY}\naudio\n1\n{timestamp}"
    signature = base64.b64encode(
        hmac.new(ACR_SECRET.encode(), string_to_sign.encode(), hashlib.sha1).digest()
    ).decode()

    with open(file_path, 'rb') as f:
        response = requests.post(
            f"https://{ACR_HOST}/v1/identify",
            files={'sample': f},
            data={
                'access_key': ACR_KEY,
                'sample_bytes': os.path.getsize(file_path),
                'timestamp': timestamp,
                'signature': signature,
                'data_type': 'audio',
                'signature_version': '1'
            }
        )
    result = response.json()
    status = result.get('status', {})
    if status.get('code') == 0:
        music = result['metadata']['music'][0]
        return {
            "found": True,
            "title": music.get('title', 'Unknown'),
            "artist": music['artists'][0]['name'] if music.get('artists') else 'Unknown',
            "album": music.get('album', {}).get('name', 'Unknown'),
            "score": music.get('score', None)
        }
    return {"found": False}

def check_loop(file_path):
    file_path = file_path.strip().strip('"').strip("'").strip('&').strip()

    if not os.path.exists(file_path):
        print(f"\n❌ File not found: {file_path}")
        print("Tip: Try typing the path manually instead of drag & drop.")
        return

    file_name = os.path.basename(file_path)
    print(f"\n✅ File found: {file_name}")
    print("Checking with AudD...")
    audd = check_audd(file_path)
    print("Checking with ACRCloud...")
    acr = check_acr(file_path)

    both_found = audd['found'] and acr['found']
    one_found = audd['found'] or acr['found']

    if both_found:
        score = max(
            audd.get('score') or 75,
            acr.get('score') or 75
        )
        confidence, label = get_confidence(score)
        title = audd.get('title', acr.get('title', 'Unknown'))
        artist = audd.get('artist', acr.get('artist', 'Unknown'))
        album = audd.get('album', acr.get('album', 'Unknown'))
        record_label = audd.get('label', 'Unknown')

        print(f"\n🔴 BOTH APIS AGREE — {label} ({confidence}%)")
        print(f"Title:  {title}")
        print(f"Artist: {artist}")
        print(f"Album:  {album}")
        print(f"Label:  {record_label}")
        print("\n❌ HIGH RISK — Do not use without clearing the sample.")

        save_to_history(file_name, {
            "status": "copyright_detected",
            "confidence": confidence,
            "label": label,
            "title": title,
            "artist": artist,
            "verified_by": "Both AudD and ACRCloud"
        })

    elif one_found:
        found = audd if audd['found'] else acr
        source = "AudD" if audd['found'] else "ACRCloud"
        confidence, label = get_confidence(found.get('score'))

        print(f"\n⚠️  ONE API FLAGGED THIS — {label} ({confidence}%)")
        print(f"Detected by: {source}")
        print(f"Title:  {found.get('title', 'Unknown')}")
        print(f"Artist: {found.get('artist', 'Unknown')}")
        print("\n⚠️  MEDIUM RISK — Could be a false positive.")
        print("   Consider consulting a music lawyer before release.")

        save_to_history(file_name, {
            "status": "possible_copyright",
            "confidence": confidence,
            "label": label,
            "title": found.get('title', 'Unknown'),
            "artist": found.get('artist', 'Unknown'),
            "verified_by": source
        })

    else:
        print("\n✅ Both APIs found no copyright match.")
        print("This loop appears safe to use — but always double-check.")

        save_to_history(file_name, {
            "status": "clear",
            "confidence": 0,
            "label": "NO MATCH",
            "verified_by": "Both AudD and ACRCloud"
        })

def show_history():
    history = load_history()
    if not history:
        print("\nNo scans yet.")
        return
    print(f"\n{'='*40}")
    print("       SCAN HISTORY")
    print(f"{'='*40}")
    for item in history:
        print(f"\n📅 {item['date']}")
        print(f"🎵 File: {item['file']}")
        status = item['result']['status']
        if status == 'copyright_detected':
            print(f"🔴 HIGH RISK — {item['result'].get('title', 'Unknown')} by {item['result'].get('artist', 'Unknown')}")
            print(f"   Verified by: {item['result'].get('verified_by', 'AudD')}")
        elif status == 'possible_copyright':
            print(f"⚠️  MEDIUM RISK — {item['result'].get('title', 'Unknown')} by {item['result'].get('artist', 'Unknown')}")
            print(f"   Detected by: {item['result'].get('verified_by', 'AudD')}")
        else:
            print("✅ Clear — No match found")
    print(f"\n{'='*40}")

while True:
    print("\n==============================")
    print("     Welcome to Sample-Safe")
    print("==============================")
    print("1. Check a loop")
    print("2. View scan history")
    print("3. Exit")

    choice = input("\nChoose an option (1/2/3): ").strip()

    if choice == '1':
        file_path = input("\nEnter the path to your audio file: ")
        check_loop(file_path)
    elif choice == '2':
        show_history()
    elif choice == '3':
        print("\nGoodbye!")
        break
    else:
        print("\n❌ Invalid option. Try again.")