import streamlit as st

import pandas as pd

import plotly.express as px

import os

from datetime import date

 

DATA_FILE = "data.csv"

IMAGE_FOLDER = "images"

 

# -----------------------------------------------------------

# 1. Setup

# -----------------------------------------------------------

 

if not os.path.exists(IMAGE_FOLDER):

    os.makedirs(IMAGE_FOLDER)

 

# Daten initialisieren

if not os.path.exists(DATA_FILE):

    df = pd.DataFrame(columns=["Objekt", "Datum", "Wert", "Bild"])

    df.to_csv(DATA_FILE, index=False)

 

df = pd.read_csv(DATA_FILE)

 

st.set_page_config(page_title="Werttracker", layout="wide")

 

st.title("📊 Wertentwicklung deiner Gegenstände")

 

# -----------------------------------------------------------

# 2. Objekt hinzufügen

# -----------------------------------------------------------

 

st.sidebar.header("Neuen Wert eintragen")

 

objekt = st.sidebar.text_input("Name des Gegenstands")

wert = st.sidebar.number_input("Aktueller Wert (€)", min_value=0.0, format="%.2f")

datum = st.sidebar.date_input("Datum", value=date.today())

bild_datei = st.sidebar.file_uploader("Bild (optional)", type=["jpg", "png", "jpeg"])

 

if st.sidebar.button("Eintrag speichern"):

    bild_name = ""

 

    if bild_datei:

        bild_name = bild_datei.name

        with open(os.path.join(IMAGE_FOLDER, bild_name), "wb") as f:

            f.write(bild_datei.getbuffer())

 

    new_entry = pd.DataFrame([{

        "Objekt": objekt,

        "Datum": str(datum),

        "Wert": wert,

        "Bild": bild_name

    }])

 

    df = pd.concat([df, new_entry], ignore_index=True)

    df.to_csv(DATA_FILE, index=False)

    st.sidebar.success("Eintrag gespeichert!")

 

# -----------------------------------------------------------

# 3. Anzeige & Diagramme

# -----------------------------------------------------------

 

st.subheader("📦 Deine Gegenstände")

 

# Liste der Objekte

objekte = df["Objekt"].unique()

 

if len(objekte) > 0:

    auswahl = st.selectbox("Wähle ein Objekt:", objekte)

 

    gefiltert = df[df["Objekt"] == auswahl].sort_values("Datum")

 

    # Bild anzeigen

    bild = gefiltert["Bild"].iloc[-1]

    if isinstance(bild, str) and bild.strip() != "":

        st.image(os.path.join(IMAGE_FOLDER, bild), width=250)

 

    # Tabelle anzeigen

    st.dataframe(gefiltert, use_container_width=True)

 

    # Diagramm

    fig = px.line(

        gefiltert,

        x="Datum",

        y="Wert",

        title=f"Wertentwicklung: {auswahl}",

        markers=True

    )

    st.plotly_chart(fig, use_container_width=True)

 

else:

    st.info("Noch keine Daten vorhanden. Trage links im Menü etwas ein!")