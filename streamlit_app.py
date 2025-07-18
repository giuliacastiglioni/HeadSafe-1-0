import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import plotly.graph_objects as go
import plotly.subplots as sp

st.set_page_config(layout="wide", page_title="HEADSAFE Dashboard")

# COLORI
CIPRIA = "#e8d8c3"
NERO = "#222222"
BIANCO = "#ffffff"
ROSSO = "#d9534f"
ARANCIONE = "#f0ad4e"
VERDE = "#5cb85c"
GRIGIOCHIARO = "#f7f7f7"
# CSS per sfondo nero e testo chiaro
st.markdown("""
    <style>
        body, .stApp {
            background-color: #000000;
            color: white;
        }
        .centered-img {
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# CSS aggiornato per un look più moderno e pulito
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

body {{
    font-family: 'Roboto', sans-serif;
    background-color: #000000;
    color: #e8d8c3;
    padding: 1rem 2rem;
}}

/* Titoli e sottotitoli */
h1, h2, h3, h4, h5, h6 {{
    color: #e8d8c3 !important;
}}

/* Testo generico */
p, .markdown-text-container, .stMarkdown, .css-1cpxqw2, .css-10trblm {{
    color: #e8d8c3 !important;
}}

/* Label sopra input e metriche */
label {{
    color: #e8d8c3 !important;
}}

.stButton>button {{
    background-color: {NERO};
    color: {BIANCO};
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    font-weight: 700;
    font-size: 1.1rem;
    border: none;
    transition: background-color 0.3s ease;
}}
.stButton>button:hover {{
    background-color: {ROSSO};
}}

.stMetric > div {{
    background: linear-gradient(135deg, {ARANCIONE} 0%, #f4e8db 100%);
    border-radius: 16px;
    padding: 1.2rem 2rem;
    box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    color: {NERO};
    font-weight: 700;
    font-size: 1.4rem;
    margin-bottom: 1rem;
}}

.section-box {{
    background-color: {CIPRIA};
    border-radius: 20px;
    padding: 1.5rem 2rem;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    margin-bottom: 2.5rem;
    border: 1px solid #ddd;
}}

.risk-bar-container {{
    background-color: #eee;
    border-radius: 20px;
    height: 28px;
    width: 100%;
    margin: 0.75rem 0 1.5rem 0;
    box-shadow: inset 0 3px 6px rgba(0,0,0,0.1);
}}

.risk-bar {{
    height: 28px;
    border-radius: 20px;
    transition: width 0.7s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}}

.risk-label {{
    font-weight: 700;
    font-size: 1.2rem;
    margin-top: 0.3rem;
    text-align: center;
    color: {CIPRIA};
}}

header {{
    text-align: center;
    margin-bottom: 2rem;
}}

header img {{
    max-height: 80px;
    margin-bottom: 0.5rem;
}}

header h1 {{
    margin: 0;
    font-size: 2.8rem;
    color: {CIPRIA};
}}

.chart-card {{
    background-color: {CIPRIA};
    border-radius: 20px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.07);
    margin-bottom: 2rem;
}}

</style>
""", unsafe_allow_html=True)


from PIL import Image
import base64
from io import BytesIO

# Funzione per convertire immagine in base64
def img_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Carica immagine
logo = Image.open("logo.png")
logo_base64 = img_to_base64(logo)

# Mostra immagine centrata e grande (es. 600px)
st.markdown(
    f"""
    <div style='text-align: center; margin-top: 30px;'>
        <img src='data:image/png;base64,{logo_base64}' style='width: 1000px; height: auto;' alt='HEADSAFE Logo'>
    </div>
    """,
    unsafe_allow_html=True
)
# HEADER personalizzato con possibile logo (aggiungi immagine logo se vuoi)
st.markdown("""
<header>
    <h1>HEADSAFE - Dashboard Impatti</h1>
</header>
""", unsafe_allow_html=True)

ruolo = st.selectbox("Seleziona il tuo ruolo:", ["Allenatore/Preparatore", "Atleta"])

uploaded_file = st.file_uploader("Carica il file CSV HEADSAFE", type="csv")


def get_csv(df):
    return df.to_csv(index=False).encode('utf-8')



