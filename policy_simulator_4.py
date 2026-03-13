import streamlit as st
import pandas as pd
import plotly.express as px
import pickle

st.set_page_config(page_title="AI Climate Policy Simulator", layout="wide")

df = pd.read_csv("india_co2_dataset_realistic.csv")

# Use latest year per state
df = df.sort_values("year")
df = df.groupby("state").tail(1).reset_index(drop=True)
df = df.sort_values("state")


model = pickle.load(open("co2_model.pkl","rb"))

# -----------------------------
# Create One-Hot Encoding for State
# -----------------------------
df_encoded = pd.get_dummies(df, columns=["state"])

# -----------------------------
# Align Features With Model
# -----------------------------
model_features = model.feature_names_in_

for col in model_features:
    if col not in df_encoded.columns:
        df_encoded[col] = 0

df_encoded = df_encoded[model_features]

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.title("Climate Policy Controls")

car_reduction = st.sidebar.slider("Reduce Private Vehicles (%)",0,50,20)/100
public_transport = st.sidebar.slider("Increase Public Transport (%)",0,50,20)/100
renewable_increase = st.sidebar.slider("Increase Renewable Energy (%)",0,80,30)/100
industry_efficiency = st.sidebar.slider("Industrial Efficiency (%)",0,40,15)/100

# -----------------------------
# CURRENT EMISSIONS
# -----------------------------
df["current_total"] = model.predict(df_encoded)

# -----------------------------
# APPLY POLICY CHANGES
# -----------------------------
df_policy = df.copy()

df_policy["vehicles_registered_million"] *= (1 - car_reduction)

df_policy["public_transport_usage_percent"] *= (1 + public_transport)

df_policy["electricity_consumption_kwh_per_capita"] *= (1 - renewable_increase*0.4)

df_policy["industrial_output_index"] *= (1 - industry_efficiency*0.3)

# -----------------------------
# Encode Policy Dataset
# -----------------------------
df_policy_encoded = pd.get_dummies(df_policy, columns=["state"])

for col in model_features:
    if col not in df_policy_encoded.columns:
        df_policy_encoded[col] = 0

df_policy_encoded = df_policy_encoded[model_features]


# -----------------------------
# POLICY EMISSIONS
# -----------------------------
df["policy_total"] = model.predict(df_policy_encoded)

# -----------------------------
# Scale emissions to realistic range
# -----------------------------
df["current_total"] = df["current_total"] / 15
df["policy_total"] = df["policy_total"] / 15

# -----------------------------
# REDUCTION
# -----------------------------
df["reduction_percent"] = (
    (df["current_total"] - df["policy_total"])
    / df["current_total"]
) * 100

# -----------------------------
# NATIONAL METRICS
# -----------------------------
total_current = df["current_total"].sum()
total_policy = df["policy_total"].sum()

reduction = ((total_current-total_policy)/total_current)*100

best_state = df.sort_values(
    "reduction_percent",
    ascending=False
).iloc[0]["state"]

# -----------------------------
# TITLE
# -----------------------------
st.title("AI Climate Policy Impact Simulator for Indian States")

col1,col2,col3,col4 = st.columns(4)

col1.metric("Current CO₂ Emissions (Mt)",round(total_current,2))
col2.metric("After Policy (Mt)",round(total_policy,2))
col3.metric("Reduction %",round(reduction,2))
col4.metric("Best Performing State",best_state)

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
# NATIONAL TAB
# -----------------------------
with tab1:

    fig = px.bar(
        df.sort_values("reduction_percent",ascending=False),
        x="state",
        y="reduction_percent",
        color="reduction_percent",
        color_continuous_scale="greens",
        title="CO₂ Reduction Potential by State"
    )

    st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# STATE ANALYSIS
# -----------------------------
with tab2:

    state = st.selectbox("Select State",df["state"].unique())

    state_df = df[df["state"]==state]

    c1,c2,c3 = st.columns(3)

    c1.metric("Current CO₂",round(state_df["current_total"].values[0],2))
    c2.metric("After Policy",round(state_df["policy_total"].values[0],2))
    c3.metric("Reduction %",round(state_df["reduction_percent"].values[0],2))

# -----------------------------
# POLICY IMPACT
# -----------------------------
with tab3:

    compare_df = pd.DataFrame({
        "Scenario":["Current","Policy"],
        "Emissions":[total_current,total_policy]
    })

    fig = px.bar(compare_df,x="Scenario",y="Emissions",color="Scenario")

    st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# DATASET
# -----------------------------
with tab4:

    st.dataframe(df)

    csv = df.to_csv(index=False)

    st.download_button(
        "Download Simulation Results",
        csv,
        "climate_policy_results.csv",
        "text/csv"
    )