import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Smart Warehouse System", layout="wide")

FILE_PATH = "inventory.csv"

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
    else:
        df = pd.DataFrame(
            columns=["Item", "Category", "Quantity", "Min_Level", "Location"]
        )
        df.to_csv(FILE_PATH, index=False)

    # Clean data
    df = df.dropna(how="all")

    if "Item" in df.columns:
        df = df[df["Item"].notna()]
        df = df[df["Item"].astype(str).str.strip() != ""]

    if "Quantity" in df.columns:
        df["Quantity"] = pd.to_numeric(
            df["Quantity"], errors="coerce"
        ).fillna(0)

    if "Min_Level" in df.columns:
        df["Min_Level"] = pd.to_numeric(
            df["Min_Level"], errors="coerce"
        ).fillna(0)

    return df

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

df = load_data()

# ---------------- TITLE ----------------
st.title("🏭 Smart Warehouse Management System")

# ---------------- DASHBOARD ----------------
st.header("📊 Dashboard")

low_stock = df[df["Quantity"] <= df["Min_Level"]]

col1, col2, col3 = st.columns(3)

col1.metric("Total Items", len(df))
col2.metric("Total Stock", int(df["Quantity"].sum()) if not df.empty else 0)
col3.metric("Low Stock Items", len(low_stock))

st.divider()

# ---------------- SEARCH ----------------
st.header("🔍 Search Inventory")

search = st.text_input("Search Item")

if search:
    filtered_df = df[
        df["Item"].astype(str).str.contains(search, case=False, na=False)
    ]
else:
    filtered_df = df

st.dataframe(filtered_df, width="stretch")

st.divider()

# ---------------- ADD ITEM ----------------
st.header("➕ Add New Item")

with st.form("add_item_form"):

    item = st.text_input("Item Name")
    category = st.text_input("Category")
    quantity = st.number_input("Quantity", min_value=0)
    min_level = st.number_input("Minimum Level", min_value=0)
    location = st.text_input("Location")

    submitted = st.form_submit_button("Add Item")

    if submitted:

        if not item.strip():
            st.error("Please enter item name")

        else:

            new_row = pd.DataFrame(
                [[item, category, quantity, min_level, location]],
                columns=df.columns
            )

            df = pd.concat([df, new_row], ignore_index=True)

            save_data(df)

            st.success("✅ Item Added Successfully")

st.divider()

# ---------------- UPDATE STOCK ----------------
st.header("✏️ Update Stock")

if not df.empty:

    selected_item = st.selectbox(
        "Select Item",
        df["Item"]
    )

    current_qty = int(
        df.loc[df["Item"] == selected_item, "Quantity"].values[0]
    )

    new_quantity = st.number_input(
        "New Quantity",
        min_value=0,
        value=current_qty
    )

    if st.button("Update Quantity"):

        df.loc[
            df["Item"] == selected_item,
            "Quantity"
        ] = new_quantity

        save_data(df)

        st.success("✅ Stock Updated")

st.divider()

# ---------------- DELETE ITEM ----------------
st.header("🗑️ Delete Item")

if not df.empty:

    delete_item = st.selectbox(
        "Choose Item To Delete",
        df["Item"],
        key="delete"
    )

    if st.button("Delete Item"):

        df = df[df["Item"] != delete_item]

        save_data(df)

        st.success("✅ Item Deleted")

st.divider()

# ---------------- INVENTORY TABLE ----------------
st.header("📦 Inventory Status")

df = load_data()

st.dataframe(df, width="stretch")

st.divider()

# ---------------- LOW STOCK ALERT ----------------
st.header("🚨 Low Stock Alerts")

low_stock = df[df["Quantity"] <= df["Min_Level"]]

if low_stock.empty:

    st.success("✅ All Stock Levels Are Healthy")

else:

    st.error("⚠️ Low Stock Items Found")

    st.dataframe(low_stock, width="stretch")

st.divider()

# ---------------- DOWNLOAD REPORT ----------------
st.header("⬇️ Download Inventory Report")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name="warehouse_inventory.csv",
    mime="text/csv"
)

st.divider()

# ---------------- CHART ----------------
st.header("📈 Stock Overview")

if not df.empty:

    chart_df = df.set_index("Item")

    st.bar_chart(chart_df["Quantity"])

else:

    st.warning("No Inventory Data Available")