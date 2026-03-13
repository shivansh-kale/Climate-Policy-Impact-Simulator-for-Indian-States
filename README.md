# Climate Policy Simulator – India CO₂ Emission Prediction

This project uses **Machine Learning and interactive visualization** to predict **CO₂ emissions for Indian states** based on socio-economic and environmental factors.  
It also includes a **policy simulator** that allows users to test how different policy decisions can impact emissions.

---

## Project Overview

The goal of this project is to analyze the relationship between economic growth, infrastructure, energy usage, and environmental factors with **carbon emissions**.  

Using historical state-level data, a machine learning model predicts CO₂ emissions and allows users to simulate policy interventions.

---

## Features

• CO₂ emission prediction using Machine Learning  
• Interactive **Streamlit dashboard**  
• Policy simulation using sliders  
• Dynamic graphs and visualization  
• State-level environmental and economic analysis  

Users can simulate policies like:

- Increasing public transport usage  
- Reducing vehicles  
- Changing electricity consumption  
- Industrial output variation  

and observe how these changes affect predicted emissions.

---

## Dataset Features

The dataset includes the following variables:

- Population growth rate
- Vehicles registered
- GDP per capita
- Electricity consumption per capita
- Forest cover percentage
- Economic growth rate
- Industrial output index
- Public transport usage
- CO₂ emissions (target variable)

The dataset covers **multiple Indian states across several years**.

---

## Libraries Used

- Python  
- Scikit-Learn  
- Pandas  
- NumPy  
- Streamlit  
- Plotly

## Project Files 

finalize_project.ipynb → Model training and analysis
co2_model.pkl → Trained ML model
policy_simulator_3.py → Streamlit interactive simulator
india_co2_dataset_5year.csv → Dataset
state_info.csv → State metadata



## Running the Project

1. Install dependencies


  - pip install pandas numpy scikit-learn streamlit plotly


2. Run the simulator


  - streamlit run policy_simulator_3.py


3. Open in browser


  - http://localhost:8501
---
