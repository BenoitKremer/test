import streamlit as st
import pandas as pd
import plotly.express as px

# Fonction pour charger les données CSV
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convertir en datetime
    return df

# Interface Streamlit
st.title("📊 Analyse de production de tags par tranche de 5min")

# Upload de fichier CSV
uploaded_file = st.file_uploader("Chargez un fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Grouper par périodes de 5 minutes
    df["Time Interval"] = df["timestamp"].dt.floor("5T")
    count_df = df.groupby("Time Interval").size().reset_index(name="tagNumber")

    # Afficher un histogramme interactif avec Plotly
    fig = px.bar(count_df, x="Time Interval", y="tagNumber", title="Nombre de tags produits toutes les 5 minutes",
                 labels={"Time Interval": "Temps", "tagNumber": "Nombre de tags"},
                 color="tagNumber")
    
    fig.update_layout(bargap=0.05)

    st.plotly_chart(fig, use_container_width=True)

    # Affichage des carrés de couleur
    st.subheader("📌 Indicateur de production de tags")
    
    def get_color(tag_count):
        if tag_count < 500:
            return "🔴"
        elif 500 <= tag_count <= 1000:
            return "🟡"
        else:
            return "🟢"

    # Création d'une colonne avec les couleurs
    count_df["Status"] = count_df["tagNumber"].apply(get_color)

    # Affichage des résultats sous forme de tableau coloré
    st.dataframe(count_df.style.applymap(lambda x: "color: white; background-color: red" if x == "🔴" else 
                                                  "color: black; background-color: yellow" if x == "🟡" else 
                                                  "color: white; background-color: green" if x == "🟢" else ""))
