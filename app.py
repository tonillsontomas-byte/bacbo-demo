import streamlit as st
import pandas as pd
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
.alerta {background-color: #ffff99; font-weight: bold; font-size:32px; text-align:center; padding:10px; border-radius:10px; animation: blink 1s infinite;}
.forca-forte {background-color:#00cc00; color:white; font-weight:bold; padding:5px; border-radius:5px;}
.forca-medio {background-color:#ffcc00; color:white; font-weight:bold; padding:5px; border-radius:5px;}
.forca-fraco {background-color:#999999; color:white; font-weight:bold; padding:5px; border-radius:5px;}
@keyframes blink { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# ===== ESTADO =====
if "historico" not in st.session_state:
    st.session_state.historico = []
if "acertos" not in st.session_state:
    st.session_state.acertos = 0
if "total_rondas" not in st.session_state:
    st.session_state.total_rondas = 0
if "empates" not in st.session_state:
    st.session_state.empates = []
if "alerta_tocado" not in st.session_state:
    st.session_state.alerta_tocado = False

# ===== FUNÇÕES =====
def gerar_sinal(hist):
    if len(hist) < 3:
        return "AGUARDAR", "FRACO"
    if hist[-3:].count("PLAYER") == 3:
        return "PLAYER", "FORTE"
    if hist[-3:].count("BANKER") == 3:
        return "BANKER", "FORTE"
    if hist[-2:].count("TIE") == 2:
        return "TIE", "FORTE"
    return "AGUARDAR", "FRACO"

def sinal_html(sinal):
    if sinal == "PLAYER":
        return '<div class="player">🔵 PLAYER</div>'
    if sinal == "BANKER":
        return '<div class="banker">🔴 BANKER</div>'
    if sinal == "TIE":
        return '<div class="tie">🟣 TIE</div>'
    return '<div class="wait">⚪ AGUARDAR</div>'

def forca_html(forca):
    if forca == "FORTE":
        return f'<span class="forca-forte">{forca}</span>'
    if forca == "MÉDIO":
        return f'<span class="forca-medio">{forca}</span>'
    return f'<span class="forca-fraco">{forca}</span>'

def atualizar_acertos(sinal, ultimo_resultado):
    if sinal in ["PLAYER","BANKER","TIE"] and ultimo_resultado == sinal:
        st.session_state.acertos += 1
    st.session_state.total_rondas += 1

def tocar_alerta():
    st.components.v1.html("""
    <audio autoplay>
      <source src="https://www.soundjay.com/button/beep-07.wav" type="audio/wav">
    </audio>
    <script>
      let count = 0;
      let audio = document.querySelector('audio');
      audio.volume = 1.0;
      audio.play();
      audio.onended = function() {
        count++;
        if(count < 3) audio.play();
      }
    </script>
    """, height=0, width=0)

# ===== TÍTULO =====
st.title("🎲 MT — Painel Profissional Bac Bo")

# ===== BOTÕES DE INSERÇÃO =====
st.subheader("📥 Inserir resultado da ronda")
col1, col2, col3 = st.columns(3)

if col1.button("🔵 PLAYER"):
    st.session_state.historico.append("PLAYER")
    atualizar_acertos("PLAYER","PLAYER")
    st.session_state.alerta_tocado = False

if col2.button("🔴 BANKER"):
    st.session_state.historico.append("BANKER")
    atualizar_acertos("BANKER","BANKER")
    st.session_state.alerta_tocado = False

if col3.button("🟣 TIE"):
    st.session_state.historico.append("TIE")
    atualizar_acertos("TIE","TIE")
    st.session_state.empates.append(len(st.session_state.historico))
    st.session_state.alerta_tocado = False

# ===== BOTÃO POWER / RESET =====
if st.button("⚡ POWER / RESET"):
    st.session_state.historico = []
    st.session_state.acertos = 0
    st.session_state.total_rondas = 0
    st.session_state.empates = []
    st.session_state.alerta_tocado = False

# ===== MINI-PAINEL =====
sinal, forca = gerar_sinal(st.session_state.historico)
st.markdown(f"<div style='font-size:60px; text-align:center;'>{sinal_html(sinal)}</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; font-size:32px;'>{forca_html(forca)}</div>", unsafe_allow_html=True)

if forca in ["FORTE","MÉDIO"] and not st.session_state.alerta_tocado:
    st.markdown(f'<div class="alerta">🔔 ALERTA: ENTAR {sinal}!</div>', unsafe_allow_html=True)
    tocar_alerta()
    st.session_state.alerta_tocado = True

st.markdown("🟣 **Empates recentes:**")
st.write(st.session_state.empates[::-1] if st.session_state.empates else "Nenhum empate")

# ===== ESTATÍSTICAS =====
taxa = (st.session_state.acertos / st.session_state.total_rondas * 100) if st.session_state.total_rondas>0 else 0
st.markdown(f"<div style='text-align:center; font-size:20px;'>Total de rondas: {st.session_state.total_rondas} | Acertos: {st.session_state.acertos} | Taxa: {taxa:.2f}%</div>", unsafe_allow_html=True)

# ===== HISTÓRICO E GRÁFICO =====
st.subheader("📊 Histórico e Streaks")
if st.session_state.historico:
    df = pd.DataFrame({"Resultado": st.session_state.historico, "Index": range(1, len(st.session_state.historico)+1)})
    # Gerar sinais em loop seguro
    sinais = []
    for i in range(len(st.session_state.historico)):
        slice_hist = st.session_state.historico[:i+1]
        sinal_temp,_ = gerar_sinal(slice_hist)
        sinais.append(sinal_temp)
    df['Sinal'] = sinais
    st.table(df[::-1])
    
    color_scale = alt.Scale(domain=["PLAYER","BANKER","TIE"], range=["#1f77ff","#ff2b2b","#9b59b6"])
    chart = alt.Chart(df).mark_circle(size=100).encode(
        x='Index',
        y=alt.value(0),
        color=alt.Color('Resultado', scale=color_scale),
        tooltip=['Index','Resultado']
    ).properties(height=50)
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("Nenhum resultado inserido ainda.")
