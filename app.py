import streamlit as st
import pandas as pd

# ================= CONFIG =================
st.set_page_config(page_title="MT Bac Bo", layout="wide")

# ================= ESTILO =================
st.markdown("""
<style>
.big {font-size:38px; font-weight:bold; text-align:center}
.player {color:#1f77ff}
.banker {color:#d62728}
.tie {color:#f1c40f}
.pause {color:#e67e22}
.box {padding:12px; border-radius:10px; background:#111}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
def init_state():
    st.session_state.historico = []
    st.session_state.total = 0
    st.session_state.empates = []
    st.session_state.modo = "DEMO"     # DEMO ou REAL
    st.session_state.perdas = 0
    st.session_state.pausa = False

if "historico" not in st.session_state:
    init_state()

# ================= FUNÇÕES =================
def forca_sinal(hist):
    if len(hist) < 5:
        return 0
    ultimos = hist[-5:]
    p = ultimos.count("PLAYER")
    b = ultimos.count("BANKER")
    return max(p, b) / len(ultimos) * 100

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

# ================= TÍTULO =================
st.title("🤖 MT — Analista Bac Bo")

# ================= POWER =================
st.markdown("## ⚡ Controlo Geral")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("⚡ POWER / RESET", key="power"):
        init_state()
        st.success("✅ MT reiniciado")

with c2:
    if st.button("🔁 Alternar DEMO / REAL"):
        st.session_state.modo = "REAL" if st.session_state.modo == "DEMO" else "DEMO"

with c3:
    st.markdown(f"**Modo atual:** `{st.session_state.modo}`")

st.divider()

# ================= INSERÇÃO =================
st.markdown("## 🎮 Inserir resultado da ronda")

b1, b2, b3 = st.columns(3)

with b1:
    if st.button("🔵 PLAYER"):
        st.session_state.historico.append("PLAYER")
        st.session_state.total += 1

with b2:
    if st.button("🔴 BANKER"):
        st.session_state.historico.append("BANKER")
        st.session_state.total += 1

with b3:
    if st.button("🟡 EMPATE"):
        st.session_state.historico.append("TIE")
        st.session_state.empates.append(st.session_state.total + 1)
        st.session_state.total += 1

# ================= SINAL =================
sinal, forca = gerar_sinal(st.session_state.historico)

st.divider()
st.markdown("## 📢 Sinal Atual")

if st.session_state.pausa:
    st.markdown("<div class='big pause'>⛔ PAUSA ATIVA</div>", unsafe_allow_html=True)

elif sinal == "PLAYER" and forca >= 60:
    st.markdown(f"<div class='big player'>ENTRAR PLAYER 🔵<br>Força {forca:.0f}% | {st.session_state.modo}</div>", unsafe_allow_html=True)

elif sinal == "BANKER" and forca >= 60:
    st.markdown(f"<div class='big banker'>ENTRAR BANKER 🔴<br>Força {forca:.0f}% | {st.session_state.modo}</div>", unsafe_allow_html=True)

elif sinal == "EMPATE":
    st.markdown("<div class='big tie'>EMPATE 🟡</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='big'>AGUARDAR ⏳</div>", unsafe_allow_html=True)

# ================= CONTROLO DE PERDA =================
st.divider()
st.markdown("## 🛑 Controlo de Perdas")

p1, p2 = st.columns(2)

with p1:
    if st.button("❌ Registrar PERDA"):
        st.session_state.perdas += 1
        if st.session_state.perdas >= 2:
            st.session_state.pausa = True

with p2:
    if st.button("✅ Registrar GANHO"):
        st.session_state.perdas = 0
        st.session_state.pausa = False

# ================= ESTATÍSTICAS =================
st.divider()
st.markdown("## 📊 Estatísticas")

e1, e2, e3 = st.columns(3)

with e1:
    st.metric("🎯 Rondas", st.session_state.total)

with e2:
    st.metric("🟡 Empates", len(st.session_state.empates))

with e3:
    st.metric("🧠 Força Atual", f"{forca:.0f}%")

# ================= HISTÓRICO =================
st.divider()
st.markdown("## 📜 Histórico")

if st.session_state.historico:
    df = pd.DataFrame({
        "Ronda": range(1, len(st.session_state.historico) + 1),
        "Resultado": st.session_state.historico
    })
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhuma ronda ainda.")
