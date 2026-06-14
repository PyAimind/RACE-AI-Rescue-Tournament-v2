import sys
from worker import WorkerAgent

# نقشه ۱×۶: آزاد، آزاد، آوار، آتش، دود، هدف
grid = [[0, 0, 1, 2, 3, 4]]

print("Testing Worker events...")

# مورد ۱: حرکت به سلول آزاد
w = WorkerAgent(0, 0, grid)
pos, event = w.move("RIGHT")
assert pos == (0, 1) and event == "moved", f"Failed: {pos}, {event}"
print("[OK] Free cell -> 'moved'")

# مورد ۲: حرکت به آوار (۱)
pos, event = w.move("RIGHT")  # به (0,2) که rubble است
assert pos == (0, 2) and event == "hit_rubble", f"Failed: {pos}, {event}"
print("[OK] Rubble cell -> 'hit_rubble'")

# مورد ۳: آتش بدون اجازه مغز -> بلوکه شدن
pos, event = w.move("RIGHT", brain_allow=False)  # به (0,3) آتش
assert pos == (0, 2) and event == "blocked", f"Failed: {pos}, {event}"
print("[OK] Fire without brain_allow -> 'blocked'")

# مورد ۴: آتش با اجازه مغز -> ریسپان و رویداد hit_fire
pos, event = w.move("RIGHT", brain_allow=True)
assert pos == (0, 0) and event == "hit_fire", f"Failed: {pos}, {event}"
print("[OK] Fire with brain_allow -> 'hit_fire' and respawn at (0,0)")

# مورد ۵: حرکت به دود (3) -> moved
# ابتدا کارگر را دستی در (0,4) که دود است قرار می‌دهیم (تست سریع)
w.x, w.y = 0, 4  # سلول دود
pos, event = w.move("RIGHT")  # به هدف (0,5) می‌رود؟ اما grid 0..5, target at index 5
# چون grid[0][5] هدف است، event باید rescued بدهد، نه moved. 
# برای تست دود، از حرکت به یک سلول دیگر استفاده می‌کنیم. مثلاً move LEFT به آتش (0,3)؟ آن هم hit_fire.
# پس یک نقشه دیگر با دود و سپس آزاد می‌سازیم.
grid2 = [[0, 3, 0]]
w2 = WorkerAgent(0, 0, grid2)
pos, event = w2.move("RIGHT")  # به سلول دود (0,1)
assert pos == (0, 1) and event == "moved", f"Failed: {pos}, {event}"
print("[OK] Smoke cell -> 'moved'")

# مورد ۶: رسیدن به هدف -> rescued
# از همان نقشه اصلی: کارگر را در (0,5) هدف قرار دهیم؟ اما کارگر تازه ریسپان شده. 
# نقشه اصلی: target در (0,5). کارگر را با تنظیم دستی در (0,4) دود می‌گذاریم و یک بار RIGHT می‌زنیم.
w.x, w.y = 0, 4  # دود
pos, event = w.move("RIGHT")  # به (0,5) هدف
assert pos == (0, 5) and event == "rescued", f"Failed: {pos}, {event}"
print("[OK] Target cell -> 'rescued'")

print("\n✅ All worker event tests passed.")