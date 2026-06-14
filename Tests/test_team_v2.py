import sys
from team import Team

# نقشه ۳×۳ با یک هدف در (2,2)
map_grid = [[0,0,0],[0,0,0],[0,0,4]]

# تیم با epsilon=0.2 برای کاوش
team = Team("TestTeam", (0,0), map_grid, alpha=0.5, gamma=0.9, epsilon=0.2)

print("Training team for 50 episodes...")
steps_per_episode = []
for episode in range(50):
    team.reset()
    step_count = 0
    while not team.has_won():
        result = team.step()
        step_count += 1
        if step_count > 100:  # safety
            break
    steps_per_episode.append(step_count)

# بررسی یادگیری: میانگین قدم‌های ۱۰ اپیزود آخر کمتر از ۱۰ اپیزود اول باشد
first_10_avg = sum(steps_per_episode[:10]) / 10
last_10_avg = sum(steps_per_episode[-10:]) / 10
print(f"Average steps (first 10 episodes): {first_10_avg:.1f}")
print(f"Average steps (last 10 episodes): {last_10_avg:.1f}")

if last_10_avg < first_10_avg:
    print("✅ Test passed. Team learned to reach target faster.")
else:
    print("❌ Test failed. No improvement detected. Might need more training.")