# 🔬 Technical Deep Dive – RACE v2.0

This document provides a detailed explanation of the key technical decisions, algorithms, and architecture behind the RACE v2.0 AI Rescue Tournament.

---

## 1. State Representation

In Q-Learning, the **state** must capture enough information for the agent to make a good decision, while keeping the state space small enough to learn efficiently. The state used for target selection in `BrainAgent` is defined as:
state = (worker_x, worker_y, dir_x, dir_y)

Where:
- `worker_x`, `worker_y`: Current position of the worker on the grid.
- `dir_x`: Direction vector to the nearest target on the x-axis. Coded as `-1` (target is left/above), `0` (same column), or `+1` (target is right/below).
- `dir_y`: Same concept for the y-axis.

**Why this representation?**
- It gives the agent a rough sense of where the nearest target is without fixing it to a specific coordinate pair, allowing generalization across similar situations.
- It keeps the state space manageable. An 8×8 grid with 4 direction combinations has at most `64 × 9 = 576` possible states per target configuration — trivial for a Q-table.

---

## 2. Reward Design

The reward function is crucial: it shapes the agent's behavior. The rewards are defined in `Team.step()` and passed to `BrainAgent.learn_from_outcome()`:

| Event         | Reward | Purpose                                                    |
|---------------|--------|------------------------------------------------------------|
| Rescued target| +50    | Strong positive reinforcement for completing the objective |
| Stepped on rubble | -10| Penalty for inefficient path choices                       |
| Stepped on fire   | -50| Heavy penalty for dangerous moves (causes respawn)         |
| Blocked (wall)    | -5 | Small penalty to discourage impossible moves               |
| Normal step       | -1 | Small cost per action to encourage shorter paths           |

**Design rationale:**
- The large gap between rescuing (+50) and the highest penalty (-50) ensures the agent remains goal-driven even after major setbacks.
- The per-step penalty of -1 is the key to solving the "cold start" problem: it pressures the agent to find the shortest path rather than wandering aimlessly.

---

## 3. Why Q-Learning?

Several reinforcement learning approaches were considered. Q-Learning was chosen for these reasons:

- **Model-Free**: The agent learns directly from interaction with the environment, without needing a pre-built model of the map or opponent behavior. This makes it robust to new or procedurally generated maps.
- **Tabular Simplicity**: The state space is small enough to use a dictionary-based Q-table (no neural network required). This means:
  - No heavy dependencies (NumPy, TensorFlow).
  - Instant learning updates.
  - The Q-table can be easily saved to and loaded from JSON — perfect for persistent memory.
- **Off-Policy Learning**: The agent can learn from exploratory actions (epsilon-greedy) while still improving a deterministic optimal policy.

**Why not other algorithms?**
- **Deep Q-Network (DQN)**: Overkill for a small discrete grid. Would add complexity and dependencies without improving performance.
- **SARSA**: On-policy and more conservative. In a competitive game with aggressive penalties (fire = -50), the risk-taking allowed by Q-Learning's off-policy nature leads to faster adaptation.
- **Monte Carlo Methods**: Require full episodes to update. Q-Learning's step-by-step updates fit naturally in a turn-based game.

---

## 4. Hybrid Architecture (Q-Learning + BFS)

A unique aspect of RACE v2.0 is the separation of concerns between **target selection** and **path planning**:

- **Q-Learning** decides *which* target to go for next (strategic decision).
- **Breadth-First Search (BFS)** calculates *how* to get there once a target is chosen (tactical execution).

**Why split them?**
- BFS guarantees the shortest path to a known goal — there's nothing to "learn" about it.
- Q-Learning handles the high-level choice under uncertainty: should the agent go for a closer target with a rubble-trapped path, or a slightly farther one that's safer? This is where learning pays off.

This hybrid approach proved more effective than either method alone. A pure Q-Learning agent took too long to learn basic navigation, while a pure BFS agent was predictable and couldn't adapt to the shared-map competition.

---

## 5. Training Regimen: Solving the Cold Start

A known problem in RL is the **cold start**: untrained agents behave randomly and poorly, which is unacceptable for a demo or competition.

RACE v2.0 solves this with **silent pretraining**:

1. On first launch, each team runs 50 full training episodes in the background (≈5–10 seconds total, depending on hardware).
2. During pretraining, the GUI is not updated and no visualization is shown — the agent simply explores, collects rewards, and updates its Q-table.
3. After pretraining, the Q-table is saved to `q_tables/<team_name>.json`.
4. On subsequent launches, the saved Q-table is loaded, and the agent starts with expert-level performance.

This transforms the first user experience from "random flailing" to "strategic competition."

---

## 6. Handling the Shared Map

In v2.0, both teams race on the same physical grid. When a target is rescued:
- The `RaceManager` sets that cell to `0` in the shared grid.
- All teams' Q-Learning agents have that target removed from their internal list.

This required careful synchronization: the `Team.step()` method returns an event (`"rescued"`), and the `RaceManager.step_turn()` method intercepts it, performs the grid update, and propagates the removal to all teams' brains. This ensures a single source of truth for the map state.

---

## 7. Key Hyperparameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `alpha` (learning rate) | 0.3 | Relatively high to adapt quickly in a dynamic environment with 2 competing teams |
| `gamma` (discount factor) | 0.9 | Values future rewards strongly — encourages planning ahead |
| `epsilon` (exploration) | 0.2 | 20% random actions during training to discover new strategies |
| Pretraining episodes | 50 | Balances quick startup with sufficient learning |

These values were tuned experimentally. A higher `alpha` (0.3 instead of the usual 0.1) helps the agent react faster when the other team steals a target it was heading toward.

---

## 8. Code Structure (Separation of Concerns)

The learning logic is cleanly separated from the game logic:

| Module | Responsibility |
|--------|----------------|
| `brain.py` | Q-Learning logic: `choose_best_target()`, `learn_from_outcome()`, Q-table save/load |
| `team.py` | Orchestration: calls Brain for target, gets BFS path, executes moves via Worker, translates events to rewards |
| `race_manager.py` | Shared grid management, turn ordering, win detection, calls pretraining |
| `worker.py` | Grid movement and event reporting (`"rescued"`, `"hit_rubble"`, etc.) |
| `gui.py` | PyQt5 visualization — no learning logic at all |

This strict separation means the AI can be upgraded (e.g., to DQN) without touching the UI, or the UI can be redesigned without affecting the learning algorithm.

---

*For questions or discussions about the architecture, feel free to open an issue on GitHub.*