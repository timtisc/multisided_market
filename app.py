import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Two-Sided Market Simulator",
                   layout="wide")

st.title("Two-Sided Platform Simulator")

st.markdown(
    "Adjust price elasticities and cross-side effects to see how "
    "demand and **revenue rectangles** (price × quantity) change on each side "
    "of the platform."
)

# -----------------------------
# Sidebar: parameters
# -----------------------------
st.sidebar.header("Parameters")

# Base demand (scale)
k_A = st.sidebar.slider("Base demand k_A (side A)", 10.0, 200.0, 100.0, 10.0)
k_B = st.sidebar.slider("Base demand k_B (side B)", 10.0, 200.0, 80.0, 10.0)

# Prices (still used for KPIs, but visuals show optimal price rectangle)
p_A = st.sidebar.slider("Current price p_A (side A)", 0.0, 50.0, 10.0, 1.0)
p_B = st.sidebar.slider("Current price p_B (side B)", 0.0, 50.0, 5.0, 1.0)

# Own-price elasticities (negative)
beta_A = st.sidebar.slider("Price elasticity β_A (side A)", -3.0, 0.0, -1.0, 0.1)
beta_B = st.sidebar.slider("Price elasticity β_B (side B)", -3.0, 0.0, -1.5, 0.1)

# Cross-side effects
gamma_A = st.sidebar.slider("Cross-side effect γ_A (A reacts to B)", 0.0, 2.0, 0.5, 0.1)
gamma_B = st.sidebar.slider("Cross-side effect γ_B (B reacts to A)", 0.0, 2.0, 0.8, 0.1)

# -----------------------------
# Core model
# -----------------------------
def solve_demands(k_A, k_B, p_A, p_B,
                  beta_A, beta_B, gamma_A, gamma_B,
                  max_iter=500, tol=1e-6):
    """Simple fixed-point iteration for Q_A and Q_B."""
    Q_A, Q_B = 50.0, 50.0  # starting guess
    for _ in range(max_iter):
        new_Q_A = k_A * (p_A ** beta_A) * ((Q_B + 1.0) ** gamma_A)
        new_Q_B = k_B * (p_B ** beta_B) * ((Q_A + 1.0) ** gamma_B)
        if abs(new_Q_A - Q_A) < tol and abs(new_Q_B - Q_B) < tol:
            Q_A, Q_B = new_Q_A, new_Q_B
            break
        Q_A, Q_B = new_Q_A, new_Q_B
    return max(Q_A, 0.0), max(Q_B, 0.0)

# Equilibrium for current slider values (for KPIs)
Q_A, Q_B = solve_demands(k_A, k_B, p_A, p_B,
                          beta_A, beta_B, gamma_A, gamma_B)

R_A = p_A * Q_A
R_B = p_B * Q_B
R_total = R_A + R_B

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Side A quantity (Q_A at current p_A)", f"{Q_A:,.1f}")
col2.metric("Side B quantity (Q_B at current p_B)", f"{Q_B:,.1f}")
col3.metric("Total platform revenue (at current prices)", f"{R_total:,.1f}")

st.divider()

# -----------------------------
# Price grids for plotting
# -----------------------------
grid_points = 40
# Make sure the grid is stable and >= some minimum range
max_pA = max(p_A * 2, 10.0)
max_pB = max(p_B * 2, 10.0)

pA_grid = np.linspace(0.1, max_pA, grid_points)
pB_grid = np.linspace(0.1, max_pB, grid_points)

# For each price point, recompute equilibrium quantities
QA_grid = []
RA_grid = []

for pA_val in pA_grid:
    QA_val, QB_val = solve_demands(k_A, k_B, pA_val, p_B,
                                   beta_A, beta_B, gamma_A, gamma_B)
    QA_grid.append(QA_val)
    RA_grid.append(pA_val * QA_val)

QB_grid = []
RB_grid = []

for pB_val in pB_grid:
    QA_val, QB_val = solve_demands(k_A, k_B, p_A, pB_val,
                                   beta_A, beta_B, gamma_A, gamma_B)
    QB_grid.append(QB_val)
    RB_grid.append(pB_val * QB_val)

