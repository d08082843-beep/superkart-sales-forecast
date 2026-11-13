import os
import requests
import pandas as pd
import streamlit as st

# Backend URL: inside the Docker network the backend is reachable by its container name
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("🛒 SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a store.")

tab_online, tab_batch = st.tabs(["Online prediction", "Batch prediction"])

# ------------------------------------------------------------------ online
with tab_online:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
        product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                       value=0.027, step=0.001, format="%.3f")
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)
        product_id_char = st.selectbox("Product Id prefix", ["FD", "NC", "DR"],
                                       help="FD = Food, NC = Non-Consumable, DR = Drinks")
    with col2:
        product_category = st.selectbox("Product Type Category", ["Non Perishables", "Perishables"])
        store_size = st.selectbox("Store Size", ["Medium", "High", "Small"])
        store_city = st.selectbox("Store Location City Type", ["Tier 2", "Tier 1", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type2", "Supermarket Type1",
                                                 "Departmental Store", "Food Mart"])
        store_age = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16, step=1)

    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar,
        "Product_Allocated_Area": product_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_city,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": store_age,
        "Product_Type_Category": product_category,
    }

    if st.button("Predict sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted Sales"]
                st.success(f"Predicted Product Store Sales Total: **{prediction:,.2f}**")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ------------------------------------------------------------------ batch
with tab_batch:
    st.subheader("Upload a CSV file")
    st.caption("Columns required: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, Product_MRP, "
               "Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, Store_Age_Years, "
               "Product_Type_Category")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        input_df = pd.read_csv(uploaded_file)
        st.write("Preview of the uploaded data:")
        st.dataframe(input_df.head())

        if st.button("Predict batch", type="primary"):
            try:
                files = {"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=60)
                if response.status_code == 200:
                    preds = response.json()
                    input_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(input_df))]
                    st.success(f"Predicted sales for {len(input_df)} records.")
                    st.dataframe(input_df)
                    st.download_button("Download predictions", input_df.to_csv(index=False),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"API error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
