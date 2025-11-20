import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Gaming Platform Simulator", layout="wide")

st.title("Gaming Platform Simulator – Linear Demand Model (Two-Sided Market)")

st.markdown(
    """
    **Two-Sided Market Example: Gaming Platform**

    - **Side A: Consumers** → highly price-sensitive, large base  
    - **Side B: Game Developers** → fewer, less elastic, revenue contributors  
    - Demand is linear, reacts to **own price** and **network effects from the other side**
    - Revenues visualized as **rectangles = price × quantity**  
    """
)

# 🌎 Fixed axis display ranges (stable view)
MAX_Q = 2000   # Quantity axis max
MAX_P = 60     # Price axis max

# Sidebar Parameters
st.sidebar.header("Platform Parameters")

# Demand base levels (starting values where full plot is visible)
a_A = st.sidebar.slider("Base demand a_A (Consumers)", 500, 2000, 1000, 50)
b_A = st.sidebar.slider("Price sensitivity b_A (Consumers)", 10, 50, 30, 1)
a_B = st.sidebar.slider("Base demand a_B (Developers)", 50, 300, 150, 10)
b_B = st.sidebar.slider("Price sensitivity b_B (Developers)", 1, 10, 2, 1)

# Cross-side effects
gamma_A = st.sidebar.slider("γ_A (Effect of games on consumers)", 0.0, 2.0, 0.5, 0.1)
gamma_B = st.sidebar.slider("γ_B (Effect of users on developers)", 0.0, 3.0, 1.2, 0.1)

# Prices
p_A = st.sidebar.slider("Price to Consumers (p_A)", 0.0, 20.0, 5.0, 0.5)
p_B = st.sidebar.slider("Price to Developers (p_B)", 0.0, 50.0, 25.0, 1.0)


# Linear demand solver
def solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B):
    A = np.array([[1, -gamma_A], [-gamma_B, 1]])
    B = np.array([a_A - b_A * p_A, a_B - b_B * p_B])
    Q_A, Q_B = np.linalg.solve(A, B)
    return max(Q_A, 0), max(Q_B, 0)


Q_A, Q_B = solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B)

# Revenue
R_A, R_B = p_A * Q_A, p_B * Q_B

# KPI metrics
col1, col2, col3 = st.columns(3)
col1.metric("Consumers (Q_A)", f"{Q_A:.1f}")
col2.metric("Developers (Q_B)", f"{Q_B:.1f}")
col3.metric("Total Revenue", f"{(R_A+R_B):.1f}")

st.divider()

# Create linear demand curves with shifts
Q_range = np.linspace(0, MAX_Q, 200)

P_A_curve = np.maximum(0, (a_A + gamma_A * Q_B - Q_range) / b_A)
P_B_curve = np.maximum(0, (a_B + gamma_B * Q_A - Q_range) / b_B)


# 🎨 Helper to draw curves + rectangle
def draw_panel(ax, Q_curve, Q_star, P_star, label):
    ax.plot(Q_range, Q_curve, label="Demand Curve", color="black", linewidth=1.8)

    # Draw revenue rectangle p×Q
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

    # Mark equilibrium point
    ax.scatter(min(Q_star, MAX_Q), min(P_star, MAX_P), color="red", s=70)

    # Labels and formatting
    ax.set_xlim(0, MAX_Q)
    ax.set_ylim(0, MAX_P)
    ax.set_xlabel("Quantity (Q)")
    ax.set_ylabel("Price (p)")
    ax.set_title(label, fontsize=14)
    ax.grid(True)


# 📊 Panel 1: Consumers (Side A)
figA, axA = plt.subplots(figsize=(8, 5))
draw_panel(axA, P_A_curve, Q_A, p_A, "Side A: Consumers (Gamers)")
st.pyplot(figA)

# 📊 Panel 2: Developers (Side B)
figB, axB = plt.subplots(figsize=(8, 5))
draw_panel(axB, P_B_curve, Q_B, p_B, "Side B: Developers (Game Publishers)")
st.pyplot(figB)

st.caption("Demand curves are linear and shift with γ values. Revenue is shaded area p × Q.")
