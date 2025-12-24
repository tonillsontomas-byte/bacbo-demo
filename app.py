
   else:
        return "TIE"

def gerar_sinal(hist):
    if hist.count("BANKER") >= 3:
        return "PLAYER", "MÉDIO"
    if hist.count("PLAYER") >= 3:
        return "BANKER", "MÉDIO"
    if hist.count("TIE") >= 2:
        return "TIE", "FORTE"
    return "AGUARDAR", "FRACO"

st.title("🤖 Bac Bo IA — DEMO ONLINE")

col1, col2 = st.columns([2,1])

with col1:
    if st.button("▶️ Nova Jogada"):
        resultado = simular_resultado()
        st.session_state.historico.append(resultado)

    sinal, forca = gerar_sinal(list(st.session_state.historico))

    st.subheader("🔴 SINAL ATUAL")
    st.markdown(f"## **{sinal}**")
    st.write(f"Força do sinal: **{forca}**")

    st.subheader("🧠 Leitura da IA")
    if sinal == "AGUARDAR":
        st.info("Sem vantagem clara. Aguardar nova oportunidade.")
    else:
        st.success(f"Padrão detectado. Possível entrada em **{sinal}**.")

with col2:
    st.subheader("📊 Histórico")
    df = pd.DataFrame(
        list(st.session_state.historico),
        columns=["Resultado"]
    )ad
    st.table(df[::-1])

    st.subheader("📈 Probabilidades (estimas)")
    total = max(len(st.session_state.historico), 1)
    st.write("PLAYER:", round(df["Resultado"].tolist().count("PLAYER")/total*100,1), "%")
    st.write("BANKER:", round(df["Resultado"].tolist().count("BANKER")/total*100,1), "%")
    st.write("TIE:", round(df["Resultado"].tolist().count("TIE")/total*100,1), "%")

st.caption("Modo DEMO • Preparado para ligação ao cassino real")
 
