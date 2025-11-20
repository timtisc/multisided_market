import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Gaming Platform Simulator", layout="wide")

st.title("Gaming Platform Simulator – Linear Demand Curves & Revenue Rectangles")

st.markdown(
    """
    **Two-Sided Market: Gaming Platform Example**  
    - **Side A:** Gamers (price-sensitive, large base)  
    - **Side B:** Game Developers (pay fees/commission, less elastic)  
    Demand is linear and reacts to **prices and cross-side network effects (γ)**.
    """
)

# Sidebar parameters
st.sidebar.header("Platform Parameters")

# Base linear demand parameters
a_A = st.sidebar.slider("Base demand a_A (Consumers)", 500, 2000, 1000, 50)
b_A = st.sidebar.slider("Price sensitivity b_A (Consumers)", 10, 50, 30, 1)
a_B = st.sidebar.slider("Base demand a_B (Developers)", 50, 300, 150, 10)
b_B = st.sidebar.slider("Price sensitivity b_B (Developers)", 1, 10, 2, 1)

gamma_A = st.sidebar.slider("Cross-side effect γ_A (Games → Consumers)", 0.0, 2.0, 0.5, 0.1)
gamma_B = st.sidebar.slider("Cross-side effect γ_B (Consumers → Games)", 0.0, 3.0, 1.2, 0.1)

p_A = st.sidebar.slider("Price to Consumers (p_A)", 0.0, 20.0, 5.0, 0.5)
p_B = st.sidebar.slider("Price to Developers (p_B)", 0.0, 50.0, 25.0, 1.0)


def solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B):
    """Solve simultaneous linear demand system."""
    A = np.array([[1, -gamma_A], [-gamma_B, 1]])
    B = np.array([a_A - b_A * p_A, a_B - b_B * p_B])
    Q_A, Q_B = np.linalg.solve(A, B)
    return max(Q_A, 0), max(Q_B, 0)


Q_A, Q_B = solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B)

# Revenue
R_A, R_B = p_A * Q_A, p_B * Q_B

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Consumers (Q_A)", f"{Q_A:.1f}")
col2.metric("Developers (Q_B)", f"{Q_B:.1f}")
col3.metric("Total Revenue", f"{(R_A + R_B):.1f}")

st.divider()

# Stable visualization ranges (fixed)
MAX_Q = 2000  # max quantity
MAX_P = 60    # max price  

# Create demand curves (linear) — adjusting for cross-side effects
Q_range = np.linspace(0, MAX_Q, 200)
P_A_curve = np.maximum(0, (a_A + gamma_A * Q_B - Q_range) / b_A)
P_B_curve = np.maximum(0, (a_B + gamma_B * Q_A - Q_range) / b_B)


# Plot both curves with fixed axes
def plot_demand(fig, ax, P_curve, Q_star, P_star, label):
    ax.plot(Q_range, P_curve, label="Demand Curve", color="black", linewidth=1.5)

    # Draw revenue rectangle (shaded area)
    rect = patches.Rectangle(
        (0, 0),
        min(Q_star, MAX_Q),
        min(P_star, MAX_P),
        facecolor='orange',
        alpha=0.3,
        edgecolor='black'
    )
    ax.add_patch(rect)

    # Mark the (Q*,P*) point
    ax.scatter(min(Q_star, MAX_Q), min(P_star, MAX_P), color="red", s=60)

    # Labels and formatting
    ax.set_xlim(0, MAX_Q)
    ax.set_ylim(0, MAX_P)
    ax.set_xlabel("Quantity (Q)")
    ax.set_ylabel("Price (p)")
    ax.grid(True)
    ax.set_title(label)


c1, c2 = st.columns(2)

with c1:
    figA, axA = plt.subplots(figsize=(5,4))
    plot_demand(figA, axA, P_A_curve, Q_A, p_A, "Side A: Consumers")
    st.pyplot(figA)

with c2:
    figB, axB = plt.subplots(figsize=(5,4))
    plot_demand(figB, axB, P_B_curve, Q_B, p_B, "Side B: Developers")
    st.pyplot(figB)

st.caption("Linear demand curves with fixed axes. Revenue shown as rectangle p × Q.")
