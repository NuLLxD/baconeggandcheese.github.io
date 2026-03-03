import requests
import time
import json
import os
from datetime import datetime, timedelta, timezone

# --- Configuration ---
DATA_FILE = "fw_battlefield_data.json"
ESI_BASE = "https://esi.evetech.net/latest"
API_POLL_INTERVAL = 60  
BF_VP_THRESHOLD = 1900 

FACTIONS = {500001: "Caldari", 500002: "Minmatar", 500003: "Amarr", 500004: "Gallente"}

# ANSI Colors for CLI
GREEN = "\033[92m"
RESET = "\033[0m"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"vp_history": {}, "timers": {}, "recent_spikes": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    data_store = load_data()
    now_utc = datetime.now(timezone.utc)
    
    # 1. Fetch ESI
    try:
        response = requests.get(f"{ESI_BASE}/fw/systems/", timeout=10).json()
        name_res = requests.post(f"{ESI_BASE}/universe/names/", 
                                 json=[s['solar_system_id'] for s in response]).json()
        name_map = {item['id']: item['name'] for item in name_res}
    except: return

    # 2. Process Battlefields
    for sys in response:
        if sys.get('contested') != 'frontline': continue
        
        sys_id = str(sys['solar_system_id'])
        current_vp = sys.get('victory_points', 0)
        faction = FACTIONS.get(sys.get('occupier_faction_id'), "Unknown")

        if sys_id in data_store["vp_history"]:
            diff = current_vp - data_store["vp_history"][sys_id]
            if diff >= BF_VP_THRESHOLD:
                # NEW SPIKE: Start 3-hour cooldown
                data_store["timers"][faction] = (now_utc + timedelta(hours=3)).isoformat()
                timestamp = datetime.now().strftime('%H:%M')
                data_store["recent_spikes"].append(f"[{timestamp}] BF: {name_map[int(sys_id)]} ({faction})")
                if len(data_store["recent_spikes"]) > 5: data_store["recent_spikes"].pop(0)

        data_store["vp_history"][sys_id] = current_vp

    save_data(data_store)

    # 3. Enhanced UI Output
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"EVE TIME: {now_utc.strftime('%H:%M:%S')}\n" + "-"*40)
    
    for fac_id, fac_name in FACTIONS.items():
        timer_raw = data_store["timers"].get(fac_name)
        if timer_raw:
            t_dt = datetime.fromisoformat(timer_raw).replace(tzinfo=timezone.utc)
            if t_dt > now_utc:
                rem = str(t_dt - now_utc).split('.')[0]
                print(f"{fac_name:10}: COOLDOWN ({rem} left)")
            else:
                print(f"{GREEN}{fac_name:10}: BF AVAILABLE{RESET}")
        else:
            print(f"{GREEN}{fac_name:10}: BF AVAILABLE{RESET}")

if __name__ == "__main__":
    main()
