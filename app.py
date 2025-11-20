import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ---- Page setup ----
st.set_page_config(page_title="Gaming Platform Simulator", layout="wide")

# ---- Reduce vertical spacing globally ----
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .element-container {margin-bottom: 0rem;}
    .stPlotlyChart {margin-bottom: -20px;}
    div[data-testid="column"] {padding: 0.2rem;}
</style>
""", unsafe_allow_html=True)

st.title("Gaming Platform Simulator – Linear Demand & Revenue Visualization")

st.markdown("""
**Two-Sided Market Example: Gaming Platform**  
Demand is linear and reacts to prices and network effects.  
Revenue shown as shaded rectangles below demand curves.
""")

# ---- Fixed axis for stable plots ----
MAX_Q = 2000
MAX_P = 60

# ---- Default values ----
a_A, b_A, a_B, b_B = 1000, 30, 150, 2
gamma_A, gamma_B = 0.5, 1.2
p_A, p_B = 5, 25


# ---- Linear demand solver ----
def solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B):
    A = np.array([[1, -gamma_A], [-gamma_B, 1]])
    B = np.array([a_A - b_A * p_A, a_B - b_B * p_B])
    Q_A, Q_B = np.linalg.solve(A, B)
    return max(Q_A, 0), max(Q_B, 0)


Q_A, Q_B = solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B)
R_A, R_B = p_A * Q_A, p_B * Q_B

# ---- Prepare demand curves ----
Q_range = np.linspace(0, MAX_Q, 200)
P_A_curve = np.maximum(0, (a_A + gamma_A * Q_B - Q_range) / b_A)
P_B_curve = np.maximum(0, (a_B + gamma_B * Q_A - Q_range) / b_B)


# ---- Plotting function ----
def draw_panel(ax, Q_curve, Q_star, P_star, title):
    ax.plot(Q_range, Q_curve, color="black", linewidth=1.8)
    rect = patches.Rectangle(
        (0, 0),
        min(Q_star, MAX_Q),
        min(P_star, MAX_P),
        facecolor='orange',
        alpha=0.3,
        edgecolor='black',
        linewidth=2
    )
    ax.add_patch(rect)
    ax.scatter(min(Q_star, MAX_Q), min(P_star, MAX_P), color="red", s=60)
    ax.set_xlim(0, MAX_Q)
    ax.set_ylim(0, MAX_P)
    ax.set_title(title, fontsize=13)
    ax.set_xlabel("Quantity (Q)")
    ax.set_ylabel("Price (P)")
    ax.grid(True)
    fig.tight_layout(pad=0.5)


# ---- Visualization (side-by-side, with minimal padding) ----
col1, col2 = st.columns([1,1])

with col1:
    fig, ax = plt.subplots(figsize=(5,3.2))
    draw_panel(ax, P_A_curve, Q_A, p_A, "Side A: Consumers (Gamers)")
    st.pyplot(fig, use_container_width=True)

with col2:
    fig, ax = plt.subplots(figsize=(5,3.2))
    draw_panel(ax, P_B_curve, Q_B, p_B, "Side B: Developers")
    st.pyplot(fig, use_container_width=True)


# ---- KPI / metrics below images ----
colk1, colk2, colk3 = st.columns(3)
colk1.metric("Consumers (Q_A)", f"{Q_A:.1f}")
colk2.metric("Developers (Q_B)", f"{Q_B:.1f}")
colk3.metric("Total Revenue", f"{(R_A+R_B):.1f}")

st.write("")  # minimal spacing only


# ---- Controls BELOW visualization ----
st.subheader("Adjust Platform Parameters")

colA, colB = st.columns(2)

with colA:
    st.markdown("**Side A: Consumers**")
    a_A = st.slider("Base demand a_A", 500, 2000, 1000, 50)
    b_A = st.slider("Price sensitivity b_A", 10, 50, 30, 1)
    gamma_A = st.slider("γ_A (Effect of games on users)", 0.0, 2.0, 0.5, 0.1)
    p_A = st.slider("Price to Consumers (p_A)", 0.0, 20.0, 5.0, 0.5)

with colB:
    st.markdown("**Side B: Developers**")
    a_B = st.slider("Base demand a_B", 50, 400, 150, 10)
    b_B = st.slider("Price sensitivity b_B", 1, 10, 2, 1)
    gamma_B = st.slider("γ_B (Effect of users on developers)", 0.0, 3.0, 1.2, 0.1)
    p_B = st.slider("Price to Developers (p_B)", 0.0, 50.0, 25.0, 1.0)

st.caption("Minimal spacing, full visual area, teaching-optimized layout.")
