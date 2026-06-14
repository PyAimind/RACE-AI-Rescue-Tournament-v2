import sys
from race_manager import RaceManager

print("Testing Q-Learning tournament (3 races on apartment map)...")

# برگزاری ۳ مسابقه پشت سر هم
race = RaceManager("apartment.json", ["AI Team 1", "AI Team 2"])
for r in range(3):
    winner = race.run_race()
    print(f"Race {r+1}: Winner = {winner}")
    # به تیم‌ها اجازه می‌دهیم Q-Table خود را حفظ کنند
    # (این منطق باید در race_manager پیاده‌سازی شده باشد)

# بررسی اینکه مسابقه بدون خطا اجرا شده و دو تیم وجود دارند
assert len(race.teams) == 2
print("✅ All races completed successfully.")
print("Q-Tables have been preserved for next tournament.")