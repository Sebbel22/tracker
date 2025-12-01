import streamlit as st

import pandas as pd

import plotly.express as px

import os

from datetime import date

 

DATA_FILE = "data.csv"

IMAGE_FOLDER = "images"

 

# -----------------------------------------------------------

# 1. PAGE CONFIG & DARK MODE

# -----------------------------------------------------------

 

st.set_page_config(

    page_title="Werttracker",

    layout="wide",

    initial_sidebar_state="expanded"

)

 

# Custom Dark Theme CSS

st.markdown("""

    <style>

        body {

            background-color: #111111;

        }

        .stApp {

            background-color: #111111;

            color: white;

        }

        .css-1cpxqw2, .css-1d391kg {

            background-color: #222222 !important;

        }

    </style>

""", unsafe_allow_html=True)

 

 

# -----------------------------------------------------------

# 2. INITIALISIERUNG

# -----------------------------------------------------------

 

if not os.path.exists(IMAGE_FOLDER):

    os.makedirs(IMAGE_FOLDER)

 

if not os.path.exists(DATA_FILE):

    df = pd.DataFrame(columns=["Objekt", "Datum", "Wert", "Bild"])

    df.to_csv(DATA_FILE, index=False)

 

df = pd.read_csv(DATA_FILE)

 

# -----------------------------------------------------------

# 3. SIDEBAR – DATENEINGABE

# -----------------------------------------------------------

 

st.sidebar.header("📥 Neuen Wert eintragen")

 

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

    st.sidebar.success("Eintrag gespeichert! 🔥")

    st.rerun()

 

 

# -----------------------------------------------------------

# 4. DASHBOARD

# -----------------------------------------------------------

 

st.title("📊 Werttracker – Dashboard")

 

if len(df) > 0:

 

    df["Datum"] = pd.to_datetime(df["Datum"])

    latest_values = df.sort_values("Datum").groupby("Objekt").last()

 

    # 🔢 Berechnungen

    total_value = latest_values["Wert"].sum()

 

    # Wertänderung pro Objekt

    def calc_change(obj):

        obj_df = df[df["Objekt"] == obj].sort_values("Datum")

        if len(obj_df) < 2:

            return 0

        first = obj_df.iloc[0]["Wert"]

        last = obj_df.iloc[-1]["Wert"]

        return (last - first) / first * 100

 

    latest_values["Änderung (%)"] = latest_values.index.map(calc_change)

 

    change_series = latest_values["Änderung (%)"].dropna()

if change_series.empty:
    avg_change = 0
    top_gain = "Keine Daten"
    top_loss = "Keine Daten"
else:
    avg_change = change_series.mean()
    top_gain = change_series.idxmax()
    top_loss = change_series.idxmin()

 

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Gesamtwert", f"{total_value:,.2f} €")

    col2.metric("📈 Durchschnittliche Änderung", f"{avg_change:,.2f} %")

    col3.metric("🏆 Top-Gewinner", top_gain)

    col4.metric("📉 Top-Verlierer", top_loss)

 

    st.subheader("📦 Aktuelle Werte pro Gegenstand")

 

    fig1 = px.bar(

        latest_values,

        x=latest_values.index,

        y="Wert",

        color="Wert",

        title="Aktuelle Werte",

        text_auto=".2f",

        color_continuous_scale="Blues"

    )

    st.plotly_chart(fig1, use_container_width=True)

 

    # -----------------------------------------------------------

    # Gesamtwertentwicklung über alle Objekte

    # -----------------------------------------------------------

 

    st.subheader("📈 Gesamtwertentwicklung über Zeit")

 

    total_by_date = df.groupby("Datum")["Wert"].sum().reset_index()

    fig2 = px.line(

        total_by_date,

        x="Datum",

        y="Wert",

        title="Gesamtsumme aller Gegenstände über Zeit",

        markers=True

    )

    st.plotly_chart(fig2, use_container_width=True)

 

    # -----------------------------------------------------------

    # Tabelle aller Objekte

    # -----------------------------------------------------------

    st.subheader("📃 Tabelle aller Wertentwicklungen")

    st.dataframe(df, use_container_width=True)

 

    # -----------------------------------------------------------

    # Detailansicht eines Objekts

    # -----------------------------------------------------------

 

    st.subheader("🔍 Detailanalyse eines Gegenstands")

 

    auswahl = st.selectbox("Objekt wählen:", latest_values.index)

 

    obj_df = df[df["Objekt"] == auswahl].sort_values("Datum")

 

    bild = obj_df["Bild"].iloc[-1]

    if isinstance(bild, str) and bild.strip() != "":

        st.image(os.path.join(IMAGE_FOLDER, bild), width=250)

 

    st.dataframe(obj_df, use_container_width=True)

 

    fig3 = px.line(

        obj_df,

        x="Datum",

        y="Wert",

        title=f"Wertentwicklung: {auswahl}",

        markers=True

    )

    st.plotly_chart(fig3, use_container_width=True)

 

else:

    st.info("Noch keine Daten vorhanden. Trage links im Menü Werte ein!")


