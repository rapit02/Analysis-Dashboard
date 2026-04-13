# data.py — Single source of truth for data loading, cleaning and queries

import pandas as pd
import duckdb
import calendar
import streamlit as st

DATA_PATH = "../data/chicago_taxi_2020.csv"

# ── Load & clean ──────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and clean the Chicago Taxi 2020 dataset."""
    df = pd.read_csv(
        DATA_PATH,
        dtype={
            "unique_key": "str",
            "taxi_id": "str",
            "fare": "float32",
            "tips": "float32",
            "tolls": "float32",
            "extras": "float32",
            "payment_type": "category",
            "company": "category",
            "trip_miles": "float32",
            "trip_seconds": "float32",
        },
    )

    df["trip_start_timestamp"] = pd.to_datetime(df["trip_start_timestamp"], utc=True)
    df = df.dropna()
    df = df[~((df["trip_miles"] == 0) & (df["trip_seconds"] == 0))]
    df = df[df["fare"] <= 500]
    df = df[df["trip_miles"] <= 100]
    df = df[df["trip_seconds"] <= 14400]
    df = df[df["extras"] <= 100]
    df = df[~((df["trip_miles"] == 0) & (df["fare"] > 20))]

    df["total_revenue"]      = df["fare"] + df["tips"] + df["tolls"] + df["extras"]
    df["trip_minutes"]       = df["trip_seconds"] / 60
    df["revenue_per_mile"]   = df["total_revenue"] / df["trip_miles"].replace(0, float("nan"))
    df["revenue_per_minute"] = df["total_revenue"] / df["trip_minutes"].replace(0, float("nan"))
    df["tip_rate"]           = df["tips"] / df["fare"].replace(0, float("nan"))
    df["hour"]               = df["trip_start_timestamp"].dt.hour
    df["day_of_week"]        = df["trip_start_timestamp"].dt.day_name()
    df["month"]              = df["trip_start_timestamp"].dt.month
    df["month_name"]         = df["trip_start_timestamp"].dt.strftime("%b")

    df = df[df["trip_start_timestamp"] < "2020-07-01"].copy()
    return df


# ── Queries ───────────────────────────────────────────────────────────────────

def query_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly trip count, revenue and avg revenue per trip."""
    return duckdb.query("""
        SELECT
            month,
            month_name,
            COUNT(*)                          AS trip_count,
            ROUND(SUM(total_revenue), 2)      AS total_revenue,
            ROUND(AVG(total_revenue), 2)      AS avg_revenue_per_trip
        FROM df
        GROUP BY month, month_name
        ORDER BY month
    """).df()


def query_hourly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Trip count and avg revenue by hour of day."""
    return duckdb.query("""
        SELECT
            hour,
            COUNT(*)                     AS trip_count,
            ROUND(AVG(total_revenue), 2) AS avg_revenue
        FROM df
        GROUP BY hour
        ORDER BY hour
    """).df()


def query_daily_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Trip count by day of week."""
    return duckdb.query("""
        SELECT
            day_of_week,
            COUNT(*) AS trip_count
        FROM df
        GROUP BY day_of_week
    """).df()


def query_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Trip count by hour and day of week for heatmap."""
    return duckdb.query("""
        SELECT
            day_of_week,
            hour,
            COUNT(*) AS trip_count
        FROM df
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour
    """).df()


