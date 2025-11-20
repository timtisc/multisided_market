import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Gaming Platform Simulator", layout="wide")

st.title("Gaming Platform Simulator – Linear Demand & Revenue Visualization")

st.markdown("""
**Visualizing a Two-Sided Gaming Platform**  
- **Side A:** Gamers (Consumers) – high price sensitivity  
- **Side B:** Game Developers – lower price sensitivity, pay fees  
- Linear demand, revenue = p × Q, with network effects.
""")

# --- Fixed axis ranges for stable plots ---
MAX_Q = 2000  
MAX_P = 60   

# --- Default realistic platform values (gaming platform) ---
a_A = 1000; b_A = 30; a_B = 150; b_B = 2
gamma_A = 0.5; gamma_B = 1.2
p_A = 5; p_B = 25


# ---- Demand solver ----
def solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B):
    A = np.array([[1, -gamma_A], [-gamma_B, 1]])
    B = np.array([a_A - b_A * p_A, a_B - b_B * p_B])
    Q_A, Q_B = np.linalg.solve(A, B)
    return max(Q_A, 0), max(Q_B, 0)

Q_A, Q_B = solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B)

# ---- Revenue ----
R_A, R_B = p_A * Q_A, p_B * Q_B

# ---- Demand curves (linear) ----
Q_range = np.linspace(0, MAX_Q, 200)

P_A_curve = np.maximum(0, (a_A + gamma_A * Q_B - Q_range) / b_A)
P_B_curve = np.maximum(0, (a_B + gamma_B * Q_A - Q_range) / b_B)


# ---- Plotting function ----
def draw_panel(ax, Q_curve, Q_star, P_star, label):
    ax.plot(Q_range, Q_curve, label="Demand Curve", color="black", linewidth=1.8)
    
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
    
    ax.scatter(min(Q_star, MAX_Q), min(P_star, MAX_P), color="red", s=70)

    ax.set_xlim(0, MAX_Q)
    ax.set_ylim(0, MAX_P)
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price p")
    ax.set_title(label)
    ax.grid(True)

# ---- Visualization (side-by-side) ----
col1, col2 = st.columns(2)

with col1:
    figA, axA = plt.subplots(figsize=(6,4))
    draw_panel(axA, P_A_curve, Q_A, p_A, "Side A: Consumers (Gamers)")
    st.pyplot(figA, use_container_width=True)

with col2:
    figB, axB = plt.subplots(figsize=(6,4))
    draw_panel(axB, P_B_curve, Q_B, p_B, "Side B: Developers")
    st.pyplot(figB, use_container_width=True)


# ---- KPI Summary ----
st.markdown("### Key Performance Indicators")
colk1, colk2, colk3 = st.columns(3)
colk1.metric("Consumers (Q_A)", f"{Q_A:.1f}")
colk2.metric("Developers (Q_B)", f"{Q_B:.1f}")
colk3.metric("Total Revenue", f"{(R_A+R_B):.1f}")

st.divider()

# ---- Sliders Below Visualization ----
st.markdown("## Adjust Platform Parameters")

colA, colB = st.columns(2)

with colA:
    st.subheader("Side A (Consumers / Gamers)")
    a_A = st.slider("Base demand a_A", 500, 2000, 1000, 50)
    b_A = st.slider("Price sensitivity b_A", 10, 50, 30, 1)
    gamma_A = st.slider("γ_A (Effect of games on users)", 0.0, 2.0, 0.5, 0.1)
    p_A = st.slider("Platform price to Consumers (p_A)", 0.0, 20.0, 5.0, 0.5)

with colB:
    st.subheader("Side B (Game Developers)")
    a_B = st.slider("Base demand a_B", 50, 300, 150, 10)
    b_B = st.slider("Price sensitivity b_B", 1, 10, 2, 1)
    gamma_B = st.slider("γ_B (Effect of users on developers)", 0.0, 3.0, 1.2, 0.1)
    p_B = st.slider("Platform price to Developers (p_B)", 0.0, 50.0, 25.0, 1.0)

st.caption("Adjust parameters below — plots remain fixed and stable above.")
