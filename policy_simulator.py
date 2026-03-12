import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle

# Load dataset
df = pd.read_csv("state_info.csv")

co2_targets = {
"Andhra Pradesh":150,
"Arunachal Pradesh":4,
"Assam":35,
"Bihar":60,
"Chhattisgarh":110,
"Goa":6,
"Gujarat":220,
"Haryana":90,
"Himachal Pradesh":12,
"Jharkhand":85,
"Karnataka":170,
"Kerala":65,
"Madhya Pradesh":140,
"Maharashtra":310,
"Manipur":3,
"Meghalaya":6,
"Mizoram":2,
"Nagaland":2,
"Odisha":125,
"Punjab":70,
"Rajasthan":160,
"Sikkim":1,
"Tamil Nadu":200,
"Telangana":130,
"Tripura":5,
"Uttar Pradesh":290,
"Uttarakhand":18,
"West Bengal":180,
"Andaman and Nicobar Islands":1,
"Chandigarh":2,
"Dadra and Nagar Haveli and Daman and Diu":8,
"Delhi":70,
"Jammu and Kashmir":15,
"Ladakh":1,
"Lakshadweep":0.5,
"Puducherry":4
}
df["co2_emissions_mt"] = df["state"].map(co2_targets)



# Load trained pipeline
pipeline = pickle.load(open("co2_model.pkl","rb"))

st.title("India CO₂ Policy Simulator")

st.write("Simulate how policy changes affect state-level emissions.")

# POLICY SLIDERS
car_reduction = st.slider("Reduce vehicles (%)",0,50,20)
public_transport = st.slider("Increase public transport (%)",0,50,20)
renewable_energy = st.slider("Renewable energy increase (%)",0,50,20)
industry_efficiency = st.slider("Industrial efficiency (%)",0,40,10)

# Convert to decimal
car_reduction /= 100
public_transport /= 100
renewable_energy /= 100
industry_efficiency /= 100

policy_df = df.copy()

# Apply policy changes
policy_df["vehicles_registered_million"] *= (1 - car_reduction)
policy_df["public_transport_usage_percent"] *= (1 + public_transport)
policy_df["electricity_consumption_kwh_per_capita"] *= (1 - renewable_energy)
policy_df["industrial_output_index"] *= (1 - industry_efficiency)

# Predict emissions
X = policy_df.drop(["state","co2_emissions_mt"],axis=1)

policy_df["predicted_emissions"] = pipeline.predict(X)

# Compare emissions
comparison = pd.DataFrame({
    "state": df["state"],
    "current": df["co2_emissions_mt"],
    "policy": policy_df["predicted_emissions"]
})

comparison["reduction_%"] = (
    (comparison["current"] - comparison["policy"]) /
    comparison["current"]
) * 100

st.subheader("Emission Reduction by State")

st.dataframe(comparison)

# Plot
fig, ax = plt.subplots(figsize=(10,5))

ax.bar(comparison["state"], comparison["reduction_%"])

plt.xticks(rotation=90)
plt.ylabel("CO₂ Reduction (%)")
plt.title("Impact of Policy Changes")

st.pyplot(fig)


import plotly.express as px

fig = px.bar(
    comparison,
    x="state",
    y="reduction_%",
    title="CO₂ Reduction by State",
    color="reduction_%",
    color_continuous_scale="greens"
)

st.plotly_chart(fig, use_container_width=True)



fig = px.scatter(
    df,
    x="vehicles_registered_million",
    y="co2_emissions_mt",
    size="gdp_per_capita_inr",
    color="industrial_output_index",
    hover_name="state",
    title="Vehicles vs CO₂ Emissions"
)

st.plotly_chart(fig, use_container_width=True)




fig = px.bar(
    comparison,
    x="state",
    y=["current","policy"],
    barmode="group",
    title="Current vs Policy CO₂ Emissions"
)

st.plotly_chart(fig, use_container_width=True)



fig = px.choropleth(
    comparison,
    geojson="india_states.geojson",
    locations="state",
    color="policy",
    featureidkey="properties.ST_NM",
    title="Predicted CO₂ Emissions by State"
)

fig.update_geos(fitbounds="locations", visible=True)

st.plotly_chart(fig)