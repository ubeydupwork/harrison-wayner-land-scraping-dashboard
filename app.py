import streamlit as st
import pandas as pd
import boto3

# --------------------------
# S3'ten CSV oku
# --------------------------
@st.cache_data  # Streamlit 1.22+ için cache
def load_data():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_REGION"]
    )
    obj = s3.get_object(Bucket=st.secrets["BUCKET_NAME"], Key=st.secrets["FILE_KEY"])
    df = pd.read_csv(obj["Body"])
    return df

df = load_data()

st.title("Property Dashboard")
st.set_page_config(
    page_title="Property Dashboard",
    layout="wide"   # <-- "centered" yerine "wide"
)

# --------------------------
# Sidebar filtreler
# --------------------------
st.sidebar.header("Filters")

# County / Location
counties = st.sidebar.multiselect("County", df["County"].unique())

df["Price"] = df["Price"].replace('[\$,]', '', regex=True).astype(float)
df["Acres"] = df["Acres"].astype(float)

# Sidebar min/max değerler
price_min = int(df["Price"].min())
price_max = int(df["Price"].max())
acres_min = float(df["Acres"].min())
acres_max = float(df["Acres"].max())

# Sidebar: Price
st.sidebar.subheader("Price Filter")
min_price_input = st.sidebar.number_input(
    "Min Price", min_value=price_min, max_value=price_max, value=price_min, step=1000
)
max_price_input = st.sidebar.number_input(
    "Max Price", min_value=price_min, max_value=price_max, value=price_max, step=1000
)
price_range = st.sidebar.slider(
    "Price Range",
    min_value=price_min,
    max_value=price_max,
    value=(min_price_input, max_price_input),
    step=1000
)
st.sidebar.markdown(f"**Selected Price Range: ${price_range[0]:,} - ${price_range[1]:,}**")

# Sidebar: Acres
st.sidebar.subheader("Acres Filter")
min_acres_input = st.sidebar.number_input(
    "Min Acres", min_value=acres_min, max_value=acres_max, value=acres_min, step=0.1, format="%.1f"
)
max_acres_input = st.sidebar.number_input(
    "Max Acres", min_value=acres_min, max_value=acres_max, value=acres_max, step=0.1, format="%.1f"
)
acres_range = st.sidebar.slider(
    "Acres Range",
    min_value=acres_min,
    max_value=acres_max,
    value=(min_acres_input, max_acres_input),
    step=0.1,
    format="%.1f"
)
st.sidebar.markdown(f"**Selected Acres Range: {acres_range[0]:,.1f} - {acres_range[1]:,.1f}**")

# DataFrame filtreleme örneği
filtered_df = df[
    (df["Price"] >= price_range[0]) & (df["Price"] <= price_range[1]) &
    (df["Acres"] >= acres_range[0]) & (df["Acres"] <= acres_range[1])
]

filtered_df["Price"] = filtered_df["Price"].map("${:,.0f}".format)

# --------------------------
# Tablo (tek tablo içinde URL → "Git")
# --------------------------


st.data_editor(
    filtered_df,
    column_config={
        "URL": st.column_config.LinkColumn("URL", display_text='Open Land Page')
    },
    hide_index=True,
    disabled=True,
    height=700,
    width=1200
)

