"""
Autonomously Generated Sovereign Swarm Agent
Generation: 2
"""
import numpy as np

class BoundedCropModel:
    def __init__(self, L=75.0, p0=50.0, alpha=0.0400, beta=0.120):
        self.L, self.p0, self.alpha, self.beta = float(L), float(p0), float(alpha), float(beta)

    def transform(self, prices: np.ndarray) -> np.ndarray:
        p = np.maximum(np.asarray(prices, dtype=np.float32), 0.0)
        z = np.clip(self.beta * (p - self.p0), -40.0, 35.0)
        hinge = (np.maximum(z, 0.0) + np.log1p(np.exp(-np.abs(z)))) / self.beta
        damp = np.log1p(self.alpha * p) / (1.0 + 0.35 * self.alpha * p)
        return self.L * (1.0 - np.exp(-(hinge * (1.0 + damp)) / self.L))


class SovereignSwarmAgent:
    def __init__(self):
        self.corn_min_nitrogen = 50.00
        self.cash_reserve_floor = 2500.00
        self.chi2_gate = 9.4877
        self.generation = 2
        self.step_count = 0

        # Kinematic parameters
        self.grid_res = 32
        self.step_size = 0.045
        self.tau = 0.80
        self.k_agent = 0.020
        self.r_core_sq = 0.025 ** 2
        self.max_repulsion = 2.0
        self.price_model = BoundedCropModel()

        self.xs = np.linspace(0.0, 1.0, self.grid_res, dtype=np.float32)
        self.ys = np.linspace(0.0, 1.0, self.grid_res, dtype=np.float32)
        self.X, self.Y = np.meshgrid(self.xs, self.ys)
        self.h = 1.0 / (self.grid_res - 1)

    def compute_mutual_repulsion(self, pos: np.ndarray) -> np.ndarray:
        M = pos.shape[0]
        if M <= 1:
            return np.zeros_like(pos)
        diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
        dist_sq = np.sum(diff ** 2, axis=-1) + self.r_core_sq
        factor = (2.0 * self.k_agent) / (dist_sq ** 2)
        np.fill_diagonal(factor, 0.0)
        raw = np.sum(diff * factor[:, :, np.newaxis], axis=1)
        mags = np.linalg.norm(raw, axis=-1, keepdims=True)
        scale = np.minimum(1.0, self.max_repulsion / (mags + 1e-6))
        return raw * scale

    def compute_swarm_kinematics(self, observation: dict) -> list:
        harvesters = observation.get("harvesters", [])
        if not harvesters:
            return []

        markets = observation.get("markets", [])
        raw_prices = np.array([m.get("price", 50.0) for m in markets], dtype=np.float32)
        b_prices = self.price_model.transform(raw_prices) if len(markets) else np.array([], dtype=np.float32)

        U = np.full((self.grid_res, self.grid_res), 50.0, dtype=np.float32)
        for idx, mkt in enumerate(markets):
            d = np.sqrt((self.X - mkt["x"]) ** 2 + (self.Y - mkt["y"]) ** 2 + 0.002)
            U -= (b_prices[idx] * 0.8) / (1.0 + 8.0 * d)

        hazards = observation.get("hazards", [])
        for b in hazards:
            proj_x = np.clip(b["x"] + b.get("vx", 0.0) * self.tau, 0.02, 0.98)
            proj_y = np.clip(b["y"] + b.get("vy", 0.0) * self.tau, 0.02, 0.98)
            r_sq = (b.get("radius", 0.12) ** 2) * 0.45
            dist_sq = (self.X - proj_x) ** 2 + (self.Y - proj_y) ** 2
            U += (35.0 * b.get("severity", 1.0)) * np.exp(-dist_sq / (2.0 * r_sq))

        edge_x = np.minimum(self.X, 1.0 - self.X)
        edge_y = np.minimum(self.Y, 1.0 - self.Y)
        U += np.maximum(0.0, 0.05 - edge_x) * 150.0
        U += np.maximum(0.0, 0.05 - edge_y) * 150.0

        grad_y, grad_x = np.gradient(U, self.h, self.h)
        pos = np.array([[h["x"], h["y"]] for h in harvesters], dtype=np.float32)
        rep = self.compute_mutual_repulsion(pos)

        hx = np.clip(pos[:, 0] * (self.grid_res - 1), 0.0, self.grid_res - 1.001)
        hy = np.clip(pos[:, 1] * (self.grid_res - 1), 0.0, self.grid_res - 1.001)
        x0, y0 = hx.astype(np.int32), hy.astype(np.int32)
        x1, y1 = np.minimum(self.grid_res - 1, x0 + 1), np.minimum(self.grid_res - 1, y0 + 1)
        tx, ty = hx - x0, hy - y0

        dx = (1 - tx)*(1 - ty)*grad_x[y0, x0] + tx*(1 - ty)*grad_x[y0, x1] + (1 - tx)*ty*grad_x[y1, x0] + tx*ty*grad_x[y1, x1]
        dy = (1 - tx)*(1 - ty)*grad_y[y0, x0] + tx*(1 - ty)*grad_y[y0, x1] + (1 - tx)*ty*grad_y[y1, x0] + tx*ty*grad_y[y1, x1]

        norm = np.hypot(dx, dy) + 1e-6
        tot = np.column_stack((-dx / norm, -dy / norm)) + rep
        tot_mags = np.linalg.norm(tot, axis=-1, keepdims=True) + 1e-6
        disp = (tot / tot_mags) * self.step_size

        actions = []
        for i, h in enumerate(harvesters):
            actions.append({"id": h["id"], "target_vector": [float(disp[i, 0]), float(disp[i, 1])], "mode": "CONTINUOUS_FLOW"})
        return actions

    def __call__(self, observation, configuration=None):
        self.step_count += 1
        
        # 1. Swarm Kinematics Execution (Moves harvesters across the map)
        if "harvesters" in observation and observation["harvesters"]:
            return self.compute_swarm_kinematics(observation)

        # 2. Agronomic Plot Actions (Fallback if running in pure agricultural plot arena)
        plots = observation.get("plots", [])
        cash = observation.get("cash", 15000.0)
        actions = {"plot_actions": [], "market_orders": []}

        for i, p in enumerate(plots):
            idx = p.get("id", i)
            if p.get("crop", "Empty") == "Empty":
                if p.get("nitrogen", 50.0) < self.corn_min_nitrogen or cash < self.cash_reserve_floor:
                    actions["plot_actions"].append({"plot_index": idx, "action": "PLANT_SOYBEANS"})
                else:
                    actions["plot_actions"].append({"plot_index": idx, "action": "PLANT_CORN"})
            elif p.get("stage", 0.0) >= 1.0:
                actions["plot_actions"].append({"plot_index": idx, "action": "HARVEST"})
            else:
                actions["plot_actions"].append({"plot_index": idx, "action": "WAIT"})

        return actions

_agent_instance = SovereignSwarmAgent()

def agent(observation, configuration=None):
    return _agent_instance(observation, configuration)
