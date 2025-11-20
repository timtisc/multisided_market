import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Two-Sided Market Simulator",
                   layout="wide")

st.title("Two-Sided Platform Simulator")

st.markdown(
    "Adjust price elasticities and cross-side effects and see how "
    "demand and revenue change for each side of the platform."
)

# -----------------------------
# Sidebar: parameters
# -----------------------------
st.sidebar.header("Parameters")

# Base demand (scale)
k_A = st.sidebar.slider("Base demand k_A (side A)", 10.0, 200.0, 100.0, 10.0)
k_B = st.sidebar.slider("Base demand k_B (side B)", 10.0, 200.0, 80.0, 10.0)

# Prices
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

# Equilibrium for current slider values
Q_A, Q_B = solve_demands(k_A, k_B, p_A, p_B,
                          beta_A, beta_B, gamma_A, gamma_B)

R_A = p_A * Q_A
R_B = p_B * Q_B
R_total = R_A + R_B

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Side A quantity", f"{Q_A:,.1f}")
col2.metric("Side B quantity", f"{Q_B:,.1f}")
col3.metric("Total platform revenue", f"{R_total:,.1f}")

st.divider()

# -----------------------------
# Price–demand & revenue curves
# -----------------------------

# Price grids for plotting
grid_points = 40
pA_grid = np.linspace(0.1, max(p_A * 2, 1.0), grid_points)
pB_grid = np.linspace(0.1, max(p_B * 2, 1.0), grid_points)

# For each price point, recompute equilibrium quantities
QA_grid = []
QB_grid_for_A = []
RA_grid = []

for pA in pA_grid:
    QA, QB = solve_demands(k_A, k_B, pA, p_B,
                           beta_A, beta_B, gamma_A, gamma_B)
    QA_grid.append(QA)
    QB_grid_for_A.append(QB)
    RA_grid.append(pA * QA)

QB_grid = []
QA_grid_for_B = []
RB_grid = []

for pB_ in pB_grid:
    QA, QB = solve_demands(k_A, k_B, p_A, pB_,
                           beta_A, beta_B, gamma_A, gamma_B)
    QB_grid.append(QB)
    QA_grid_for_B.append(QA)
    RB_grid.append(pB_ * QB)

# -----------------------------
# Layout: two plots side by side
# -----------------------------
c1, c2 = st.columns(2)

# ---- Side A plot ----
with c1:
    st.subheader("Side A: demand and revenue vs. price")
    figA, axA1 = plt.subplots()

    # Demand curve
    axA1.plot(pA_grid, QA_grid, label="Demand Q_A")
    axA1.set_xlabel("Price p_A")
    axA1.set_ylabel("Quantity Q_A")

    # Current price marker
    axA1.axvline(p_A, linestyle="--")
    axA1.text(p_A, max(QA_grid) * 0.95, "current p_A",
              rotation=90, va="top", ha="right")

    # Revenue curve on second axis
    axA2 = axA1.twinx()
    axA2.plot(pA_grid, RA_grid, linestyle="--", label="Revenue R_A")
    axA2.set_ylabel("Revenue R_A")

    # Compact legend
    lines, labels = axA1.get_legend_handles_labels()
    lines2, labels2 = axA2.get_legend_handles_labels()
    axA1.legend(lines + lines2, labels + labels2, loc="upper right", fontsize="small")

    st.pyplot(figA)

# ---- Side B plot ----
with c2:
    st.subheader("Side B: demand and revenue vs. price")
    figB, axB1 = plt.subplots()

    # Demand curve
    axB1.plot(pB_grid, QB_grid, label="Demand Q_B")
    axB1.set_xlabel("Price p_B")
    axB1.set_ylabel("Quantity Q_B")

    # Current price marker
    axB1.axvline(p_B, linestyle="--")
    axB1.text(p_B, max(QB_grid) * 0.95, "current p_B",
              rotation=90, va="top", ha="right")

    # Revenue curve on second axis
    axB2 = axB1.twinx()
    axB2.plot(pB_grid, RB_grid, linestyle="--", label="Revenue R_B")
    axB2.set_ylabel("Revenue R_B")

    lines, labels = axB1.get_legend_handles_labels()
    lines2, labels2 = axB2.get_legend_handles_labels()
    axB1.legend(lines + lines2, labels + labels2, loc="upper right", fontsize="small")

    st.pyplot(figB)

st.caption(
    "Each panel shows how quantity (solid line) and revenue (dashed line) change with price "
    "on one side of the platform, holding the other side's price fixed at its current value."
)