def query_company_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue, trips and avg revenue per trip by company."""
    return duckdb.query("""
        SELECT
            company,
            COUNT(*)                                        AS trip_count,
            ROUND(SUM(total_revenue), 2)                   AS total_revenue,
            ROUND(AVG(total_revenue), 2)                   AS avg_revenue_per_trip,
            ROUND(SUM(total_revenue) / SUM(trip_miles), 2) AS revenue_per_mile
        FROM df
        WHERE company IS NOT NULL
        AND trip_miles > 0
        GROUP BY company
        HAVING COUNT(*) > 10
        ORDER BY total_revenue DESC
    """).df()


def query_payment_behaviour(df: pd.DataFrame) -> pd.DataFrame:
    """Trip count, revenue and tip rate by payment type."""
    return duckdb.query("""
        SELECT
            payment_type,
            COUNT(*)                                                                AS trip_count,
            ROUND(AVG(total_revenue), 2)                                            AS avg_revenue_per_trip,
            ROUND(AVG(tips), 2)                                                     AS avg_tip,
            ROUND(AVG(CASE WHEN fare > 0 THEN tips / fare ELSE NULL END) * 100, 2) AS avg_tip_rate_pct
        FROM df
        WHERE payment_type IS NOT NULL
        GROUP BY payment_type
        HAVING COUNT(*) > 10
        ORDER BY trip_count DESC
    """).df()


def query_market_rpatd(df: pd.DataFrame) -> pd.DataFrame:
    """Daily market-wide RPATD with 7-day rolling average and recovery rate."""
    daily = duckdb.query("""
        SELECT
            DATE_TRUNC('day', trip_start_timestamp)::DATE          AS trip_date,
            COUNT(*)                                               AS total_trips,
            COUNT(DISTINCT taxi_id)                                AS active_taxis,
            ROUND(SUM(total_revenue), 2)                           AS total_revenue,
            ROUND(SUM(total_revenue) / COUNT(DISTINCT taxi_id), 2) AS rpatd
        FROM df
        GROUP BY DATE_TRUNC('day', trip_start_timestamp)::DATE
        ORDER BY trip_date
    """).df()

    daily["trip_date"]       = pd.to_datetime(daily["trip_date"])
    daily["rpatd_7day_avg"]  = daily["rpatd"].rolling(7).mean()

    baseline = daily[daily["trip_date"] < "2020-03-01"]["rpatd"].mean()
    daily["recovery_rate"]   = (daily["rpatd"] / baseline * 100).round(1)
    daily["baseline"]        = round(baseline, 2)

    return daily


def query_company_rpatd(df: pd.DataFrame) -> pd.DataFrame:
    """Daily RPATD by company."""
    company_daily = duckdb.query("""
        SELECT
            DATE_TRUNC('day', trip_start_timestamp)::DATE          AS trip_date,
            company,
            COUNT(DISTINCT taxi_id)                                AS active_taxis,
            ROUND(SUM(total_revenue), 2)                           AS total_revenue,
            ROUND(SUM(total_revenue) / COUNT(DISTINCT taxi_id), 2) AS rpatd
        FROM df
        WHERE company IS NOT NULL
        GROUP BY DATE_TRUNC('day', trip_start_timestamp)::DATE, company
        ORDER BY trip_date, company
    """).df()

    company_daily["trip_date"] = pd.to_datetime(company_daily["trip_date"])
    return company_daily


def query_overview_metrics(df: pd.DataFrame) -> dict:
    """Top-level summary metrics for the overview page."""
    if df is None or len(df) == 0:
        return {
            "total_trips": 0,
            "total_revenue": 0,
            "avg_revenue_per_trip": 0,
            "avg_trip_miles": 0,
            "avg_trip_minutes": 0,
            "unique_taxis": 0,
            "unique_companies": 0,
        }

    result = duckdb.query("""
        SELECT
            COUNT(*)                     AS total_trips,
            ROUND(SUM(total_revenue), 2) AS total_revenue,
            ROUND(AVG(total_revenue), 2) AS avg_revenue_per_trip,
            ROUND(AVG(trip_miles), 2)    AS avg_trip_miles,
            ROUND(AVG(trip_minutes), 2)  AS avg_trip_minutes,
            COUNT(DISTINCT taxi_id)      AS unique_taxis,
            COUNT(DISTINCT company)      AS unique_companies
        FROM df
    """).df()

    return result.iloc[0].to_dict()


# ── Chart theme ───────────────────────────────────────────────────────────────

def apply_dark_theme(fig, height=400):
    """Apply consistent dark theme to all plotly charts."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1a1d2e",
        font=dict(color="#ffffff", family="sans-serif"),
        xaxis=dict(
            gridcolor="#2d3748",
            linecolor="#2d3748",
            tickcolor="#8892a4",
        ),
        yaxis=dict(
            gridcolor="#2d3748",
            linecolor="#2d3748",
            tickcolor="#8892a4",
        ),
        legend=dict(
            bgcolor="rgba(26,29,46,0.8)",
            bordercolor="#2d6a9f",
            borderwidth=1,
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig