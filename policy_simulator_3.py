import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="AI Climate Policy Simulator", layout="wide")

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("state_info.csv")

# -----------------------------
# Population Data (millions)
# -----------------------------
population = {
"Andhra Pradesh":54,"Arunachal Pradesh":1.6,"Assam":35,"Bihar":124,
"Chhattisgarh":29,"Goa":1.6,"Gujarat":71,"Haryana":29,
"Himachal Pradesh":7.5,"Jharkhand":38,"Karnataka":68,"Kerala":35,
"Madhya Pradesh":85,"Maharashtra":125,"Manipur":3.2,"Meghalaya":3.3,
"Mizoram":1.2,"Nagaland":2.3,"Odisha":46,"Punjab":30,
"Rajasthan":81,"Sikkim":0.7,"Tamil Nadu":77,"Telangana":39,
"Tripura":4,"Uttar Pradesh":240,"Uttarakhand":11,"West Bengal":100,
"Andaman and Nicobar Islands":0.4,"Chandigarh":1.2,
"Dadra and Nagar Haveli and Daman and Diu":0.6,"Delhi":20,
"Jammu and Kashmir":13,"Ladakh":0.3,"Lakshadweep":0.07,"Puducherry":1.6
}

df["population_million"] = df["state"].map(population)

# -----------------------------
# Emission Factors
# -----------------------------
grid_emission_factor = 0.0007
vehicle_km_per_year = 10000
vehicle_emission_factor = 0.0002
industry_emission_intensity = 0.5

# -----------------------------
# Sidebar Policy Controls
# -----------------------------
st.sidebar.title("Climate Policy Controls")

car_reduction = st.sidebar.slider("Reduce Private Vehicles (%)",0,50,20)/100
public_transport = st.sidebar.slider("Increase Public Transport (%)",0,50,20)/100
renewable_increase = st.sidebar.slider("Increase Renewable Energy (%)",0,80,30)/100
industry_efficiency = st.sidebar.slider("Industrial Efficiency (%)",0,40,15)/100

# -----------------------------
# POWER EMISSIONS
# -----------------------------
df["power_co2"] = (
    df["electricity_consumption_kwh_per_capita"] *
    df["population_million"] * 1e6 *
    grid_emission_factor
)/1e6

new_grid_factor = grid_emission_factor * (1-renewable_increase*0.9)

df["power_policy"] = (
    df["electricity_consumption_kwh_per_capita"] *
    df["population_million"] * 1e6 *
    new_grid_factor
)/1e6

# -----------------------------
# TRANSPORT EMISSIONS
# -----------------------------
df["transport_co2"] = (
    df["vehicles_registered_million"] * 1e6 *
    vehicle_km_per_year *
    vehicle_emission_factor
)/1e6

vehicle_factor = (1 - car_reduction*0.8)
public_factor = (1 - public_transport*0.6)

df["transport_policy"] = df["transport_co2"] * vehicle_factor * public_factor

# -----------------------------
# INDUSTRY EMISSIONS
# -----------------------------
df["industry_co2"] = (
    df["industrial_output_index"] *
    industry_emission_intensity
)

df["industry_policy"] = (
    df["industrial_output_index"] *
    industry_emission_intensity *
    (1-industry_efficiency*0.9)
)

# -----------------------------
# TOTAL EMISSIONS
# -----------------------------
df["current_total"] = (
    df["power_co2"] +
    df["transport_co2"] +
    df["industry_co2"]
)

df["policy_total"] = (
    df["power_policy"] +
    df["transport_policy"] +
    df["industry_policy"]
)

df["reduction_percent"] = (
    (df["current_total"] - df["policy_total"])
    / df["current_total"]
)*100

# -----------------------------
# NATIONAL METRICS
# -----------------------------
total_current = df["current_total"].sum()
total_policy = df["policy_total"].sum()

reduction = (
    (total_current-total_policy)/total_current
)*100

best_state = df.sort_values(
    "reduction_percent",
    ascending=False
).iloc[0]["state"]

# -----------------------------
# TITLE
# -----------------------------
st.title("AI Climate Policy Impact Simulator for Indian States")

# -----------------------------
# KPI DASHBOARD
# -----------------------------
col1,col2,col3,col4 = st.columns(4)

col1.metric(
"Current CO₂ Emissions (Mt)",
round(total_current,2)
)

col2.metric(
"After Policy (Mt)",
round(total_policy,2)
)

col3.metric(
"Reduction %",
round(reduction,2)
)

col4.metric(
"Best Performing State",
best_state
)

st.divider()

# -----------------------------
# TABS
# -----------------------------
tab1,tab2,tab3,tab4 = st.tabs([
"National Dashboard",
"State Analysis",
"Policy Impact",
"Dataset"
])

# -----------------------------
# TAB 1 NATIONAL
# -----------------------------
with tab1:

    st.subheader("Emission Reduction by State")

    fig = px.bar(
        df.sort_values("reduction_percent",ascending=False),
        x="state",
        y="reduction_percent",
        color="reduction_percent",
        color_continuous_scale="greens",
        title="CO₂ Reduction Potential by State"
    )

    st.plotly_chart(fig,use_container_width=True)

    source_df = pd.DataFrame({
        "Source":["Power","Transport","Industry"],
        "Emissions":[
            df["power_co2"].sum(),
            df["transport_co2"].sum(),
            df["industry_co2"].sum()
        ]
    })

    fig2 = px.pie(
        source_df,
        names="Source",
        values="Emissions",
        title="India CO₂ Emission Breakdown"
    )

    st.plotly_chart(fig2,use_container_width=True)

# -----------------------------
# TAB 2 STATE ANALYSIS
# -----------------------------
with tab2:

    state = st.selectbox(
        "Select State",
        df["state"]
    )

    state_df = df[df["state"]==state]

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Current CO₂",
        round(state_df["current_total"].values[0],2)
    )

    c2.metric(
        "After Policy",
        round(state_df["policy_total"].values[0],2)
    )

    c3.metric(
        "Reduction %",
        round(state_df["reduction_percent"].values[0],2)
    )

    fig = px.scatter(
        df,
        x="vehicles_registered_million",
        y="current_total",
        size="gdp_per_capita_inr",
        color="industrial_output_index",
        hover_name="state",
        title="Vehicles vs CO₂ Emissions"
    )

    st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# TAB 3 POLICY IMPACT
# -----------------------------
with tab3:

    compare_df = pd.DataFrame({
        "Scenario":["Current","Policy"],
        "Emissions":[
            total_current,
            total_policy
        ]
    })

    fig = px.bar(
        compare_df,
        x="Scenario",
        y="Emissions",
        color="Scenario",
        title="National Emission Comparison"
    )

    st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# TAB 4 DATASET
# -----------------------------
with tab4:

    st.subheader("Policy Simulation Data")

    st.dataframe(
        df.sort_values(
            "reduction_percent",
            ascending=False
        )
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "Download Simulation Results",
        csv,
        "climate_policy_results.csv",
        "text/csv"
    )