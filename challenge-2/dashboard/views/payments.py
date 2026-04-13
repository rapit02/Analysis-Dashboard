# views/payments.py — Payment behaviour page

import streamlit as st
import plotly.graph_objects as go
import duckdb
from data import apply_dark_theme


def render(df):
    st.title("Payment Behaviour & Tipping Analysis")
    st.markdown(
        "Payment method significantly influences both trip value and tipping behaviour. "
        "Understanding this helps identify opportunities to increase driver earnings."
    )
    st.markdown("---")

    # Guard against empty dataframe
    if df is None or len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    payment = duckdb.query("""
        SELECT
            payment_type,
            COUNT(*) AS trip_count,
            ROUND(AVG(total_revenue), 2) AS avg_revenue_per_trip,
            ROUND(AVG(tips), 2) AS avg_tip,
            ROUND(AVG(CASE WHEN fare > 0 THEN tips / fare ELSE NULL END) * 100, 2) AS avg_tip_rate_pct
        FROM df
        WHERE payment_type IS NOT NULL
        GROUP BY payment_type
        HAVING COUNT(*) > 1000
        ORDER BY trip_count DESC
    """).df()

    total_trips = payment["trip_count"].sum()

    # ── Metrics ───────────────────────────────────────────────────────────────
    cols = st.columns(len(payment))
    for i, (_, row) in enumerate(payment.iterrows()):
        cols[i].metric(
            row["payment_type"],
            f"{row['trip_count']/total_trips*100:.1f}%",
            f"${row['avg_revenue_per_trip']:.2f}/trip",
        )

    st.markdown("---")

    COLORS = ["#2d6a9f", "#27ae60", "#e67e22", "#8e44ad", "#f39c12"]

    col_left, col_right = st.columns(2)

    # ── Trip Volume ───────────────────────────────────────────────────────────
    with col_left:
        st.subheader("Trip Volume by Payment Type")
        fig1 = go.Figure(go.Bar(
            x=payment["payment_type"],
            y=payment["trip_count"] / 1000,
            marker_color=COLORS[:len(payment)],
            text=[f"{v/1000:.0f}K" for v in payment["trip_count"]],
            textposition="outside",
            textfont=dict(color="#ffffff"),
        ))
        fig1.update_layout(
            yaxis_title="Trips (thousands)",
            showlegend=False,
        )
        fig1 = apply_dark_theme(fig1, height=350)
        st.plotly_chart(fig1, use_container_width=True)

    # ── Avg Revenue Per Trip ──────────────────────────────────────────────────
    with col_right:
        st.subheader("Average Revenue Per Trip")
        fig2 = go.Figure(go.Bar(
            x=payment["payment_type"],
            y=payment["avg_revenue_per_trip"],
            marker_color=COLORS[:len(payment)],
            text=[f"${v:.2f}" for v in payment["avg_revenue_per_trip"]],
            textposition="outside",
            textfont=dict(color="#ffffff"),
        ))
        fig2.update_layout(
            yaxis_title="Avg Revenue ($)",
            yaxis_tickprefix="$",
            showlegend=False,
        )
        fig2 = apply_dark_theme(fig2, height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tip Rate ──────────────────────────────────────────────────────────────
    st.subheader("Average Tip Rate by Payment Type")
    st.markdown(
        "⚠️ **Note:** Cash tip rate shows 0.0% because cash tips are paid "
        "directly to drivers and are not captured in the electronic payment system. "
        "This is a data limitation, not true tipping behaviour."
    )
    fig3 = go.Figure(go.Bar(
        x=payment["payment_type"],
        y=payment["avg_tip_rate_pct"],
        marker_color=COLORS[:len(payment)],
        text=[f"{v:.1f}%" for v in payment["avg_tip_rate_pct"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
    ))
    fig3.update_layout(
        yaxis_title="Avg Tip Rate (%)",
        yaxis_ticksuffix="%",
        showlegend=False,
    )
    fig3 = apply_dark_theme(fig3, height=350)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    cash = payment[payment["payment_type"] == "Cash"]
    card = payment[payment["payment_type"] == "Credit Card"]

    if len(cash) > 0 and len(card) > 0:
        cash_rev = cash["avg_revenue_per_trip"].values[0]
        card_rev = card["avg_revenue_per_trip"].values[0]
        diff = card_rev - cash_rev
        pct = diff / cash_rev * 100

        st.markdown("---")
        st.subheader("Key Insight")
        st.markdown(f"""
        <div style='background: rgba(45,106,159,0.1);
                border: 1px solid rgba(45,106,159,0.3);
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 0.9rem;
                color: #94a3b8;
                line-height: 1.8;'>
            Trips paid by <strong style='color: #ffffff;'>credit card</strong> generate
            <strong style='color: #ffffff;'>${card_rev:.2f}</strong> per trip on average —
            <strong style='color: #4ade80;'>${diff:.2f} ({pct:.0f}%) more</strong>
            than cash trips (${cash_rev:.2f}).
            Cash remains the most common payment at
            <strong style='color: #ffffff;'>{cash['trip_count'].values[0]/total_trips*100:.1f}%</strong>
            of trips.
            Encouraging card payments could meaningfully increase driver earnings
            without changing prices or adding trips.
            </div>
            """, unsafe_allow_html=True)