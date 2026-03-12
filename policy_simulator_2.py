import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="India CO2 Policy Simulator", layout="wide")

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("state_info.csv")

# -----------------------------
# Add population estimates (millions)
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
# Emission factors (baseline)
# -----------------------------
grid_emission_factor = 0.0007     # tCO2 per kWh
vehicle_km_per_year = 10000
vehicle_emission_factor = 0.0002  # tCO2 per km
industry_emission_intensity = 0.5

# -----------------------------
# Policy sliders
# -----------------------------
st.title("India Climate Policy Simulator")

car_reduction = st.slider("Reduce Vehicles (%)",0,50,20)/100
public_transport = st.slider("Increase Public Transport (%)",0,50,20)/100
renewable_increase = st.slider("Increase Renewable Energy (%)",0,80,30)/100
industry_efficiency = st.slider("Industrial Efficiency (%)",0,40,15)/100

# -----------------------------
# POWER EMISSIONS
# -----------------------------
df["power_co2"] = (
    df["electricity_consumption_kwh_per_capita"] *
    df["population_million"]*1e6 *
    grid_emission_factor
)/1e6

new_grid_factor = grid_emission_factor * (1-renewable_increase)

df["power_policy"] = (
    df["electricity_consumption_kwh_per_capita"] *
    df["population_million"]*1e6 *
    new_grid_factor
)/1e6

# -----------------------------
# TRANSPORT EMISSIONS
# -----------------------------
df["transport_co2"] = (
    df["vehicles_registered_million"]*1e6 *
    vehicle_km_per_year *
    vehicle_emission_factor
)/1e6

policy_vehicles = df["vehicles_registered_million"]*(1-car_reduction)

km_shift = 1-public_transport

df["transport_policy"] = (
    policy_vehicles*1e6 *
    vehicle_km_per_year *
    vehicle_emission_factor *
    km_shift
)/1e6

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
    (1-industry_efficiency)
)

# -----------------------------
# TOTAL EMISSIONS
# -----------------------------
df["current_total"] = df["power_co2"] + df["transport_co2"] + df["industry_co2"]

df["policy_total"] = df["power_policy"] + df["transport_policy"] + df["industry_policy"]

df["reduction_percent"] = (
    (df["current_total"]-df["policy_total"])
    / df["current_total"]
)*100

# -----------------------------
# Show Table
# -----------------------------
st.subheader("Emission Reduction by State")

st.dataframe(
    df[["state","current_total","policy_total","reduction_percent"]]
    .sort_values("reduction_percent",ascending=False)
)

# -----------------------------
# Interactive Plot
# -----------------------------
fig = px.bar(
    df,
    x="state",
    y="reduction_percent",
    color="reduction_percent",
    title="CO2 Reduction by State",
    color_continuous_scale="greens"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Scatter Insight
# -----------------------------
fig2 = px.scatter(
    df,
    x="vehicles_registered_million",
    y="current_total",
    size="gdp_per_capita_inr",
    color="industrial_output_index",
    hover_name="state",
    title="Vehicles vs CO2 Emissions"
)

st.plotly_chart(fig2,use_container_width=True)