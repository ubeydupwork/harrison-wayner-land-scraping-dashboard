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

# --------------------------
# Refresh Data butonu
# --------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --------------------------
# Veri yükleme
# --------------------------
df = load_data()

st.set_page_config(
    page_title="Property Dashboard",
    layout="wide"
)

st.title("Property Dashboard")

# --------------------------
# Eğer veri yoksa
# --------------------------
if df.empty:
    st.warning("⚠️ No Land Found")
else:
    # Price sütununu güvenli şekilde sayıya çevir
    df["Price"] = df["Price"].replace('[\$,]', '', regex=True)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    # --------------------------
    # Sidebar filtreler
    # --------------------------
    st.header("Filters")

    # County / Location
    counties = st.multiselect("County", df["County"].unique())

    # Price Range
    price_min = int(df["Price"].min())
    price_max = int(df["Price"].max())
    price_range = st.slider("Price Range", price_min, price_max, (price_min, price_max))

    # Acres Range
    acres_min = df['Acres'].min()
    acres_max = df['Acres'].max()
    acres_range = st.slider('Acres Range', acres_min, acres_max, (acres_min, acres_max))

    # --------------------------
    # Filtreleme
    # --------------------------
    filtered = df.copy()

    if counties:
        filtered = filtered[filtered["County"].isin(counties)]

    filtered = filtered[(filtered["Price"] >= price_range[0]) & (filtered["Price"] <= price_range[1])]
    filtered = filtered[(filtered['Acres'] >= acres_range[0]) & (filtered['Acres'] <= acres_range[1])]

    filtered["Price"] = filtered["Price"].map("${:,.0f}".format)

    # --------------------------
    # Tablo
    # --------------------------
    st.data_editor(
        filtered,
        column_config={
            "URL": st.column_config.LinkColumn("URL", display_text='Open Land Page')
        },
        hide_index=True,
        disabled=True,
        height=700,
        width=1200
    )
