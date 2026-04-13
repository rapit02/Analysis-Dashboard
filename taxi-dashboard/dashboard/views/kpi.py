# views/kpi.py — CEO KPI: Revenue Per Active Taxi Per Day (RPATD)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data import query_market_rpatd, query_company_rpatd, apply_dark_theme

COMPANY_COLORS = {
    "Flash Cab": "#d32f2f",
    "Taxi Affiliation Services": "#2d6a9f",
    "Chicago Carriage Cab Corp": "#27ae60",
    "City Service": "#e67e22",
    "Blue Ribbon Taxi Association Inc.": "#8e44ad",
    "Choice Taxi Association": "#f39c12",
}


def render(df):
    st.markdown("""
    <div style='padding: 8px 0 24px 0;'>
        <div style='font-size: 2rem; font-weight: 800; color: #ffffff;
                    letter-spacing: -0.03em; line-height: 1.2;'>
            CEO KPI — RPATD
        </div>
        <div style='font-size: 0.9rem; color: #6b7a99; margin-top: 6px;'>
            Revenue Per Active Taxi Per Day — daily fleet productivity metric
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style='background: #0d1117;
                border: 1px solid rgba(45,106,159,0.25);
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 24px;'>
        <div style='font-size: 0.95rem; color: #e2e8f0; margin-bottom: 12px;'>
            <strong>RPATD</strong> measures how much total revenue each working taxi generates daily.
        </div>
        <div style='font-family: monospace;
                    background: rgba(45,106,159,0.15);
                    border: 1px solid rgba(45,106,159,0.3);
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-size: 0.9rem;
                    color: #7dd3fc;
                    margin-bottom: 12px;'>
            RPATD = Total Daily Revenue / Number of Taxis With ≥1 Trip That Day
        </div>
        <div style='font-size: 0.85rem; color: #6b7a99; line-height: 1.7;'>
            This KPI controls for fleet size — it only grows if each individual 
            taxi earns more, not just because more taxis are on the road.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    market = query_market_rpatd(df)
    company_daily = query_company_rpatd(df)

    baseline = market["baseline"].iloc[0]
    latest_recovery = market["recovery_rate"].iloc[-1]
    lowest_rpatd = market["rpatd"].min()
    lowest_date = market.loc[market["rpatd"].idxmin(), "trip_date"].strftime("%b %d")
    highest_rpatd = market["rpatd"].max()
    highest_date = market.loc[market["rpatd"].idxmax(), "trip_date"].strftime("%b %d")

    # ── Metrics ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jan–Feb Baseline", f"${baseline:.2f}")
    col2.metric("Lowest RPATD", f"${lowest_rpatd:.2f}", f"{lowest_date}")
    col3.metric("Peak RPATD", f"${highest_rpatd:.2f}", f"{highest_date}")
    col4.metric("Recovery by Jun 30", f"{latest_recovery:.1f}%")

    st.markdown("---")

    lockdown_date = pd.Timestamp("2020-03-21")

    # ── Market RPATD Chart ────────────────────────────────────────────────────
    st.subheader("Market-Wide RPATD — Daily with 7-Day Rolling Average")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=market["trip_date"],
        y=market["rpatd"],
        mode="lines",
        name="Daily RPATD",
        line=dict(color="#2d6a9f", width=1),
        opacity=0.4,
        fill="tozeroy",
        fillcolor="rgba(45,106,159,0.15)",
    ))
    fig1.add_trace(go.Scatter(
        x=market["trip_date"],
        y=market["rpatd_7day_avg"],
        mode="lines",
        name="7-Day Rolling Average",
        line=dict(color="#d32f2f", width=2.5),
    ))
    fig1.add_hline(
        y=baseline,
        line_dash="dash",
        line_color="#27ae60",
        annotation_text=f"Jan-Feb Baseline: ${baseline:.2f}",
        annotation_position="top right",
        annotation_font_color="#27ae60",
    )
    fig1.update_layout(
        yaxis_title="Revenue Per Taxi ($)",
        yaxis_tickprefix="$",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig1 = apply_dark_theme(fig1, height=400)
    st.plotly_chart(fig1, use_container_width=True)

    # ── Company RPATD Chart ───────────────────────────────────────────────────
    st.subheader("Company-Level RPATD vs Market Average (7-Day Smoothed)")

    company_pivot = company_daily.pivot(
        index="trip_date", columns="company", values="rpatd"
    )
    company_pivot_smooth = company_pivot.rolling(7).mean()
    market_smooth = market.set_index("trip_date")["rpatd_7day_avg"]

    fig2 = go.Figure()
    for company_name in company_pivot_smooth.columns:
        color = COMPANY_COLORS.get(company_name, "#95a5a6")
        fig2.add_trace(go.Scatter(
            x=company_pivot_smooth.index,
            y=company_pivot_smooth[company_name],
            mode="lines",
            name=company_name,
            line=dict(color=color, width=2),
        ))
    fig2.add_trace(go.Scatter(
        x=market_smooth.index,
        y=market_smooth.values,
        mode="lines",
        name="Market Average",
        line=dict(color="#ffffff", width=2, dash="dash"),
    ))
    fig2.update_layout(
        yaxis_title="Revenue Per Taxi ($)",
        yaxis_tickprefix="$",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig2 = apply_dark_theme(fig2, height=450)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Recovery Rate Chart ───────────────────────────────────────────────────
    st.subheader("Market Recovery Rate vs Jan-Feb Baseline")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=market["trip_date"],
        y=market["recovery_rate"],
        mode="lines",
        name="Recovery Rate",
        line=dict(color="#2d6a9f", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(230,126,34,0.2)",
    ))
    fig3.add_hline(
        y=100,
        line_dash="dash",
        line_color="#27ae60",
        annotation_text="Jan-Feb Baseline (100%)",
        annotation_position="top right",
        annotation_font_color="#27ae60",
    )
    fig3.add_hline(
        y=50,
        line_dash="dot",
        line_color="#e67e22",
        annotation_text="50% Recovery",
        annotation_position="top right",
        annotation_font_color="#e67e22",
    )
    fig3.update_layout(
        yaxis_title="Recovery (%)",
        yaxis_ticksuffix="%",
    )
    fig3 = apply_dark_theme(fig3, height=350)
    st.plotly_chart(fig3, use_container_width=True)

    # ── KPI Explanation ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Why RPATD?")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **RPATD is the right CEO daily KPI because:**
        - Controls for fleet size — total revenue grows just by adding taxis
        - Actionable — a drop signals demand issues, pricing problems, or fleet oversizing
        - Reflects real economics — every taxi has fixed daily costs
        - Changes daily — useful for immediate decision-making
        - Enables competitive benchmarking across operators
        """)
    with col_b:
        st.markdown("""
        **Ideal KPI (if cost data were available):**

        Daily Contribution Margin Per Active Taxi:

        > DCMAT = (Revenue − Variable Costs) / Active Taxis

        Variable costs: driver commission, fuel, processing fees.
        RPATD serves as the strongest revenue-side proxy for DCMAT
        when cost data is unavailable.
        """)

    st.markdown(f"""
    <div style='background: rgba(45,106,159,0.1);
            border: 1px solid rgba(45,106,159,0.3);
            border-radius: 12px;
            padding: 16px 20px;
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.8;'>
        <strong style='color: #7dd3fc;'>Summary:</strong>
        The Jan–Feb baseline was
        <strong style='color: #ffffff;'>${baseline:.2f}</strong>
        per active taxi per day.
        RPATD dropped to
        <strong style='color: #ffffff;'>${lowest_rpatd:.2f}</strong>
        on {lowest_date} — just
        <strong style='color: #f87171;'>{lowest_rpatd/baseline*100:.1f}%</strong>
        of the baseline.
        By June 30th the market had recovered to
        <strong style='color: #4ade80;'>{latest_recovery:.1f}%</strong>
        of baseline — a strong recovery given the scale of the disruption.
    </div>
    """, unsafe_allow_html=True)