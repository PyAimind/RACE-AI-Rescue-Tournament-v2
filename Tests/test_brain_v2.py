import sys
import random
from brain import BrainAgent

# نقشه ۳×۳ با یک هدف
map_grid = [[0,0,0],[0,0,0],[0,0,0]]
targets = [(2,2)]

# مغز با epsilon=0.2 برای کاوش در حین یادگیری (بعداً صفر می‌کنیم)
brain = BrainAgent(map_grid, targets, alpha=0.5, gamma=0.9, epsilon=0.2)

# مسیر صحیح از (0,0) به (2,2)
actions_path = ["RIGHT", "RIGHT", "DOWN", "DOWN"]
positions = [(0,0), (0,1), (0,2), (1,2), (2,2)]

print("Training agent for 100 episodes...")
for episode in range(100):
    # شروع از خانه اول
    cur_pos = (0,0)
    total_reward = 0
    for step in range(4):
        state = brain.get_state(cur_pos)
        action = brain.choose_action(state)  # epsilon-greedy explores
        # محاسبه موقعیت بعدی بر اساس action (فارغ از مسیر بهینه)
        if action == "UP":    next_pos = (cur_pos[0]-1, cur_pos[1])
        elif action == "DOWN":  next_pos = (cur_pos[0]+1, cur_pos[1])
        elif action == "LEFT":  next_pos = (cur_pos[0], cur_pos[1]-1)
        elif action == "RIGHT": next_pos = (cur_pos[0], cur_pos[1]+1)
        
        # محدود کردن به نقشه (اگر خارج شد، برگرد)
        if not (0 <= next_pos[0] < 3 and 0 <= next_pos[1] < 3):
            next_pos = cur_pos  # جریمه می‌شود
        
        # تعیین پاداش
        if next_pos == (2,2):
            reward = 50
        else:
            reward = -1
        
        next_state = brain.get_state(next_pos)
        brain.update_q_value(reward, next_state)
        
        cur_pos = next_pos
        if cur_pos == (2,2):
            break  # به هدف رسیده

# حالا مغز را قطعی می‌کنیم
brain.epsilon = 0.0

# تست در (0,0)
state = brain.get_state((0,0))
best = max(brain.q_table[state], key=brain.q_table[state].get)
print(f"Best action from (0,0) after training: {best}")

# انتظار داریم RIGHT یا DOWN (حرکت به سمت هدف)
if best in ["RIGHT", "DOWN"]:
    print("✅ Test passed. Agent learned to move towards target.")
else:
    print(f"❌ Test failed. Unexpected action: {best}")