def parse_heads_csv(file):
    lines = file.getvalue().decode("utf-8").splitlines()
    data = []
    for line in lines:
        acc_match = re.search(r"Acc \[g\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)", line)
        gyro_match = re.search(r"Gyro \[.*?/s\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)", line)
        acc_mag_match = re.search(r"Mag: ([\d\.-]+).*?Gyro", line)
        gyro_mag_match = re.search(r"Gyro .*?Mag: ([\d\.-]+)", line)

        if acc_match and gyro_match and acc_mag_match and gyro_mag_match:
            ax, ay, az = map(float, acc_match.groups())
            gx, gy, gz = map(float, gyro_match.groups())
            acc_mag = float(acc_mag_match.group(1))
            gyro_mag = float(gyro_mag_match.group(1))
            data.append({
                "ax": ax, "ay": ay, "az": az,
                "gx": gx, "gy": gy, "gz": gz,
                "accMagnitude": acc_mag,
                "gyroMagnitude": gyro_mag
            })
    return pd.DataFrame(data)

def risk_level(acc, gyr):
    # Acceleration risk
    if acc < 8:
        risk_acc = "Basso"
        color_acc = VERDE
    elif acc < 15:
        risk_acc = "Moderato"
        color_acc = ARANCIONE
    else:
        risk_acc = "Alto"
        color_acc = ROSSO

    # Gyro risk
    if gyr < 400:
        risk_gyr = "Basso"
        color_gyr = VERDE
    elif gyr < 800:
        risk_gyr = "Moderato"
        color_gyr = ARANCIONE
    else:
        risk_gyr = "Alto"
        color_gyr = ROSSO

    # Decisione complessiva
    if risk_acc == "Alto" or risk_gyr == "Alto":
        overall = "ALTO RISCHIO - Possibile danno"
        overall_color = ROSSO
    elif risk_acc == "Moderato" or risk_gyr == "Moderato":
        overall = "Rischio Moderato - Monitorare"
        overall_color = ARANCIONE
    else:
        overall = "Rischio Basso"
        overall_color = VERDE

    return (risk_acc, color_acc, risk_gyr, color_gyr, overall, overall_color)

def render_risk_bar(value, max_value=20):
    ratio = min(value / max_value, 1)
    if ratio < 0.4:
        color = VERDE
    elif ratio < 0.7:
        color = ARANCIONE
    else:
        color = ROSSO
    bar_html = f"""
    <div class="risk-bar-container">
        <div class="risk-bar" style="width:{ratio*100}%;background-color:{color};"></div>
    </div>
    """
    return bar_html


