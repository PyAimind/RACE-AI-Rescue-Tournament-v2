import sys
from tournament import Tournament

try:
    print("[1] Creating tournament with 3 maps...")
    maps = ["apartment.json", "hospital.json", "metro.json"]
    teams = ["Blue", "Red"]
    tournament = Tournament(maps, teams)
    print(f"    OK: Tournament created. Maps: {maps}, Teams: {teams}")

    print("[2] Running tournament...")
    champion = tournament.run()
    print(f"    OK: Tournament finished. Champion: {champion}")

    print("[3] Final leaderboard (tokens):")
    leaderboard = tournament.get_leaderboard()
    for name, tokens in leaderboard.items():
        print(f"    {name}: {tokens} token(s)")

    assert champion in teams, "Champion must be one of the teams"
    print("Test passed.")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)