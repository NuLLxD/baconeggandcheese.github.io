import requests
import json
import os
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "fw_battlefield_data.json")
ESI_BASE = "https://esi.evetech.net/latest"
BF_VP_THRESHOLD = 1900 

FACTIONS = {500001: "Caldari", 500002: "Minmatar", 500003: "Amarr", 500004: "Gallente"}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                d = json.load(f)
                # Ensure structure exists
                for key in ["vp_history", "timers", "last_systems", "recent_spikes", "active_battlefields"]:
                    if key not in d: d[key] = {} if "history" in key or "timers" in key or "systems" in key or "active" in key else []
                return d
        except: pass
    return {"vp_history": {}, "timers": {}, "last_systems": {}, "recent_spikes": [], "active_battlefields": {}, "last_updated": ""}

def main():
    data = load_data()
    now_utc = datetime.now(timezone.utc)
    
    try:
        response = requests.get(f"{ESI_BASE}/fw/systems/", timeout=10).json()
        ids = [sys['solar_system_id'] for sys in response]
        name_res = requests.post(f"{ESI_BASE}/universe/names/", json=ids).json()
        name_map = {item['id']: item['name'] for item in name_res}

        # Clear active flags to re-scan
        # We only mark them 'Active' if they are currently in the 3-hour window
        # or if the window has passed but no new spike has occurred.
        
        for sys in response:
            if sys.get('contested') != 'frontline': continue
            
            sid = str(sys['solar_system_id'])
            vp = sys.get('victory_points', 0)
            fid = sys.get('occupier_faction_id')
            fname = FACTIONS.get(fid, "Unknown")
            sname = name_map.get(int(sid), sid)

            if sid in data["vp_history"]:
                diff = vp - data["vp_history"][sid]
                
                # BATTLEFIELD DETECTED (Spike)
                if diff >= BF_VP_THRESHOLD:
                    # Set the 3-hour cooldown
                    data["timers"][fname] = (now_utc + timedelta(hours=3)).isoformat()
                    # Store the system
                    data["last_systems"][fname] = sname
                    # This faction is now in COOLDOWN, not "Available"
                    data["active_battlefields"][fname] = False 
                    
                    entry = f"[{now_utc.strftime('%H:%M')}] BF: {sname} ({fname})"
                    data["recent_spikes"].append(entry)
                    if len(data["recent_spikes"]) > 10: data["recent_spikes"].pop(0)

            data["vp_history"][sid] = vp

        data["last_updated"] = now_utc.isoformat()

        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    main()