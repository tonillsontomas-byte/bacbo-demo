import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import ImageGrab
import time
from ultralytics import YOLO
from playsound import playsound
import threading

# ================= CONFIG =================
st.set_page_config(page_title="MT Bac Bo PROFISSIONAL YOLO", layout="wide")

# ================= ESTILO =================
st.markdown("""
<style>
.big {font-size:38px; font-weight:bold; text-align:center}
.player {color:#1f77ff}
.banker {color:#d62728}
.tie {color:#f1c40f}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "historico" not in st.session_state:
    st.session_state.historico = []
if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = None

# ================= YOLO =================
# Modelo treinado YOLOv8 para Bac Bo
model = YOLO("bacbo_yolov8.pt")  # substitua com o caminho do modelo treinado

# ================= FUNÇÕES =================
def forca_sinal(hist):
    if len(hist) < 5:
        return 0
    ultimos = hist[-5:]
    p = ultimos.count("PLAYER")
    b = ultimos.count("BANKER")
    return max(p, b) / 5 * 100

def gerar_sinal(hist):
    if len(hist) < 4:
        return "AGUARDAR", 0
    ultimos = hist[-3:]
    if ultimos.count("PLAYER") >= 2:
        return "PLAYER", forca_sinal(hist)
    if ultimos.count("BANKER") >= 2:
        return "BANKER", forca_sinal(hist)
    if ultimos[-1] == "TIE":
        return "EMPATE", 50
    return "AGUARDAR", 0

def tocar_alerta():
    playsound("alerta.mp3")

def capturar_resultado_yolo(region=None):
    if region:
        img = ImageGrab.grab(bbox=region)
    else:
        img = ImageGrab.grab()
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    results = model(img_cv)
    classes = [r.boxes.cls[0].item() for r in results]
    # Supondo que classe 0=PLAYER, 1=BANKER, 2=TIE
    if 0 in classes:
        return "PLAYER"
    elif 1 in classes:
        return "BANKER"
    elif 2 in classes:
        return "TIE"
    return None

# ================= TÍTULO =================
st.title("🤖 MT — Bac Bo PROFISSIONAL YOLO (REAL)")

# ================= POWER =================
if st.button("⚡ POWER / RESET"):
    st.session_state.historico = []
    st.session_state.ultimo_resultado = None
    st.success("MT reiniciado")

st.markdown("### 🟢 MODO: REAL (fixo)")
st.divider()

# ================= CAPTURA CONTÍNUA =================
st.markdown("## 🤖 Captura automática contínua (YOLO)")

REGIAO_JOGO = (100, 200, 800, 600)
intervalo = st.slider("⏱ Intervalo de captura (segundos)", 1, 10, 3)

def loop_captura_yolo():
    while True:
        resultado = capturar_resultado_yolo(REGIAO_JOGO)
        if resultado and resultado != st.session_state.ultimo_resultado:
            st.session_state.historico.append(resultado)
            st.session_state.ultimo_resultado = resultado
            st.success(f"Resultado capturado: {resultado}")
            threading.Thread(target=tocar_alerta, daemon=True).start()
        time.sleep(intervalo)

if st.button("▶️ Iniciar captura automática"):
    st.info("Captura automática iniciada. Não feche o Streamlit.")
    threading.Thread(target=loop_captura_yolo, daemon=True).start()

# ================= SINAL =================
sinal, forca = gerar_sinal(st.session_state.historico)
st.divider()
st.markdown("## 📢 Sinal AO VIVO")
if sinal == "PLAYER":
    st.markdown(f"<div class='big player'>ENTRAR PLAYER 🔵<br>Força {forca:.0f}%</div>", unsafe_allow_html=True)
elif sinal == "BANKER":
    st.markdown(f"<div class='big banker'>ENTRAR BANKER 🔴<br>Força {forca:.0f}%</div>", unsafe_allow_html=True)
elif sinal == "EMPATE":
    st.markdown("<div class='big tie'>EMPATE 🟡</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='big'>AGUARDAR ⏳</div>", unsafe_allow_html=True)

# ================= HISTÓRICO =================
st.divider()
st.markdown("## 📊 Histórico")
if st.session_state.historico:
    df = pd.DataFrame({
        "Ronda": range(1, len(st.session_state.historico)+1),
        "Resultado": st.session_state.historico
    })
    st.dataframe(df, use_container_width=True)
