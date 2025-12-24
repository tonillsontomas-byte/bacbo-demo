import streamlit as st
import pandas as pd
from collections import deque
import altair as alt

st.set_page_config(page_title="MT — Analista Bac Bo", layout="wide")

# ===== ESTILO =====
st.markdown("""
<style>
.player { color: #1f77ff; font-weight: bold; font-size: 50px; text-align:center;}
.banker { color: #ff2b2b; font-weight: bold; font-size: 50px; text-align:center;}
.tie { color: #9b59b6; font-weight: bold; font-size: 50px; text-align:center;}
.wait { color: #aaaaaa; font-weight: bold; font-size: 50px; text-align:center;}
button.stButton > button {height: 80px; width: 100%; font-size: 24px;}
.alerta {background-color: #ffff99; font-weight: bold; font-size:28px; text-align:center; padding:10px; border-radius:10px; animation: blink 1s infinite;}
.table-cell {font-size: 20px;}
@keyframes blink { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# ===== ESTADO =====
if "historico" not in st.session_state:
    st.session_state.historico = deque(maxlen=100)
if "acertos" not in st.session_state:
    st.session_state.acertos = 0
if "total_rondas" not in st.session_state:
    st.session_state.total_rondas = 0
if "empates" not in st.session_state:
    st.session_state.empates = []

# ===== FUNÇÕES =====
def gerar_sinal(hist):
    if len(hist) < 5:
        return "AGUARDAR", "FRACO"
    # Sinais fortes por sequência
    if hist[-3:].count("PLAYER") == 3:
        return "PLAYER", "FORTE"
    if hist[-3:].count("BANKER") == 3:
        return "BANKER", "FORTE"
    if hist[-2:].count("TIE") == 2:
        return "TIE", "FORTE"
    # Sinais médios por contagem
    if hist.count("PLAYER") >= 3:
        return "PLAYER", "MÉDIO"
    if hist.count("BANKER") >= 3:
        return "BANKER", "MÉDIO"
    if hist.count("TIE") >= 2:
        return "TIE", "MÉDIO"
    return "AGUARDAR", "FRACO"

def sinal_html(sinal):
    if sinal == "PLAYER":
        return '<div class="player">🔵 PLAYER</div>'
    if sinal == "BANKER":
        return '<div class="banker">🔴 BANKER</div>'
    if sinal == "TIE":
        return '<div class="tie">🟣 TIE</div>'
    return '<div class="wait">⚪ AGUARDAR</div>'

def atualizar_acertos(sinal, ultimo_resultado):
    if sinal in ["PLAYER","BANKER","TIE"] and ultimo_resultado == sinal:
        st.session_state.acertos += 1
    st.session_state.total_rondas += 1

# ===== TÍTULO =====
st.title("🎲 MT — Bot Analista Externo Bac Bo")

# ===== BOTÕES =====
st.subheader("📥 Inserir resultado da ronda")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔵 PLAYER"):
        st.session_state.historico.append("PLAYER")
        atualizar_acertos("PLAYER", "PLAYER")

with col2:
    if st.button("🔴 BANKER"):
        st.session_state.historico.append("BANKER")
        atualizar_acertos("BANKER", "BANKER")

with col3:
    if st.button("🟣 TIE"):
        st.session_state.historico.append("TIE")
        atualizar_acertos("TIE", "TIE")
        st.session_state.empates.append(len(st.session_state.historico))

# ===== SINAL ATUAL =====
sinal, forca = gerar_sinal(list(st.session_state.historico))
st.subheader("🔔 SINAL ATUAL")
st.markdown(sinal_html(sinal), unsafe_allow_html=True)

# ===== ALERTA =====
if forca in ["MÉDIO","FORTE"] and sinal != "AGUARDAR":
    st.markdown(f'<div class="alerta">🔔 ALERTA: ENTAR {sinal}!</div>', unsafe_allow_html=True)

# ===== HISTÓRICO E TABELA RÁPIDA =====
st.subheader("📊 Histórico e Sinais (Tabela rápida)")
df = pd.DataFrame(list(st.session_state.historico), columns=["Resultado"])
df['Index'] = range(1, len(df)+1)
df['Sinal'] = [gerar_sinal(list(st.session_state.historico[:i]))[0] for i in range(1, len(df)+1)]
df['Força'] = [gerar_sinal(list(st.session_state.historico[:i]))[1] for i in range(1, len(df)+1)]
st.table(df[::-1])

# ===== LISTA DE EMPATES =====
st.subheader("🟣 Lista de Empates (posição)")
if st.session_state.empates:
    st.write(st.session_state.empates[::-1])
else:
    st.write("Nenhum empate até agora")

# ===== ESTATÍSTICAS =====
st.subheader("📈 Estatísticas")
if st.session_state.total_rondas > 0:
    taxa = (st.session_state.acertos / st.session_state.total_rondas) * 100
else:
    taxa = 0
st.write(f"Total de rondas: **{st.session_state.total_rondas}**")
st.write(f"Acertos: **{st.session_state.acertos}**")
st.write(f"Taxa de acerto: **{taxa:.2f}%**")

# ===== GRÁFICO DE STREAKS =====
st.subheader("📊 Gráfico de Sequência (Streaks)")
if len(st.session_state.historico) > 0:
    df_chart = pd.DataFrame(list(st.session_state.historico), columns=["Resultado"])
    df_chart['Index'] = range(1, len(df_chart)+1)
    color_scale = alt.Scale(domain=["PLAYER","BANKER","TIE"], range=["#1f77ff","#ff2b2b","#9b59b6"])
    chart = alt.Chart(df_chart).mark_circle(size=100).encode(
        x='Index',
        y=alt.value(0),
        color=alt.Color('Resultado', scale=color_scale),
        tooltip=['Index','Resultado']
    ).properties(height=50)
    st.altair_chart(chart, use_container_width=True)

# ===== RODAPÉ =====
st.caption("Modo Analista Externo MT • Decisão final é sempre tua")
