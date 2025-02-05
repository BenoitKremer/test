import streamlit as st
import pandas as pd
import plotly.express as px

# Fonction pour charger les données CSV
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])  # Convertir en datetime
    return df

# Interface Streamlit
st.title("📊 Analyse de production de tags par tranche de 5min")

# Upload de fichier CSV
uploaded_file = st.file_uploader("Chargez un fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Grouper par périodes de 5 minutes
    df["Time Interval"] = df["Timestamp"].dt.floor("5T")
    count_df = df.groupby("Time Interval").size().reset_index(name="Tag Count")

    # Afficher un histogramme interactif avec Plotly
    fig = px.bar(count_df, x="Time Interval", y="Tag Count", title="Nombre de tags produits toutes les 5 minutes",
                 labels={"Time Interval": "Temps", "Tag Count": "Nombre de tags"},
                 color="Tag Count")
    
    fig.update_layout(bargap=0.05)

    st.plotly_chart(fig, use_container_width=True)
