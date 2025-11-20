import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Two-Sided Market Simulator", layout="wide")

st.title("Two-Sided Platform Simulator – Revenue Rectangles (Two-Sided Markets)")

st.markdown(
    "Price elasticity, cross-side network effects, and **visual revenue rectangles**."
)

# Sidebar Inputs
st.sidebar.header("Parameters")

k_A = st.sidebar.slider("Base demand k_A (Side A)", 50, 200, 120, 10)
k_B = st.sidebar.slider("Base demand k_B (Side B)", 50, 200, 100, 10)

p_A = st.sidebar.slider("Current price p_A (Side A)", 0.0, 50.0, 15.0, 1.0)
p_B = st.sidebar.slider("Current price p_B (Side B)", 0.0, 50.0, 12.0, 1.0)

beta_A = st.sidebar.slider("Own-price elasticity β_A", -3.0, 0.0, -1.2, 0.1)
beta_B = st.sidebar.slider("Own-price elasticity β_B", -3.0, 0.0, -1.6, 0.1)

gamma_A = st.sidebar.slider("Cross-side network effect γ_A (A reacts to B)", 0.0, 2.0, 0.9, 0.1)
gamma_B = st.sidebar.slider("Cross-side network effect γ_B (B reacts to A)", 0.0, 2.0, 1.1, 0.1)


def solve_demands(k_A, k_B, p_A, p_B, beta_A, beta_B, gamma_A, gamma_B):
    Q_A, Q_B = 80.0, 80.0
    for _ in range(200):
        new_Q_A = k_A * p_A**beta_A * (Q_B + 1)**gamma_A
        new_Q_B = k_B * p_B**beta_B * (Q_A + 1)**gamma_B
        if abs(new_Q_A - Q_A) < 1e-6 and abs(new_Q_B - Q_B) < 1e-6:
            break
        Q_A, Q_B = new_Q_A, new_Q_B
    return max(Q_A,0), max(Q_B,0)


Q_A, Q_B = solve_demands(k_A, k_B, p_A, p_B, beta_A, beta_B, gamma_A, gamma_B)

col1, col2, col3 = st.columns(3)
col1.metric("Quantity Side A", f"{Q_A:.1f}")
col2.metric("Quantity Side B", f"{Q_B:.1f}")
col3.metric("Total Revenue", f"{(p_A*Q_A+p_B*Q_B):.1f}")

st.divider()

# Price ranges for revenue optimization
prices_A = np.linspace(1, max(50, p_A*2), 60)
prices_B = np.linspace(1, max(50, p_B*2), 60)

QA_list, RA_list = [], []
QB_list, RB_list = [], []

for p1 in prices_A:
    QA, _ = solve_demands(k_A, k_B, p1, p_B, beta_A, beta_B, gamma_A, gamma_B)
    QA_list.append(QA)
    RA_list.append(p1 * QA)

for p2 in prices_B:
    _, QB = solve_demands(k_A, k_B, p_A, p2, beta_A, beta_B, gamma_A, gamma_B)
    QB_list.append(QB)
    RB_list.append(p2 * QB)

idx_opt_A = np.argmax(RA_list)
idx_opt_B = np.argmax(RB_list)

pA_opt, QA_opt = prices_A[idx_opt_A], QA_list[idx_opt_A]
pB_opt, QB_opt = prices_B[idx_opt_B], QB_list[idx_opt_B]

st.markdown("### Revenue Rectangles at Optimal Price (per Side)")

# Side-by-side visuals
c1, c2 = st.columns(2)

def plot_demand_with_rectangle(fig, ax, prices, quantities, p_opt, Q_opt, label):
    ax.plot(quantities, prices, linewidth=1.8, label="Demand Curve")
    ax.add_patch(patches.Rectangle(
        (0, 0),
        Q_opt,
        p_opt,
        linewidth=1.5,
        edgecolor='black',
        facecolor='orange',
        alpha=0.35
    ))
    ax.scatter(Q_opt, p_opt, color="black")
    ax.annotate(f"Revenue = p×Q\n({p_opt:.1f}×{Q_opt:.1f}={p_opt*Q_opt:.1f})",
                xy=(Q_opt, p_opt), xytext=(Q_opt*0.6, p_opt*1.1),
                arrowprops=dict(arrowstyle="->"))
    ax.set_xlabel("Quantity (Q)")
    ax.set_ylabel("Price (p)")
    ax.set_title(label)
    ax.set_xlim(0, max(quantities)*1.1)
    ax.set_ylim(0, max(prices)*1.1)
    ax.grid(True)

# Side A
with c1:
    figA, axA = plt.subplots(figsize=(5,4))
    plot_demand_with_rectangle(figA, axA, prices_A, QA_list, pA_opt, QA_opt, "Side A")
    st.pyplot(figA)

# Side B
with c2:
    figB, axB = plt.subplots(figsize=(5,4))
    plot_demand_with_rectangle(figB, axB, prices_B, QB_list, pB_opt, QB_opt, "Side B")
    st.pyplot(figB)

st.caption("Both revenue rectangles adjust dynamically with cross-side effects.")
