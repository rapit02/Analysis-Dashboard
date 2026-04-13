# views/overview.py — Overview page

import streamlit as st
import plotly.graph_objects as go
from data import query_monthly_summary, query_overview_metrics, apply_dark_theme


def render(df):
    st.markdown("""
    <div style='padding: 8px 0 24px 0;'>
        <div style='font-size: 2rem; font-weight: 800; color: #ffffff;
                    letter-spacing: -0.03em; line-height: 1.2;'>
            Overview
        </div>
        <div style='font-size: 0.9rem; color: #6b7a99; margin-top: 6px;'>
            Chicago Taxi Industry — January to June 2020
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if df is None or len(df) == 0:
        st.warning("No data available for the selected filters. Please adjust your selection.")
        return

    if len(df) < 100:
        st.info(
        f"Only {len(df)} trips match the current filters. "
        "Some charts may show limited data. "
        "Note: July only contains 5 trips (dataset cuts off July 1st)."
    )


    # ── Metrics ───────────────────────────────────────────────────────────────
    metrics = query_overview_metrics(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trips", f"{int(metrics['total_trips']):,}")
    col2.metric("Total Revenue", f"${metrics['total_revenue']:,.0f}")
    col3.metric("Avg Revenue / Trip", f"${metrics['avg_revenue_per_trip']:.2f}")
    col4.metric("Unique Taxis", f"{int(metrics['unique_taxis']):,}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Avg Trip Miles", f"{metrics['avg_trip_miles']:.2f} mi")
    col6.metric("Avg Trip Duration", f"{metrics['avg_trip_minutes']:.1f} min")
    col7.metric("Companies", f"{int(metrics['unique_companies'])}")
    col8.metric("Period", "Jan–Jun 2020")

    st.markdown("""
    <div style='background: rgba(45,106,159,0.1);
            border: 1px solid rgba(45,106,159,0.3);
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 0.85rem;
            color: #94a3b8;
            margin-bottom: 16px;'>
        📅 <strong style='color: #7dd3fc;'>Note:</strong>
        Monthly trend charts cover January–June 2020.
        July is excluded — the dataset contains only 5 trips on July 1st
        and is not representative of a full month.
    </div>
""", unsafe_allow_html=True)
    # ── Monthly Summary ───────────────────────────────────────────────────────
    monthly = query_monthly_summary(df)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Monthly Revenue")
        colors = ["#2d6a9f"] * len(monthly)
        fig = go.Figure(go.Bar(
            x=monthly["month_name"],
            y=monthly["total_revenue"] / 1_000_000,
            marker_color=colors,
            text=[f"${v/1_000_000:.1f}M" for v in monthly["total_revenue"]],
            textposition="outside",
            textfont=dict(color="#ffffff"),
        ))
        fig.update_layout(
            yaxis_title="Revenue ($M)",
            yaxis_tickprefix="$",
            yaxis_ticksuffix="M",
            showlegend=False,
        )
        fig = apply_dark_theme(fig, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Monthly Trip Volume")
        colors2 = ["#2d6a9f"] * len(monthly)
        fig2 = go.Figure(go.Bar(
            x=monthly["month_name"],
            y=monthly["trip_count"] / 1000,
            marker_color=colors2,
            text=[f"{v/1000:.0f}K" for v in monthly["trip_count"]],
            textposition="outside",
            textfont=dict(color="#ffffff"),
        ))
        fig2.update_layout(
            yaxis_title="Trips (thousands)",
            showlegend=False,
        )
        fig2 = apply_dark_theme(fig2, height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Avg Revenue Per Trip ──────────────────────────────────────────────────
    st.subheader("Average Revenue Per Trip By Month")
    st.markdown(
        "Note: Average revenue per trip **increased** during lockdown months — "
        "suggesting remaining trips were longer or higher value essential journeys."
    )
    fig3 = go.Figure(go.Bar(
        x=monthly["month_name"],
        y=monthly["avg_revenue_per_trip"],
        marker_color=[
            "#d32f2f" if m in [3, 4, 5] else "#e67e22"
            for m in monthly["month"]
        ],
        text=[f"${v:.2f}" for v in monthly["avg_revenue_per_trip"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
    ))
    fig3.update_layout(
        yaxis_title="Avg Revenue ($)",
        yaxis_tickprefix="$",
        showlegend=False,
    )
    fig3 = apply_dark_theme(fig3, height=300)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Key Insight ───────────────────────────────────────────────────────────
    if len(monthly) >= 4:
        peak = monthly.loc[monthly["trip_count"].idxmax()]
        lowest = monthly.loc[monthly["trip_count"].idxmin()]
        drop = (peak["trip_count"] - lowest["trip_count"]) / peak["trip_count"] * 100
        rev_drop = (
            (peak["total_revenue"] - lowest["total_revenue"])
            / peak["total_revenue"] * 100
        )

        st.markdown("---")
        st.subheader("Key Insight")
        st.info(
            f"**{peak['month_name']}** was the peak month with "
            f"**{int(peak['trip_count']):,} trips** and "
            f"**${peak['total_revenue']:,.0f}** revenue. "
            f"By **{lowest['month_name']}**, trips had fallen by **{drop:.1f}%** "
            f"and revenue by **{rev_drop:.1f}%** — consistent with the impact of "
            f"COVID-19 restrictions which began in Chicago on 21 March 2020."
        )