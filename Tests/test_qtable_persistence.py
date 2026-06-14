import os, json
from brain import BrainAgent

# نقشه ۳×۳
map_grid = [[0,0,0],[0,0,0],[0,0,0]]
targets = [(2,2)]

# مغز اول را با ۱۰۰ دوره تمرین بدهیم
brain1 = BrainAgent(map_grid, targets, epsilon=0.2)  # کمی کاوش در حین یادگیری
print("Training brain1 for 100 episodes...")
for _ in range(100):
    cur = (0,0)
    for step in range(10):  # حداکثر ۱۰ قدم برای رسیدن به هدف
        state = brain1.get_state(cur)
        action = brain1.choose_action(state)
        # شبیه‌سازی حرکت (ساده)
        if action == "UP":    nxt = (cur[0]-1, cur[1])
        elif action == "DOWN": nxt = (cur[0]+1, cur[1])
        elif action == "LEFT": nxt = (cur[0], cur[1]-1)
        elif action == "RIGHT": nxt = (cur[0], cur[1]+1)
        # محدود کردن به نقشه
        if not (0 <= nxt[0] < 3 and 0 <= nxt[1] < 3):
            nxt = cur
        reward = 50 if nxt == (2,2) else -1
        next_state = brain1.get_state(nxt)
        brain1.last_state = state
        brain1.last_action = action
        brain1.update_q_value(reward, next_state)
        cur = nxt
        if cur == (2,2):
            break

# ذخیره
os.makedirs("q_tables", exist_ok=True)
brain1.save_q_table("q_tables/test_team.json")

# مغز دوم (خالی) و بارگذاری حافظه
brain2 = BrainAgent(map_grid, targets, epsilon=0.0)
brain2.load_q_table("q_tables/test_team.json")

# تست: بهترین اقدام از (0,0)
state = brain2.get_state((0,0))
best = max(brain2.q_table[state], key=brain2.q_table[state].get)
print(f"Best action from (0,0) after loading memory: {best}")

if best in ["RIGHT", "DOWN"]:
    print("✅ Test passed. Memory persistence works perfectly.")
else:
    print(f"❌ Unexpected action: {best}")