QA_grid = np.array(QA_grid)
QB_grid = np.array(QB_grid)
RA_grid = np.array(RA_grid)
RB_grid = np.array(RB_grid)

# Find revenue-maximizing price for each side (optimal price)
idx_opt_A = int(np.argmax(RA_grid))
idx_opt_B = int(np.argmax(RB_grid))

pA_opt = pA_grid[idx_opt_A]
QA_opt = QA_grid[idx_opt_A]
RA_opt = RA_grid[idx_opt_A]

pB_opt = pB_grid[idx_opt_B]
QB_opt = QB_grid[idx_opt_B]
RB_opt = RB_grid[idx_opt_B]

# Fix axis limits so graphics don't "jump"
xmax_A = max_pA
ymax_A = max(QA_grid.max(), QA_opt, Q_A) * 1.1 if QA_grid.max() > 0 else 1.0

xmax_B = max_pB
ymax_B = max(QB_grid.max(), QB_opt, Q_B) * 1.1 if QB_grid.max() > 0 else 1.0

# -----------------------------
# Layout: two plots side by side
# -----------------------------
c1, c2 = st.columns(2)

# ---- Side A plot ----
with c1:
    st.subheader("Side A: demand curve and revenue rectangle at optimal price")

    figA, axA = plt.subplots(figsize=(5, 4))

    # Demand curve
    axA.plot(pA_grid, QA_grid, label="Demand Q_A", linewidth=1.5)
    axA.set_xlabel("Price p_A")
    axA.set_ylabel("Quantity Q_A")

    # Revenue rectangle: from origin (0,0) up to (pA_opt, QA_opt)
    rectA = patches.Rectangle(
        (0, 0),
        pA_opt,
        QA_opt,
        alpha=0.2
    )
    axA.add_patch(rectA)

    # Mark optimal price on x-axis
    axA.axvline(pA_opt, linestyle="--", linewidth=1)
    axA.text(
        pA_opt,
        ymax_A * 0.95,
        f"p*_A ≈ {pA_opt:.1f}",
        rotation=90,
        va="top",
        ha="right",
        fontsize=8
    )

    # Current price marker (for comparison)
    axA.axvline(p_A, linestyle=":", linewidth=1)
    axA.text(
        p_A,
        ymax_A * 0.6,
        "current p_A",
        rotation=90,
        va="top",
        ha="right",
        fontsize=8
    )

    axA.set_xlim(0, xmax_A)
    axA.set_ylim(0, ymax_A)
    axA.legend(loc="upper right", fontsize="small")

    st.pyplot(figA)

# ---- Side B plot ----
with c2:
    st.subheader("Side B: demand curve and revenue rectangle at optimal price")

    figB, axB = plt.subplots(figsize=(5, 4))

    # Demand curve
    axB.plot(pB_grid, QB_grid, label="Demand Q_B", linewidth=1.5)
    axB.set_xlabel("Price p_B")
    axB.set_ylabel("Quantity Q_B")

    # Revenue rectangle: from origin (0,0) up to (pB_opt, QB_opt)
    rectB = patches.Rectangle(
        (0, 0),
        pB_opt,
        QB_opt,
        alpha=0.2
    )
    axB.add_patch(rectB)

    # Mark optimal price on x-axis
    axB.axvline(pB_opt, linestyle="--", linewidth=1)
    axB.text(
        pB_opt,
        ymax_B * 0.95,
        f"p*_B ≈ {pB_opt:.1f}",
        rotation=90,
        va="top",
        ha="right",
        fontsize=8
    )

    # Current price marker for comparison
    axB.axvline(p_B, linestyle=":", linewidth=1)
    axB.text(
        p_B,
        ymax_B * 0.6,
        "current p_B",
        rotation=90,
        va="top",
        ha="right",
        fontsize=8
    )

    axB.set_xlim(0, xmax_B)
    axB.set_ylim(0, ymax_B)
    axB.legend(loc="upper right", fontsize="small")

    st.pyplot(figB)

st.caption(
    "For each side, the shaded rectangle shows revenue = p* × Q(p*) at the **revenue-maximizing price p***. "
    "The demand curve is drawn as usual; the current price is indicated by a dotted vertical line."
)
