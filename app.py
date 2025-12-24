import streamlit as st
import pandas as pd
from collections import deque

st.set_page_config(page_title="Bac Bo IA - Analista", layout="wide")

# ===== ESTILO (CORES) =====
st.markdown("""
<style>
.player { color: #1f77ff; font-weight: bold; font-size: 40px; }
.banker { color: #ff2b2b; font-weight: bold; font-size: 40px; }
.tie { color: #9b59b6; font-weight: bold; font-size: 40px; }
.wait { color: #aaaaaa; font-weight: bold; font-size: 40px; }
</style>
""", unsafe_allow_html=True)

# ===== ESTADO =====
if "historico" not in st.session_state:
    st.session_state.historico = deque(maxlen=50)

def gerar_sinal(hist):
    if len(hist) < 5:
        return "AGUARDAR", "FRACO"

    if hist.count("PLAYER") >= 3:
        return "PLAYER", "MÉDIO"

    if hist.count("BANKER") >= 3:
        return "BANKER", "MÉDIO"

    if hist.count("TIE") >= 2:
        return "TIE", "FORTE"

    return "AGUARDAR", "FRACO"

def sinal_html(sinal):
    if sinal == "PLAYER":
        return '<div class="player">PLAYER</div>'
    if sinal == "BANKER":
        return '<div class="banker">BANKER</div>'
    if sinal == "TIE":
        return '<div class="tie">TIE</div>'
    return '<div class="wait">AGUARDAR</div>'

# ===== TÍTULO =====
st.title("🎲 Bac Bo — Bot Analista Externo")

# ===== BOTÕES =====
st.subheader("📥 Inserir resultado da ronda")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔵 PLAYER"):
        st.session_state.historico.append("PLAYER")

with col2:
    if st.button("🔴 BANKER"):
        st.session_state.historico.append("BANKER")

with col3:
    if st.button("🟣 TIE"):
        st.session_state.historico.append("TIE")

# ===== SINAL =====
sinal, forca = gerar_sinal(list(st.session_state.historico))

st.subheader("🔴 SINAL ATUAL")
st.markdown(sinal_html(sinal), unsafe_allow_html=True)
st.write(f"Força do sinal: **{forca}**")

# ===== HISTÓRICO =====
st.subheader("📊 Histórico recente")
df = pd.DataFrame(list(st.session_state.historico), columns=["Resultado"])
st.table(df[::-1])

# ===== RODAPÉ =====
st.caption("Modo Analista Externo • Decisão final é sempre tua")
