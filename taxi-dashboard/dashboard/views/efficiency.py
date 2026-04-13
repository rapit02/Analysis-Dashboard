# views/efficiency.py — Operational efficiency page

import streamlit as st
import plotly.graph_objects as go
import duckdb
from data import apply_dark_theme


def render(df):
    st.markdown("""
    <div style='padding: 8px 0 24px 0;'>
        <div style='font-size: 2rem; font-weight: 800; color: #ffffff;
                    letter-spacing: -0.03em; line-height: 1.2;'>
            Operational Efficiency
        </div>
        <div style='font-size: 0.9rem; color: #6b7a99; margin-top: 6px;'>
            Revenue per mile and per minute — which trips generate the most value?
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if df is None or len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    # ── Queries ───────────────────────────────────────────────────────────────
    efficiency_company = duckdb.query("""
        SELECT
            company,
            COUNT(*)                                          AS trip_count,
            ROUND(AVG(trip_miles), 2)                        AS avg_miles,
            ROUND(AVG(trip_minutes), 2)                      AS avg_minutes,
            ROUND(SUM(total_revenue) / SUM(trip_miles), 2)   AS revenue_per_mile,
            ROUND(SUM(total_revenue) / SUM(trip_minutes), 2) AS revenue_per_minute,
            ROUND(AVG(total_revenue), 2)                     AS avg_revenue_per_trip
        FROM df
        WHERE trip_miles > 0
        AND trip_minutes > 0
        AND company IS NOT NULL
        GROUP BY company
        HAVING COUNT(*) > 1000
        ORDER BY revenue_per_mile DESC
    """).df()

    distance_buckets = duckdb.query("""
        SELECT
            CASE
                WHEN trip_miles < 1  THEN 'Under 1 mile'
                WHEN trip_miles < 3  THEN '1–3 miles'
                WHEN trip_miles < 5  THEN '3–5 miles'
                WHEN trip_miles < 10 THEN '5–10 miles'
                ELSE                      'Over 10 miles'
            END AS distance_bucket,
            COUNT(*)                                        AS trip_count,
            ROUND(AVG(total_revenue), 2)                   AS avg_revenue,
            ROUND(SUM(total_revenue) / SUM(trip_miles), 2) AS revenue_per_mile
        FROM df
        WHERE trip_miles > 0
        GROUP BY distance_bucket
        ORDER BY MIN(trip_miles)
    """).df()

    efficiency_dist = duckdb.query("""
        SELECT
            ROUND(revenue_per_mile, 1) AS rpm_bucket,
            COUNT(*)                   AS trip_count
        FROM df
        WHERE revenue_per_mile > 0
        AND revenue_per_mile <= 30
        GROUP BY rpm_bucket
        ORDER BY rpm_bucket
    """).df()

    # ── Fleet Metrics ─────────────────────────────────────────────────────────
    overall_rpm = (
        df[df["trip_miles"] > 0]["total_revenue"].sum()
        / df[df["trip_miles"] > 0]["trip_miles"].sum()
    )
    overall_rpmn = (
        df[df["trip_minutes"] > 0]["total_revenue"].sum()
        / df[df["trip_minutes"] > 0]["trip_minutes"].sum()
    )
    median_rpm = float(
        df[(df["revenue_per_mile"] > 0) & (df["revenue_per_mile"] <= 30)][
            "revenue_per_mile"
        ].median()
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Revenue Per Mile", f"${overall_rpm:.2f}")
    col2.metric("Avg Revenue Per Minute", f"${overall_rpmn:.2f}")
    col3.metric("Median Revenue Per Mile", f"${median_rpm:.2f}")

    st.markdown("---")

    COMPANY_COLORS = {
        "Flash Cab": "#d32f2f",
        "Taxi Affiliation Services": "#2d6a9f",
        "Chicago Carriage Cab Corp": "#27ae60",
        "City Service": "#e67e22",
        "Blue Ribbon Taxi Association Inc.": "#8e44ad",
        "Choice Taxi Association": "#f39c12",
    }

    # ── Revenue Per Mile by Company ───────────────────────────────────────────
    st.subheader("Revenue Per Mile by Company")
    st.markdown(
        "⚠️ Blue Ribbon's elevated revenue per mile reflects specialisation "
        "in short premium transfers — not a data error."
    )
    fig1 = go.Figure(go.Bar(
        y=efficiency_company["company"],
        x=efficiency_company["revenue_per_mile"],
        orientation="h",
        marker_color=[
            COMPANY_COLORS.get(c, "#95a5a6")
            for c in efficiency_company["company"]
        ],
        text=[f"${v:.2f}" for v in efficiency_company["revenue_per_mile"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
    ))
    fig1.update_layout(
        xaxis_title="Revenue Per Mile ($)",
        xaxis_tickprefix="$",
        yaxis=dict(autorange="reversed"),
    )
    fig1 = apply_dark_theme(fig1, height=300)
    st.plotly_chart(fig1, use_container_width=True)

    # ── Revenue Per Mile by Distance ──────────────────────────────────────────
    st.subheader("Revenue Per Mile by Trip Distance")
    BUCKET_COLORS = ["#27ae60", "#2d6a9f", "#e67e22", "#8e44ad", "#f39c12"]
    fig2 = go.Figure(go.Bar(
        x=distance_buckets["distance_bucket"],
        y=distance_buckets["revenue_per_mile"],
        marker_color=BUCKET_COLORS[:len(distance_buckets)],
        text=[f"${v:.2f}" for v in distance_buckets["revenue_per_mile"]],
        textposition="outside",
        textfont=dict(color="#ffffff"),
        customdata=distance_buckets["trip_count"],
        hovertemplate=(
            "Distance: %{x}<br>"
            "Revenue/mile: $%{y:.2f}<br>"
            "Trips: %{customdata:,}"
        ),
    ))
    fig2.update_layout(
        yaxis_title="Revenue Per Mile ($)",
        yaxis_tickprefix="$",
    )
    fig2 = apply_dark_theme(fig2, height=350)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Distribution ──────────────────────────────────────────────────────────
    st.subheader("Distribution of Revenue Per Mile Across All Trips")
    st.markdown("Capped at $30/mile to show the main distribution clearly.")
    fig3 = go.Figure(go.Bar(
        x=efficiency_dist["rpm_bucket"],
        y=efficiency_dist["trip_count"] / 1000,
        marker_color="#2d6a9f",
        width=0.8,
    ))
    fig3.add_vline(
        x=median_rpm,
        line_dash="dash",
        line_color="#f39c12",
        annotation_text=f"Median: ${median_rpm:.2f}/mile",
        annotation_position="top right",
        annotation_font_color="#f39c12",
    )
    fig3.update_layout(
        xaxis_title="Revenue Per Mile ($)",
        yaxis_title="Trips (thousands)",
    )
    fig3 = apply_dark_theme(fig3, height=350)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Key Insight")

    shortest = distance_buckets.iloc[0]
    longest = distance_buckets.iloc[-1]
    efficiency_ratio = shortest["revenue_per_mile"] / longest["revenue_per_mile"]

    st.markdown(f"""
    <div style='background: rgba(45,106,159,0.1);
            border: 1px solid rgba(45,106,159,0.3);
            border-radius: 12px;
            padding: 16px 20px;
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.8;'>
        Trips under 1 mile generate
        <strong style='color: #ffffff;'>${shortest['revenue_per_mile']:.2f}/mile</strong> —
        <strong style='color: #ffffff;'>{efficiency_ratio:.1f}x more</strong>
        than trips over 10 miles
        (<strong style='color: #ffffff;'>${longest['revenue_per_mile']:.2f}/mile</strong>).
        Short city trips are significantly more efficient per mile due to minimum fare rules.
        However long trips still generate higher
        <strong style='color: #ffffff;'>total revenue per trip</strong>
        (${longest['avg_revenue']:.2f} vs ${shortest['avg_revenue']:.2f}).
        Optimising trip mix — balancing short high-efficiency trips with longer
        high-value trips — could meaningfully improve overall fleet performance.
    </div>
    """, unsafe_allow_html=True)