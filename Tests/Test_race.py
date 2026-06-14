import sys
from race_manager import RaceManager

try:
    print("[1] Running tournament on all 3 maps...")
    maps = ["apartment.json", "hospital.json", "metro.json"]
    
    for m in maps:
        print(f"\n--- Map: {m} ---")
        race = RaceManager(m, ["Blue", "Red"])
        winner = race.run_race()
        
        for team in race.teams:
            print(f"  {team.name}: rescued={team.rescued}, steps={team.steps_taken}, score={race.calculate_score(team):.1f}")
        print(f"  Winner: {winner} (+1 token)")
    
    print("\n[2] Test passed.")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)