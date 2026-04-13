# views/companies.py — Company performance page

import streamlit as st
import plotly.graph_objects as go
from data import query_company_performance, apply_dark_theme

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
            Company Performance
        </div>
        <div style='font-size: 0.9rem; color: #6b7a99; margin-top: 6px;'>
            Market share and efficiency across 6 operators
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    company = query_company_performance(df)

    # ── Metrics ───────────────────────────────────────────────────────────────
    top = company.iloc[0]
    best_avg = company.loc[company["avg_revenue_per_trip"].idxmax()]
    worst_avg = company.loc[company["avg_revenue_per_trip"].idxmin()]
    diff = best_avg["avg_revenue_per_trip"] - worst_avg["avg_revenue_per_trip"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Leader", top["company"].split()[0])
    col2.metric("Leader Revenue", f"${top['total_revenue']/1_000_000:.1f}M")
    col3.metric("Highest Avg/Trip", f"${best_avg['avg_revenue_per_trip']:.2f}")
    col4.metric("Performance Gap", f"${diff:.2f}/trip")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── Revenue by Company ────────────────────────────────────────────────────
    with col_left:
        st.subheader("Total Revenue by Company")
        fig1 = go.Figure(go.Bar(
            y=company["company"],
            x=company["total_revenue"] / 1_000_000,
            orientation="h",
            marker_color=[
                COMPANY_COLORS.get(c, "#95a5a6") for c in company["company"]
            ],
            text=[f"${v/1_000_000:.1f}M" for v in company["total_revenue"]],
            textposition="outside",
            textfont=dict(color="#ffffff"),
        ))
        fig1.update_layout(
            xaxis_title="Revenue ($M)",
            xaxis_tickprefix="$",
            xaxis_ticksuffix="M",
            yaxis=dict(autorange="reversed"),
        )
        fig1 = apply_dark_theme(fig1, height=350)
        st.plotly_chart(fig1, use_container_width=True)

    # ── Trip Volume by Company ────────────────────────────────────────────────
    with col_right:
        st.subheader("Trip Volume by Company")
        fig2 = go.Figure(go.Bar(
            y=company["company"],
            x=company["trip_count"] / 1000,
            orientation="h",
            marker_color=[
                COMPANY_COLORS.get(c, "#95a5a6") for c in company["company"]
            ],
            text=[f"{v/1000:.0f}K" for v in company["trip_count"]],
            textposition="outside",
            textfont=dict(color="#ffffff"),
        ))
        fig2.update_layout(
            xaxis_title="Trips (thousands)",
            yaxis=dict(autorange="reversed"),
        )
        fig2 = apply_dark_theme(fig2, height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Avg Revenue Per Trip ──────────────────────────────────────────────────
    st.subheader("Average Revenue Per Trip by Company")
    company_sorted = company.sort_values("avg_revenue_per_trip")
    fig3 = go.Figure(go.Bar(
        y=company_sorted["company"],
        x=company_sorted["avg_revenue_per_trip"],
        orientation="h",
        marker_color=[
            COMPANY_COLORS.get(c, "#95a5a6") for c in company_sorted["company"]
        ],
        text=[f"${v:.2f}" for v in company_sorted["avg_revenue_per_trip"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
    ))
    fig3.update_layout(
        xaxis_title="Avg Revenue Per Trip ($)",
        xaxis_tickprefix="$",
        yaxis=dict(autorange="reversed"),
    )
    fig3 = apply_dark_theme(fig3, height=300)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Revenue Per Mile ──────────────────────────────────────────────────────
    st.subheader("Revenue Per Mile by Company")
    st.markdown(
        "⚠️ Note: Blue Ribbon's high revenue per mile reflects specialisation "
        "in short premium transfers — not a data error."
    )
    company_rpm = company.sort_values("revenue_per_mile", ascending=True)
    fig4 = go.Figure(go.Bar(
        y=company_rpm["company"],
        x=company_rpm["revenue_per_mile"],
        orientation="h",
        marker_color=[
            COMPANY_COLORS.get(c, "#95a5a6") for c in company_rpm["company"]
        ],
        text=[f"${v:.2f}" for v in company_rpm["revenue_per_mile"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
    ))
    fig4.update_layout(
        xaxis_title="Revenue Per Mile ($)",
        xaxis_tickprefix="$",
        yaxis=dict(autorange="reversed"),
    )
    fig4 = apply_dark_theme(fig4, height=300)
    st.plotly_chart(fig4, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
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
        <strong style='color: #ffffff;'>{best_avg['company']}</strong>
        generates the highest average revenue per trip at
        <strong style='color: #4ade80;'>${best_avg['avg_revenue_per_trip']:.2f}</strong>,
        while
        <strong style='color: #ffffff;'>{worst_avg['company']}</strong>
        generates the lowest at
        <strong style='color: #f87171;'>${worst_avg['avg_revenue_per_trip']:.2f}</strong>
        — a difference of
        <strong style='color: #ffffff;'>${diff:.2f} per trip</strong>.
        At scale, this gap represents significant revenue opportunity
        for lower-performing operators.
    </div>
    """, unsafe_allow_html=True)