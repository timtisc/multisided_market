import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Two-Sided Market Simulator", layout="centered")

st.title("Two-Sided Platform: Elasticities & Revenue")

st.markdown(
    """
Use the sliders to change **price elasticities** and **cross-side effects** on both sides
of the market and see how platform **revenue** changes.

Model (log–linear, very simple):

- Demand side A:  `Q_A = k_A · p_A^β_A · (Q_B+1)^γ_A`
- Demand side B:  `Q_B = k_B · p_B^β_B · (Q_A+1)^γ_B`

Platform revenue: `R = p_A · Q_A + p_B · Q_B`
"""
)

st.sidebar.header("Parameters")

# Base demand (scale)
k_A = st.sidebar.slider("Base demand k_A (side A)", 10.0, 200.0, 100.0, 10.0)
k_B = st.sidebar.slider("Base demand k_B (side B)", 10.0, 200.0, 80.0, 10.0)

# Prices
p_A = st.sidebar.slider("Price p_A (side A)", 0.0, 50.0, 10.0, 1.0)
p_B = st.sidebar.slider("Price p_B (side B)", 0.0, 50.0, 5.0, 1.0)

# Own-price elasticities (negative)
beta_A = st.sidebar.slider("Price elasticity β_A (side A)", -3.0, 0.0, -1.0, 0.1)
beta_B = st.sidebar.slider("Price elasticity β_B (side B)", -3.0, 0.0, -1.5, 0.1)

# Cross-side effects
gamma_A = st.sidebar.slider("Cross-side effect γ_A (A reacts to B)", 0.0, 2.0, 0.5, 0.1)
gamma_B = st.sidebar.slider("Cross-side effect γ_B (B reacts to A)", 0.0, 2.0, 0.8, 0.1)

# Iterative solution for Q_A, Q_B
def solve_demands(k_A, k_B, p_A, p_B, beta_A, beta_B, gamma_A, gamma_B,
                  max_iter=1000, tol=1e-6):
    Q_A, Q_B = 50.0, 50.0  # starting guess
    for _ in range(max_iter):
        new_Q_A = k_A * (p_A ** beta_A) * ((Q_B + 1.0) ** gamma_A)
        new_Q_B = k_B * (p_B ** beta_B) * ((Q_A + 1.0) ** gamma_B)
        if abs(new_Q_A - Q_A) < tol and abs(new_Q_B - Q_B) < tol:
            Q_A, Q_B = new_Q_A, new_Q_B
            break
        Q_A, Q_B = new_Q_A, new_Q_B
    return max(Q_A, 0.0), max(Q_B, 0.0)

Q_A, Q_B = solve_demands(k_A, k_B, p_A, p_B, beta_A, beta_B, gamma_A, gamma_B)

R_A = p_A * Q_A
R_B = p_B * Q_B
R_total = R_A + R_B

col1, col2, col3 = st.columns(3)
col1.metric("Users / Side A", f"{Q_A:,.1f}")
col2.metric("Partners / Side B", f"{Q_B:,.1f}")
col3.metric("Total Revenue", f"{R_total:,.1f}")

st.markdown("### Revenue Breakdown")
fig, ax = plt.subplots()
labels = ["Revenue A", "Revenue B"]
values = [R_A, R_B]
ax.bar(labels, values)
ax.set_ylabel("Revenue")
st.pyplot(fig)

st.markdown(
    """
**How to use this in class**

- Start with symmetric elasticities (β_A = β_B, γ_A = γ_B) and show how revenue changes with
  stronger cross-side effects.
- Then make one side more price-sensitive (e.g., β_A very negative) and discuss where to
  “subsidize” one side and make money on the other.
- Let groups propose real platforms (e.g., Airbnb, app stores, dating apps) and guess which
  side has which elasticity and cross-side effect.
"""
)

