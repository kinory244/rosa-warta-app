import streamlit as st
import pandas as pd
import os

# === Costanti ===
CSV_LISTONE_PATH = os.path.abspath("listone_fvm.csv")
CSV_ROSA_PATH = os.path.abspath("rosa_warta.csv")

COLORI_RUOLI = {
    "P": "#d0e1f9",
    "D": "#d0f9d9",
    "C": "#f9f1d0",
    "A": "#f9d0d0"
}

# === Config iniziale ===
st.set_page_config(page_title="Gestione Rosa Warta EN A", layout="wide")
st.title("⚽ Gestione Rosa Warta EN A")

# === Funzioni utili ===
def carica_rosa():
    if os.path.exists(CSV_ROSA_PATH):
        df = pd.read_csv(CSV_ROSA_PATH)
        if "FVMp Prevista" not in df.columns:
            df["FVMp Prevista"] = ""
        return df
    else:
        return pd.DataFrame(columns=["#", "Ruolo", "Nome", "Prezzo", "Squadra", "Anni Contratto", "FVMp", "FVMp Prevista"])

def carica_listone():
    if os.path.exists(CSV_LISTONE_PATH):
        return pd.read_csv(CSV_LISTONE_PATH)
    else:
        st.warning("⚠️ File listone_fvm.csv non trovato.")
        return pd.DataFrame(columns=["R", "RM", "Nome", "Squadra", "FVM"])

def aggiorna_fvmp(rosa_df, listone_df):
    updated = rosa_df.copy()
    for idx, row in updated.iterrows():
        nome = str(row["Nome"]).strip().lower()
        match = listone_df[listone_df['Nome'].str.strip().str.lower() == nome]
        if not match.empty:
            updated.at[idx, "FVMp"] = match.iloc[0]["FVM"]
    return updated

def applica_incremento(rosa_df, percentuale):
    updated = rosa_df.copy()
    updated["FVMp Prevista"] = pd.to_numeric(updated["FVMp"], errors="coerce") * (1 + percentuale / 100)
    updated["FVMp Prevista"] = updated["FVMp Prevista"].round(2)
    return updated

def calcola_stipendi(df, colonna_fvmp):
    tot = 0
    dettagli = []
    for _, row in df.iterrows():
        try:
            nome = row["Nome"]
            val = pd.to_numeric(row[colonna_fvmp], errors="coerce")
            if pd.notna(val):
                tot += val
                dettagli.append(f"{nome}: {val:.2f} Mln")
        except:
            continue
    return dettagli, tot, tot * 0.10

def salva_rosa(df):
    df.to_csv(CSV_ROSA_PATH, index=False)

def evidenzia_ruoli(row):
    ruolo = row["Ruolo"]
    colore = COLORI_RUOLI.get(ruolo, "white")
    return [f"background-color: {colore}" for _ in row]

# === Inizializza stato ===
if "rosa" not in st.session_state:
    st.session_state["rosa"] = carica_rosa()

listone_df = carica_listone()

# === Sidebar: Filtri ===
st.sidebar.header("🔍 Filtri Rosa")

ruolo_filtro = st.sidebar.multiselect("Filtra per Ruolo", options=st.session_state["rosa"]["Ruolo"].unique(), default=st.session_state["rosa"]["Ruolo"].unique())
squadra_filtro = st.sidebar.multiselect("Filtra per Squadra", options=st.session_state["rosa"]["Squadra"].unique(), default=st.session_state["rosa"]["Squadra"].unique())
nome_search = st.sidebar.text_input("Cerca per Nome")

filtrata_df = st.session_state["rosa"][
    (st.session_state["rosa"]["Ruolo"].isin(ruolo_filtro)) &
    (st.session_state["rosa"]["Squadra"].isin(squadra_filtro)) &
    (st.session_state["rosa"]["Nome"].str.contains(nome_search, case=False, na=False))
]

# === Tabella filtrata con colori ===
st.subheader("📋 Rosa (Filtrata)")
st.dataframe(filtrata_df.style.apply(evidenzia_ruoli, axis=1), use_container_width=True)

# === Editor Rosa ===
st.subheader("✏️ Modifica Rosa")
edited_df = st.data_editor(
    st.session_state["rosa"],
    use_container_width=True,
    num_rows="dynamic",
    column_config={"#": st.column_config.NumberColumn(disabled=True)},
    hide_index=True,
    key="editor"
)

# === Pulsanti Azione ===
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Aggiorna FVMp"):
        st.session_state["rosa"] = aggiorna_fvmp(edited_df, listone_df)
        st.success("FVMp aggiornato!")

with col2:
    variazione = st.selectbox("Simula FVMp Prevista (+/- %)", [-15, -10, -5, 5, 10, 15], index=4)
    if st.button("📈 Applica Simulazione"):
        st.session_state["rosa"] = applica_incremento(edited_df, variazione)
        st.success(f"Simulazione {variazione}% applicata!")

with col3:
    if st.button("💾 Salva Modifiche"):
        salva_rosa(edited_df)
        st.success("Rosa salvata!")

# === Calcolo Stipendi ===
st.subheader("💰 Stipendi")
col4, col5 = st.columns(2)

with col4:
    st.markdown("**FVMp (Settembre)**")
    dettagli, totale, stipendi = calcola_stipendi(edited_df, "FVMp")
    st.text("\n".join(dettagli))
    st.markdown(f"**Totale FVMp:** {totale:.2f} Mln  \n**Stipendi 10%:** {stipendi:.2f} Mln")

with col5:
    st.markdown("**FVMp Prevista**")
    dettagli, totale, stipendi = calcola_stipendi(edited_df, "FVMp Prevista")
    st.text("\n".join(dettagli))
    st.markdown(f"**Totale Previsto:** {totale:.2f} Mln  \n**Stipendi 10%:** {stipendi:.2f} Mln")