if uploaded_file:
    df = parse_heads_csv(uploaded_file)

    max_acc = df['accMagnitude'].max()
    mean_acc = df['accMagnitude'].mean()
    max_gyr = df['gyroMagnitude'].max()
    mean_gyr = df['gyroMagnitude'].mean()

    risk_acc, color_acc, risk_gyr, color_gyr, overall_risk, overall_color = risk_level(max_acc, max_gyr)

    if ruolo == "Allenatore/Preparatore":
    
        st.title("Dashboard Allenatore / Preparatore")

        # Statistiche descrittive
        st.subheader("Statistiche descrittive complete")
        descr = df.describe().T
        st.dataframe(descr.style.background_gradient(cmap='coolwarm'))

        # Calcolo impatti sopra soglia
        soglia_basso = 8
        soglia_alto = 15

        num_basso = (df['accMagnitude'] >= soglia_basso).sum()
        num_alto = (df['accMagnitude'] >= soglia_alto).sum()
        totale = len(df)

        st.markdown(f"- Campioni con accelerazione > {soglia_basso}g: **{num_basso}** ({num_basso/totale:.1%})")
        st.markdown(f"- Campioni con accelerazione > {soglia_alto}g: **{num_alto}** ({num_alto/totale:.1%})")

        # Istogrammi distribuzione accelerazioni
        st.subheader("Distribuzione accelerazioni (ax, ay, az)")

        fig = sp.make_subplots(rows=1, cols=3, subplot_titles=["Ax", "Ay", "Az"])

        fig.add_trace(go.Histogram(x=df['ax'], nbinsx=30, marker_color='red', name='Ax'), row=1, col=1)
        fig.add_trace(go.Histogram(x=df['ay'], nbinsx=30, marker_color='green', name='Ay'), row=1, col=2)
        fig.add_trace(go.Histogram(x=df['az'], nbinsx=30, marker_color='blue', name='Az'), row=1, col=3)

        fig.update_layout(title="Distribuzione accelerazioni (ax, ay, az)",
                          plot_bgcolor='black',
                          paper_bgcolor='black',
                          #font=dict(color='white'),
                          xaxis_title="Accelerazione (g)",
                          yaxis_title="Frequenza",
                          showlegend=True)
        st.plotly_chart(fig, use_container_width=True)


        # Boxplot accelerazioni
        st.subheader("Boxplot accelerazioni")
        fig = go.Figure()
        for col, color in zip(['ax', 'ay', 'az'], ['red', 'green', 'blue']):
            fig.add_trace(go.Box(y=df[col], name=col, marker_color=color))

        fig.update_layout(title="Boxplot accelerazioni",
                          plot_bgcolor='black',
                          paper_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)


        # Time series con segnali di impatto evidenziati
        st.subheader("Andamento temporale accelerazioni con picchi di impatto")
        alto_rischio = df[df['accMagnitude'] > soglia_alto]
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df['accMagnitude'], mode='lines', name='Acc Magnitude', line=dict(color='lightyellow')))

        fig.add_trace(go.Scatter(
            x=alto_rischio.index,
            y=alto_rischio['accMagnitude'],
            mode='markers',
            marker=dict(color=ROSSO, size=8),
            name='Impatto alto rischio'
        ))

        fig.update_layout(title="Andamento temporale accelerazioni con picchi di impatto",
                        plot_bgcolor='black',
                        paper_bgcolor='black',
                        xaxis_title="Campioni", yaxis_title="Accelerazione (g)")
        st.plotly_chart(fig, use_container_width=True)


        # Statistiche giroscopio
        st.subheader("Statistiche giroscopio")
        st.dataframe(df[['gx','gy','gz','gyroMagnitude']].describe())

        # Istogramma giroscopio
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df['gyroMagnitude'], nbinsx=30, marker_color='purple'))
        fig.update_layout(title="Distribuzione magnitudo giroscopio", xaxis_title="Magnitudo", yaxis_title="Frequenza",plot_bgcolor='black',
                          paper_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

        # Alert automatici
        if num_alto > 0:
            st.error(f"⚠️ Sono stati rilevati **{num_alto}** impatti con accelerazione superiore a {soglia_alto}g. Controllare attentamente il giocatore.")
        elif num_basso > 0:
            st.warning(f"⚠️ Sono stati rilevati **{num_basso}** impatti moderati con accelerazione superiore a {soglia_basso}g.")

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Valutazione rischio impatto")
        st.markdown(f"""
            <p><b>Accelerazione Massima:</b> {max_acc:.2f} g - <span style='color:{color_acc};font-weight:700'>{risk_acc}</span></p>
            <p><b>Rotazione Massima:</b> {max_gyr:.2f} °/s - <span style='color:{color_gyr};font-weight:700'>{risk_gyr}</span></p>
            <p style='font-size:1.3rem; font-weight:700; color:{overall_color};'>{overall_risk}</p>
        """, unsafe_allow_html=True)

        st.markdown(render_risk_bar(max_acc), unsafe_allow_html=True)
        st.markdown("La barra mostra il livello di rischio basato sull’accelerazione massima registrata, con colori che indicano il grado di pericolosità.")

    else:  # Atleta
        st.header("Dashboard Atleta")

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Sintesi Principali")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Accelerazione Massima (g)", f"{max_acc:.2f}")
            st.metric("Accelerazione Media (g)", f"{mean_acc:.2f}")
        with col2:
            st.metric("Rotazione Massima (°/s)", f"{max_gyr:.2f}")
            st.metric("Rotazione Media (°/s)", f"{mean_gyr:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)


#        st.markdown('<div class="section-box">', unsafe_allow_html=True)
#        st.subheader("Andamento Magnitudo Impatti")
#        fig = go.Figure()
#        fig.add_trace(go.Scatter(y=df['accMagnitude'], mode='lines', name='Acc Magnitude'))
#        fig.add_trace(go.Scatter(y=df['gyroMagnitude'], mode='lines', name='Gyro Magnitude'))

#        fig.update_layout(title="Andamento Magnitudo Impatti", xaxis_title="Campioni", yaxis_title="Magnitudo",plot_bgcolor='black',
#                          paper_bgcolor='black')
#        st.plotly_chart(fig, use_container_width=True)


        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Valutazione rischio impatto")
        st.markdown(f"""
            <p><b>Accelerazione Massima:</b> {max_acc:.2f} g - <span style='color:{color_acc};font-weight:700'>{risk_acc}</span></p>
            <p><b>Rotazione Massima:</b> {max_gyr:.2f} °/s - <span style='color:{color_gyr};font-weight:700'>{risk_gyr}</span></p>
            <p style='font-size:1.3rem; font-weight:700; color:{overall_color};'>{overall_risk}</p>
        """, unsafe_allow_html=True)
        st.markdown(render_risk_bar(max_acc), unsafe_allow_html=True)
        st.markdown("La barra di rischio indica visivamente il livello di pericolosità basato sull’accelerazione massima.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Carica un file CSV per iniziare l'analisi.")
