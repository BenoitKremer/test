import toml
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import logging
from pathlib import Path
from datetime import timedelta

# Fonction pour charger les données CSV
# !--ATTENTION au fuseaux horaire et le changement d'heure--!
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.sort_values(by= "timestamp", inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"]) + timedelta(hours=2)# +2h permet de corriger le fuseaux horaire
    return df

machines = ["I-Connect 1", "I-Connect 2", "I-Connect 3", "I-Connect 4", "I-Connect 5", "I-Connect 6", "I-Connect 7", "I-Connect 8"]
shift = ["Jour", "Nuit"]
# Interface Streamlit
st.title("📊 Analyse de production de tags par tranche de 5min")

base_dir = Path(st.secrets['paths']['base_dir'])

# Sélection des filtres
date_selectionnee = st.date_input("Choisissez une date :", datetime.date.today())
date_formatee = date_selectionnee.strftime("%d_%m_%Y")
choixShift = st.selectbox("Choisissez une équipe :", shift)
choixMachine = st.selectbox("Choisissez une machine :", machines)

# Upload de fichier CSV
uploaded_file = base_dir / choixMachine / f"JOBS_{date_formatee}_{choixShift}.csv"

# Si le bouton est appuyé on applique les filtres
if st.button("Appliquer les filtres"):
  if uploaded_file is not None:
        df = load_data(uploaded_file)

        # Grouper par périodes de 5 minutes
        df["Time Intervale"] = df["timestamp"].dt.floor("5min")
        count_df = df.groupby("Time Intervale").size().reset_index(name="tagNumber")

        # Afficher un histogramme interactif avec Plotly
        fig = px.bar(count_df, x="Time Intervale", y="tagNumber", title="Nombre de tags produits toutes les 5 minutes",
                    labels={"Time Intervale": "Temps", "tagNumber": "Nombre de tags"},
                    color="tagNumber")
        
        fig.update_layout(bargap=0.05)

        # Ajout de la ligne d'objectif
        fig.add_hline(y=1000, line_dash="solid", line_color="black", annotation_text="Objectif", annotation_position="right")

        df["Time Hours"] = df["timestamp"].dt.floor("1h")
        count_df2 = df.groupby("Time Hours").size().reset_index(name="tagNumber")

        fig2 = px.bar(count_df2, x="Time Hours", y="tagNumber", title="Tags regroupé par heures :",
                     labels={"Time Hours": "Temps", "tagNumber": "Nombre de tags"},
                     color="tagNumber")
        
        fig2.update_layout(bargap=0.05)

        fig2.add_hline(y=12000, line_dash="solid", line_color="black", annotation_text="Objectif", annotation_position="right")

        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Affichage des carrés de couleur
        st.subheader("📌 Indicateur de production de tags")
        
        def get_color(tag_count):
            if tag_count < 500:
                return "🔴"
            elif 500 <= tag_count < 1000:
                return "🟡"
            else:
                return "🟢"

        # Création d'une colonne avec les couleurs
        count_df["Status"] = count_df["tagNumber"].apply(get_color)

        # Affichage des résultats sous forme de tableau coloré
        st.dataframe(count_df.style.map(lambda x: "color: white; background-color: red" if x == "🔴" else 
                                                        "color: black; background-color: yellow" if x == "🟡" else 
                                                        "color: white; background-color: green" if x == "🟢" else ""))
        
        # Calcul du total des tags produits
        total_tags = count_df["tagNumber"].sum()

        # Affichage du total sous forme de métrique
        st.metric(label="📌 Total des tags produits", value=f"{total_tags:,}")

        # Calcul des pourcentages
        total_intervals = len(count_df)
        red_count = (count_df["Status"] == "🔴").sum()
        yellow_count = (count_df["Status"] == "🟡").sum()
        green_count = (count_df["Status"] == "🟢").sum()

        data_pie = pd.DataFrame({
            "Catégorie": ["Non atteint (<500)", "Partiellement atteint (500-1000)", "Atteint (>1000)"],
            "Nombre": [red_count, yellow_count, green_count]
        })

        # Création du camembert
        fig_pie = px.pie(data_pie, values="Nombre", names="Catégorie", 
                        title="Répartition des périodes de 5 min par performance",
                        color="Catégorie",
                        color_discrete_map={"Non atteint (<500)": "red",
                                            "Partiellement atteint (500-1000)": "yellow",
                                            "Atteint (>1000)": "green"},
                        hole=0.3)  # Pour un effet "donut"

        # Affichage du camembert
        st.plotly_chart(fig_pie, use_container_width=True)

