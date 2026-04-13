# views/demand.py — Demand patterns page

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data import query_hourly_demand, query_daily_demand, query_heatmap, apply_dark_theme

DAY_ORDER = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]


def render(df):
    st.markdown("""
    <div style='padding: 8px 0 24px 0;'>
        <div style='font-size: 2rem; font-weight: 800; color: #ffffff;
                    letter-spacing: -0.03em; line-height: 1.2;'>
            Demand Patterns
        </div>
        <div style='font-size: 0.9rem; color: #6b7a99; margin-top: 6px;'>
            When do people take taxis? — January to June 2020
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    hourly = query_hourly_demand(df)
    daily = query_daily_demand(df)
    heatmap_data = query_heatmap(df)

    # ── Key Stats ─────────────────────────────────────────────────────────────
    peak_hour = int(hourly.loc[hourly["trip_count"].idxmax(), "hour"])
    peak_hour_trips = int(hourly["trip_count"].max())
    quiet_hour = int(hourly.loc[hourly["trip_count"].idxmin(), "hour"])
    quiet_hour_trips = int(hourly["trip_count"].min())
    ratio = peak_hour_trips / quiet_hour_trips

    daily["day_of_week"] = pd.Categorical(
        daily["day_of_week"], categories=DAY_ORDER, ordered=True
    )
    daily = daily.sort_values("day_of_week")
    busiest_day = daily.loc[daily["trip_count"].idxmax(), "day_of_week"]
    quietest_day = daily.loc[daily["trip_count"].idxmin(), "day_of_week"]

    weekend = daily[
        daily["day_of_week"].isin(["Saturday", "Sunday"])
    ]["trip_count"].sum()
    weekday = daily[
        ~daily["day_of_week"].isin(["Saturday", "Sunday"])
    ]["trip_count"].sum()
    total = weekend + weekday

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peak Hour", f"{peak_hour}:00", f"{peak_hour_trips:,} trips")
    col2.metric("Quietest Hour", f"{quiet_hour}:00", f"{quiet_hour_trips:,} trips")
    col3.metric("Peak/Quiet Ratio", f"{ratio:.1f}x")
    col4.metric("Busiest Day", busiest_day)

    st.markdown("---")

    # ── Hourly Chart ──────────────────────────────────────────────────────────
    st.subheader("Trips by Hour of Day")
    colors = [
        "#d32f2f" if h == peak_hour else "#2d6a9f"
        for h in hourly["hour"]
    ]
    fig_hour = go.Figure(go.Bar(
        x=hourly["hour"],
        y=hourly["trip_count"] / 1000,
        marker_color=colors,
        textfont=dict(color="#ffffff"),
        hovertemplate="Hour: %{x}:00<br>Trips: %{customdata:,}",
        customdata=hourly["trip_count"],
    ))
    fig_hour.update_layout(
        xaxis_title="Hour of Day (24h)",
        yaxis_title="Trips (thousands)",
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
    )
    fig_hour = apply_dark_theme(fig_hour, height=350)
    st.plotly_chart(fig_hour, use_container_width=True)

    # ── Day of Week ───────────────────────────────────────────────────────────
    st.subheader("Trips by Day of Week")
    colors_day = [
        "#27ae60" if d in ["Saturday", "Sunday"] else "#2d6a9f"
        for d in daily["day_of_week"]
    ]
    fig_day = go.Figure(go.Bar(
        x=daily["day_of_week"].astype(str),
        y=daily["trip_count"] / 1000,
        marker_color=colors_day,
        text=[f"{v/1000:.0f}K" for v in daily["trip_count"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
        hovertemplate="Day: %{x}<br>Trips: %{customdata:,}",
        customdata=daily["trip_count"],
    ))
    fig_day.update_layout(
        yaxis_title="Trips (thousands)",
    )
    fig_day = apply_dark_theme(fig_day, height=350)
    st.plotly_chart(fig_day, use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    st.subheader("Trip Heatmap — Hour vs Day of Week")
    st.markdown("Darker cells indicate higher trip volume.")

    heatmap_pivot = heatmap_data.pivot(
        index="day_of_week", columns="hour", values="trip_count"
    )
    heatmap_pivot = heatmap_pivot.reindex(DAY_ORDER)

    fig_heat = px.imshow(
        heatmap_pivot / 1000,
        labels=dict(x="Hour of Day", y="Day of Week", color="Trips (K)"),
        color_continuous_scale="Blues",
        aspect="auto",
    )
    fig_heat.update_layout(
        font=dict(color="#ffffff"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1a1d2e",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Key Insight")
    st.info(
        f"Demand peaks at **{peak_hour}:00** with **{peak_hour_trips:,} trips** — "
        f"**{ratio:.1f}x more** than the quietest hour "
        f"({quiet_hour}:00 with {quiet_hour_trips:,} trips). "
        f"**{busiest_day}** is the busiest day and **{quietest_day}** the quietest. "
        f"Weekdays account for **{weekday/total*100:.1f}%** of all trips — "
        f"suggesting demand is primarily driven by work-related travel rather than leisure."
    )