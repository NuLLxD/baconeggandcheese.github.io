import requests
import json
import os
from datetime import datetime, timedelta, timezone

# Pathing relative to the script location (the 'eve' folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "fw_battlefield_data.json")
ESI_BASE = "https://esi.evetech.net/latest"
BF_VP_THRESHOLD = 1900 

FACTIONS = {500001: "Caldari", 500002: "Minmatar", 500003: "Amarr", 500004: "Gallente"}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"vp_history": {}, "timers": {}, "last_systems": {}, "recent_spikes": [], "last_updated": ""}

def main():
    data = load_data()
    now_utc = datetime.now(timezone.utc)
    
    try:
        # Fetch current FW state
        response = requests.get(f"{ESI_BASE}/fw/systems/", timeout=10).json()
        
        # Name mapping
        ids = [sys['solar_system_id'] for sys in response]
        name_res = requests.post(f"{ESI_BASE}/universe/names/", json=ids).json()
        name_map = {item['id']: item['name'] for item in name_res}

        for sys in response:
            if sys.get('contested') != 'frontline': continue
            
            sid = str(sys['solar_system_id'])
            vp = sys.get('victory_points', 0)
            fid = sys.get('occupier_faction_id')
            fname = FACTIONS.get(fid, "Unknown")
            sname = name_map.get(int(sid), sid)

            # Detection Logic
            if sid in data["vp_history"]:
                if vp - data["vp_history"][sid] >= BF_VP_THRESHOLD:
                    # Update Cooldown Timer
                    data["timers"][fname] = (now_utc + timedelta(hours=3)).isoformat()
                    # Store the specific system name
                    data["last_systems"][fname] = sname
                    
                    # Log it
                    entry = f"[{now_utc.strftime('%H:%M')}] BF: {sname} ({fname})"
                    data["recent_spikes"].append(entry)
                    if len(data["recent_spikes"]) > 5: data["recent_spikes"].pop(0)

            data["vp_history"][sid] = vp

        data["last_updated"] = now_utc.isoformat()

        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    main()