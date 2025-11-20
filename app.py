import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Gaming Platform Simulator", layout="wide")

st.title("Gaming Platform Simulator – Linear Demand with Revenue Rectangles")

st.markdown(
    """
    A two-sided gaming platform with **Consumers (Side A)** and **Game Developers (Side B)**.

    Consumers are price-sensitive and attracted by the number of available games.  
    Developers are less price-sensitive but heavily attracted by large player bases.
    """
)

# Sidebar Inputs
st.sidebar.header("Platform Parameters (Realistic Gaming Example)")

# 🔹 Base linear demand parameters
a_A = st.sidebar.slider("Base demand a_A (Consumers)", 500, 2000, 1000, 50)
b_A = st.sidebar.slider("Price sensitivity b_A", 10, 50, 30, 1)
a_B = st.sidebar.slider("Base demand a_B (Developers)", 50, 300, 150, 10)
b_B = st.sidebar.slider("Price sensitivity b_B", 1, 10, 2, 1)

# 🔹 Cross-side effects (network strength)
gamma_A = st.sidebar.slider("γ_A (Effect of games on users)", 0.0, 2.0, 0.5, 0.1)
gamma_B = st.sidebar.slider("γ_B (Effect of users on developers)", 0.0, 3.0, 1.2, 0.1)

# 🔹 Prices
p_A = st.sidebar.slider("Price to Consumers (p_A)", 0.0, 20.0, 5.0, 0.5)
p_B = st.sidebar.slider("Price to Developers (p_B)", 0.0, 50.0, 25.0, 1.0)


def solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B):
    """
    Solve the linear system:
    Q_A = a_A - b_A*p_A + gamma_A*Q_B
    Q_B = a_B - b_B*p_B + gamma_B*Q_A
    """
    A = np.array([[1, -gamma_A],
                  [-gamma_B, 1]])
    B = np.array([a_A - b_A * p_A, a_B - b_B * p_B])
    Q_A, Q_B = np.linalg.solve(A, B)
    return max(Q_A, 0), max(Q_B, 0)


Q_A, Q_B = solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B)

# Revenue
R_A = p_A * Q_A
R_B = p_B * Q_B


# 🔹 KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Consumers (Q_A)", f"{Q_A:.1f}")
col2.metric("Developers (Q_B)", f"{Q_B:.1f}")
col3.metric("Total Revenue", f"{(R_A + R_B):.1f}")


st.divider()

# 🔹 Revenue visualization (rectangles)
def draw_rectangle(ax, price, quantity, label):
    ax.plot([0, quantity], [price, price], 'k-', linewidth=1)
    ax.plot([quantity, quantity], [0, price], 'k-', linewidth=1)
    ax.add_patch(patches.Rectangle(
        (0, 0), quantity, price,
        facecolor='orange', alpha=0.3, edgecolor='black'
    ))
    ax.set_xlabel("Quantity (Q)")
    ax.set_ylabel("Price (p)")
    ax.set_title(label)
    ax.set_xlim(0, max(quantity * 1.2, 50))
    ax.set_ylim(0, max(price * 1.2, 50))
    ax.grid(True)

# Display both rectangles
c1, c2 = st.columns(2)

with c1:
    figA, axA = plt.subplots(figsize=(5,4))
    draw_rectangle(axA, p_A, Q_A, "Side A: Consumers")
    st.pyplot(figA)

with c2:
    figB, axB = plt.subplots(figsize=(5,4))
    draw_rectangle(axB, p_B, Q_B, "Side B: Developers")
    st.pyplot(figB)

st.caption("Rectangles represent revenue = p × Q for each side.")
