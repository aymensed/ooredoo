import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# ================= CONFIG =================
st.set_page_config(
    page_title="Aymen Telecom",
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
<h1>📱 Aymen Telecom</h1>
<p>Plateforme de Détection du Risque de Perte Client</p>
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

    col1, col2 = st.columns(2)
    with col1:
        satisfaction = st.slider("Satisfaction", 1, 10, 7)
        age = st.slider("Âge", 18, 80, 35)
        anciennete = st.slider("Ancienneté (mois)", 1, 120, 12)
        prix = st.slider("Prix mensuel (DZD)", 500, 20000, 3500, 100)

    with col2:
        appels = st.slider("Appels support / mois", 0, 30, 2)
        retards = st.slider("Retards paiement", 0, 12, 0)
        service = st.selectbox("Service", ["Mobile", "Fibre", "4G+", "Bundle"])
        contrat = st.selectbox("Contrat", ["Mensuel", "3 mois", "6 mois", "1 an", "2 ans"])

    if st.button("🚀 Calculer"):
        r = calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat)
        st.markdown(f"""
        <div class="info-card {r['classe']}">
        <h2>{r['niveau']} – {int(r['probabilite']*100)}%</h2>
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

