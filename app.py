import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# ================= CONFIG =================
st.set_page_config(
    page_title="OOREDOO Algérie - Prédiction Churn",
    page_icon="📱",
    layout="wide"
)

# ================= CSS =================
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #E30613, #C40511);
    color: white;
    text-align: center;
    padding: 2rem;
    border-radius: 15px;
}
.info-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}
.risk-high {border-left: 6px solid #f44336;}
.risk-medium {border-left: 6px solid #ff9800;}
.risk-low {border-left: 6px solid #4caf50;}
</style>
""", unsafe_allow_html=True)

# ================= FONCTION CHURN =================
def calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat):
    score = 30
    pos, neg = [], []

    if satisfaction <= 3:
        score += 40; neg.append("Satisfaction très faible")
    elif satisfaction <= 5:
        score += 20; neg.append("Satisfaction faible")
    elif satisfaction <= 7:
        score += 10
    else:
        score -= 20; pos.append("Bonne satisfaction")

    if appels >= 5:
        score += 25; neg.append("Appels support fréquents")
    elif appels >= 3:
        score += 15

    if retards >= 3:
        score += 30; neg.append("Retards répétés")
    elif retards >= 1:
        score += 15
    else:
        score -= 10; pos.append("Paiements réguliers")

    if anciennete < 6:
        score += 20
    elif anciennete >= 24:
        score -= 25; pos.append("Client fidèle")

    if contrat == "Mensuel":
        score += 15
    elif contrat == "2 ans":
        score -= 30; pos.append("Contrat long")

    if service == "Fibre":
        score -= 5; pos.append("Service fibre")

    if prix > 6000:
        score += 10; neg.append("Prix élevé")
    elif prix < 2000:
        score -= 5; pos.append("Prix compétitif")

    score = max(5, min(95, score))
    p = score / 100

    if p >= 0.7:
        niveau, cls = "🚨 TRÈS ÉLEVÉ", "risk-high"
    elif p >= 0.5:
        niveau, cls = "⚠️ ÉLEVÉ", "risk-medium"
    elif p >= 0.3:
        niveau, cls = "📊 MODÉRÉ", "risk-medium"
    else:
        niveau, cls = "✅ FAIBLE", "risk-low"

    return {
        "probabilite": p,
        "niveau": niveau,
        "classe": cls,
        "positifs": pos,
        "negatifs": neg
    }

# ================= HEADER =================
st.markdown("""
<div class="main-header">
<h1>📱 OOREDOO ALGÉRIE</h1>
<p>Prédiction intelligente du churn client</p>
</div>
""", unsafe_allow_html=True)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs([
    "📊 Client unique",
    "📁 Import fichier",
    "🧾 Liste de clients"
])

# ================= TAB 1 =================
with tab1:
    st.markdown("### 📊 Prédiction pour un client")

    # --- Cas réels ---
    cas_reels = {
        "Choisir un cas...": {},
        "Client fidèle et satisfait": {
            "satisfaction": 9,
            "age": 40,
            "anciennete": 36,
            "prix": 3000,
            "appels": 1,
            "retards": 0,
            "service": "Fibre",
            "contrat": "2 ans"
        },
        "Client mécontent avec retards": {
            "satisfaction": 3,
            "age": 25,
            "anciennete": 4,
            "prix": 5000,
            "appels": 6,
            "retards": 3,
            "service": "Mobile",
            "contrat": "Mensuel"
        },
        "Client moyen": {
            "satisfaction": 6,
            "age": 30,
            "anciennete": 12,
            "prix": 3500,
            "appels": 2,
            "retards": 1,
            "service": "4G+",
            "contrat": "1 an"
        }
    }

    selected_cas = st.selectbox("📌 Cas réels", list(cas_reels.keys()))

    # --- Colonnes ---
    col1, col2 = st.columns(2)
    with col1:
        satisfaction = st.slider("Satisfaction", 1, 10, 7, key="satisfaction")
        age = st.slider("Âge", 18, 80, 35, key="age")
        anciennete = st.slider("Ancienneté (mois)", 1, 120, 12, key="anciennete")
        prix = st.slider("Prix mensuel (DZD)", 500, 20000, 3500, 100, key="prix")
    with col2:
        appels = st.slider("Appels support / mois", 0, 30, 2, key="appels")
        retards = st.slider("Retards paiement", 0, 12, 0, key="retards")
        service = st.selectbox("Service", ["Mobile", "Fibre", "4G+", "Bundle"], index=0, key="service")
        contrat = st.selectbox("Contrat", ["Mensuel", "3 mois", "6 mois", "1 an", "2 ans"], index=0, key="contrat")

    # --- Remplissage automatique si un cas est choisi ---
    if selected_cas != "Choisir un cas...":
        cas = cas_reels[selected_cas]
        st.session_state['satisfaction'] = cas['satisfaction']
        st.session_state['age'] = cas['age']
        st.session_state['anciennete'] = cas['anciennete']
        st.session_state['prix'] = cas['prix']
        st.session_state['appels'] = cas['appels']
        st.session_state['retards'] = cas['retards']
        st.session_state['service'] = cas['service']
        st.session_state['contrat'] = cas['contrat']

        # Mettre à jour les sliders/selectbox avec session_state
        st.slider("Satisfaction", 1, 10, st.session_state['satisfaction'], key="satisfaction")
        st.slider("Âge", 18, 80, st.session_state['age'], key="age")
        st.slider("Ancienneté (mois)", 1, 120, st.session_state['anciennete'], key="anciennete")
        st.slider("Prix mensuel (DZD)", 500, 20000, st.session_state['prix'], 100, key="prix")
        st.slider("Appels support / mois", 0, 30, st.session_state['appels'], key="appels")
        st.slider("Retards paiement", 0, 12, st.session_state['retards'], key="retards")
        st.selectbox("Service", ["Mobile", "Fibre", "4G+", "Bundle"],
                     index=["Mobile", "Fibre", "4G+", "Bundle"].index(st.session_state['service']), key="service")
        st.selectbox("Contrat", ["Mensuel", "3 mois", "6 mois", "1 an", "2 ans"],
                     index=["Mensuel", "3 mois", "6 mois", "1 an", "2 ans"].index(st.session_state['contrat']), key="contrat")

    # --- Bouton calcul ---
    if st.button("🚀 Calculer"):
        r = calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat)
        st.markdown(f"""
        <div class="info-card {r['classe']}">
        <h2>{r['niveau']} – {int(r['probabilite']*100)}%</h2>
        <ul>
        {''.join([f'<li>✅ {p}</li>' for p in r['positifs']])}
        {''.join([f'<li>⚠️ {n}</li>' for n in r['negatifs']])}
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ================= TAB 2 =================
with tab2:
    st.markdown("### 📁 Prédiction par fichier")

    fichier = st.file_uploader("Importer CSV ou Excel", type=["csv", "xlsx"])

    if fichier:
        df = pd.read_csv(fichier) if fichier.name.endswith(".csv") else pd.read_excel(fichier)
        st.dataframe(df.head())

        if st.button("🚀 Lancer prédiction fichier"):
            results = []
            for _, row in df.iterrows():
                r = calculer_risque_churn(
                    row["satisfaction"], row["age"], row["anciennete"],
                    row["prix"], row["appels"], row["retards"],
                    row["service"], row["contrat"]
                )
                results.append({
                    "Churn_%": round(r["probabilite"]*100,1),
                    "Niveau": r["niveau"]
                })

            df_out = pd.concat([df, pd.DataFrame(results)], axis=1)
            st.dataframe(df_out)

            st.download_button(
                "⬇️ Télécharger",
                df_out.to_csv(index=False, encoding="utf-8-sig"),
                "prediction_churn.csv"
            )

# ================= TAB 3 =================
with tab3:
    st.markdown("### 🧾 Saisie d'une liste de clients")

    df_input = st.data_editor(
        pd.DataFrame({
            "satisfaction":[7],
            "age":[35],
            "anciennete":[12],
            "prix":[3500],
            "appels":[2],
            "retards":[0],
            "service":["Fibre"],
            "contrat":["1 an"]
        }),
        num_rows="dynamic"
    )

    if st.button("🚀 Calculer la liste"):
        results = []
        for _, row in df_input.iterrows():
            r = calculer_risque_churn(
                row["satisfaction"], row["age"], row["anciennete"],
                row["prix"], row["appels"], row["retards"],
                row["service"], row["contrat"]
            )
            results.append({
                "Churn_%": round(r["probabilite"]*100,1),
                "Niveau": r["niveau"]
            })

        df_out = pd.concat([df_input, pd.DataFrame(results)], axis=1)
        st.dataframe(df_out)

        st.download_button(
            "⬇️ Télécharger CSV",
            df_out.to_csv(index=False, encoding="utf-8-sig"),
            "liste_clients_churn.csv"
        )
