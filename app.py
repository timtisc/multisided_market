import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ---- Page setup ----
st.set_page_config(page_title="Gaming Platform Simulator", layout="wide")

# ---- Slightly tighter layout ----
st.markdown("""
<style>
    .block-container {padding-top: 0.8rem; padding-bottom: 0.5rem;}
    div[data-testid="column"] {padding: 0.25rem;}
</style>
""", unsafe_allow_html=True)

st.title("Gaming Platform Simulator – Linear Demand & Revenue")

st.markdown("""
**Two-sided market example: a gaming platform**

- **Side A – Consumers (Players):**  
  Price \\(p_A\\) can be interpreted as an **effective per-player monthly fee** (e.g., subscription to the platform or average platform margin per active player).

- **Side B – Developers (Game studios):**  
  Price \\(p_B\\) is an **effective monthly fee per active developer/game**, representing listing fees, commissions, or revenue share paid to the platform.

Demand on each side is **linear** and reacts to both its own price and the size of the *other* side (network effects).  
Revenue on each side is visualized as a **rectangle**: \\( R = p \\times Q \\).
""")

# ---- Fixed axis ranges (stable view) ----
MAX_Q = 2000   # max quantity for x-axis
MAX_P = 60     # max price for y-axis

# ---- Placeholders for plots & KPIs at the top ----
plot_col1, plot_col2 = st.columns(2)
plotA_placeholder = plot_col1.empty()
plotB_placeholder = plot_col2.empty()

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpiA_placeholder = kpi_col1.empty()
kpiB_placeholder = kpi_col2.empty()
kpiR_placeholder = kpi_col3.empty()

st.write("")  # small spacer

# ---- Container for controls BELOW the visuals ----
controls = st.container()

with controls:
    st.subheader("Adjust Platform Parameters")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("**Side A – Consumers (Players)**")
        # Defaults chosen so the full demand curve fits within MAX_Q, MAX_P
        a_A = st.slider("Base demand a_A (potential players)",
                        500, 2000, 1200, 50)
        b_A = st.slider("Price sensitivity b_A (players)",
                        10, 60, 40, 1)
        gamma_A = st.slider("γ_A (effect of games on players)",
                            0.0, 1.0, 0.3, 0.05)
        p_A = st.slider("Effective monthly price to players p_A [€]",
                        0.0, 20.0, 5.0, 0.5,
                        help="Subscription fee or effective margin per active player.")

    with colB:
        st.markdown("**Side B – Developers (Game studios)**")
        a_B = st.slider("Base demand a_B (potential developers)",
                        50, 400, 200, 10)
        b_B = st.slider("Price sensitivity b_B (developers)",
                        5, 40, 10, 1)
        gamma_B = st.slider("γ_B (effect of players on developers)",
                            0.0, 1.0, 0.3, 0.05)
        p_B = st.slider("Effective monthly fee to developers p_B [€]",
                        0.0, 50.0, 20.0, 1.0,
                        help="Listing fees, commission, or equivalent monthly charge per developer/game.")

# ---- Linear demand solver ----
def solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B):
    """
    Linear system:
    Q_A = a_A - b_A * p_A + γ_A * Q_B
    Q_B = a_B - b_B * p_B + γ_B * Q_A
    """
    A = np.array([[1, -gamma_A],
                  [-gamma_B, 1]])
    B = np.array([a_A - b_A * p_A,
                  a_B - b_B * p_B])
    Q_A, Q_B = np.linalg.solve(A, B)
    return max(Q_A, 0.0), max(Q_B, 0.0)

# ---- Compute equilibrium quantities and revenues given sliders ----
Q_A, Q_B = solve_demand(a_A, b_A, a_B, b_B, gamma_A, gamma_B, p_A, p_B)
R_A = p_A * Q_A
R_B = p_B * Q_B

# ---- Prepare linear demand curves (P as function of Q) ----
Q_range = np.linspace(0, MAX_Q, 200)

# P_A(Q) = (a_A + γ_A * Q_B - Q)/b_A  (capped at >= 0)
P_A_curve = np.maximum(0, (a_A + gamma_A * Q_B - Q_range) / b_A)

# P_B(Q) = (a_B + γ_B * Q_A - Q)/b_B
P_B_curve = np.maximum(0, (a_B + gamma_B * Q_A - Q_range) / b_B)

# With the chosen defaults (a_, b_, γ_), the *full* linear line for both sides
# lies inside [0, MAX_Q] × [0, MAX_P] in the default setting.

# ---- Helper for drawing each panel ----
def draw_panel(Q_curve, Q_star, P_star, title):
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    # Demand curve
    ax.plot(Q_range, Q_curve, color="black", linewidth=1.8)

    # Revenue rectangle (from (0,0) to (Q*,P*))
    rect = patches.Rectangle(
        (0, 0),
        min(Q_star, MAX_Q),
        min(P_star, MAX_P),
        facecolor='orange',
        alpha=0.35,
        edgecolor='black',
        linewidth=2
    )
    ax.add_patch(rect)

    # Mark the operating point (Q*, P*)
    ax.scatter(min(Q_star, MAX_Q), min(P_star, MAX_P),
               color="red", s=60, zorder=3)

    ax.set_xlim(0, MAX_Q)
    ax.set_ylim(0, MAX_P)
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price p")
    ax.set_title(title, fontsize=13)
    ax.grid(True, linewidth=0.3, alpha=0.7)
    fig.tight_layout(pad=0.3)
    return fig

# ---- Render plots into the placeholders at the TOP ----
with plotA_placeholder:
    figA = draw_panel(P_A_curve, Q_A, p_A,
                      "Side A – Consumers (Players)")
    st.pyplot(figA, use_container_width=True)

with plotB_placeholder:
    figB = draw_panel(P_B_curve, Q_B, p_B,
                      "Side B – Developers")
    st.pyplot(figB, use_container_width=True)

# ---- KPIs under the plots ----
kpiA_placeholder.metric("Consumers Q_A (active players)", f"{Q_A:,.1f}")
kpiB_placeholder.metric("Developers Q_B (active devs/games)", f"{Q_B:,.1f}")
kpiR_placeholder.metric("Total platform revenue R_A + R_B", f"{(R_A + R_B):,.1f} €")

st.caption(
    "In the default settings, the *entire* linear demand curve for both sides fits "
    "into the shown p–Q diagram. Adjust parameters below to explore cross-side "
    "effects and pricing trade-offs."
)
