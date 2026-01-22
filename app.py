import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Aymen Telecom - Risk Platform",
    page_icon="📱",
    layout="wide"
)

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #E30613 0%, #C40511 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    .risk-high { border-left: 6px solid #f44336 !important; background-color: #fff5f5; }
    .risk-medium { border-left: 6px solid #ff9800 !important; background-color: #fff9f0; }
    .risk-low { border-left: 6px solid #4caf50 !important; background-color: #f5fff5; }
    .metric-big { font-size: 3.5rem; font-weight: 900; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE MÉTIER ---
LEXIQUE_EMOTION = {
    "positif": ["mlih","bahi","mzyan","raqi","merci","excellent","good","جيد","ممتاز"],
    "negatif": ["machi mliha","da3if","karitha","lent","problème","bad","سيء","ضعيف"]
}

def analyser_sentiment(commentaire):
    if not commentaire or len(commentaire.strip()) < 3: return None
    texte = commentaire.lower()
    score = sum([1 for mot in LEXIQUE_EMOTION["positif"] if mot in texte])
    score -= sum([1 for mot in LEXIQUE_EMOTION["negatif"] if mot in texte])
    
    if score <= -1: return {"emotion": "Négatif 😕", "satisfaction": 3, "couleur": "#f44336"}
    if score == 0: return {"emotion": "Neutre 😐", "satisfaction": 5, "couleur": "#ffc107"}
    return {"emotion": "Positif 🙂", "satisfaction": 9, "couleur": "#4caf50"}

def calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat):
    score = 30
    if satisfaction <= 3: score += 40
    elif satisfaction <= 6: score += 20
    if appels >= 4: score += 20
    if retards >= 2: score += 25
    if contrat == "Mensuel": score += 15
    if anciennete < 6: score += 10
    
    score = max(5, min(95, score))
    prob = score / 100
    
    if prob >= 0.7:
        return {"probabilite": prob, "niveau": "🚨 TRÈS ÉLEVÉ", "couleur": "#f44336", "classe": "risk-high", "recommandation": "Contact immédiat requis"}
    elif prob >= 0.4:
        return {"probabilite": prob, "niveau": "⚠️ ÉLEVÉ", "couleur": "#ff9800", "classe": "risk-medium", "recommandation": "Offre promotionnelle à envoyer"}
    else:
        return {"probabilite": prob, "niveau": "✅ FAIBLE", "couleur": "#4caf50", "classe": "risk-low", "recommandation": "Client fidèle à fidéliser"}

# --- INTERFACE PRINCIPALE ---
st.markdown('<div class="main-header"><h1>📱 Aymen Telecom</h1><p>Analyse Prédictive du Churn Client</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🧠 ANALYSE SENTIMENT", "📊 SAISIE MANUELLE", "📁 IMPORT CSV"])

# ONGLETS 1 & 2 (Adaptés de votre code)
with tab1:
    commentaire = st.text_area("Commentaire client :", placeholder="Ex: 'Service très lent et cher'...")
    if st.button("🔍 ANALYSER SENTIMENT"):
        res = analyser_sentiment(commentaire)
        if res:
            st.session_state.satisfaction = res["satisfaction"]
            st.metric("Satisfaction estimée", f"{res['satisfaction']}/10", res['emotion'])

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        sat = st.slider("Satisfaction :", 1, 10, st.session_state.get('satisfaction', 7))
        age = st.slider("Âge :", 18, 80, 30)
        anc = st.slider("Ancienneté (mois) :", 1, 72, 12)
    with col2:
        app = st.slider("Appels Support :", 0, 15, 1)
        ret = st.slider("Retards Paiement :", 0, 10, 0)
        con = st.selectbox("Contrat :", ["Mensuel", "1 an", "2 ans"])
    
    if st.button("🚀 CALCULER RISQUE INDIVIDUEL"):
        r = calculer_risque_churn(sat, age, anc, 3000, app, ret, "Mobile", con)
        st.markdown(f'<div class="info-card {r["classe"]}"><h2 style="color:{r["couleur"]}">{r["niveau"]} ({int(r["probabilite"]*100)}%)</h2><p>{r["recommandation"]}</p></div>', unsafe_allow_html=True)

# NOUVEL ONGLET : IMPORT CSV
with tab3:
    st.subheader("Analyse de Masse")
    
    # Bouton pour télécharger un template
    template_df = pd.DataFrame(columns=["nom", "satisfaction", "age", "anciennete", "prix", "appels", "retards", "service", "contrat"])
    template_df.loc[0] = ["Ahmed", 4, 35, 12, 2500, 5, 2, "Fibre", "Mensuel"]
    csv_template = template_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger le modèle CSV", csv_template, "modele_telecom.csv", "text/csv")
    
    uploaded_file = st.file_uploader("Charger votre fichier client (CSV)", type="csv")
    
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        st.write("Aperçu des données chargées :", df_input.head(3))
        
        if st.button("⚡ ANALYSER TOUT LE FICHIER"):
            try:
                # Calcul batch
                results = df_input.apply(lambda row: calculer_risque_churn(
                    row['satisfaction'], row['age'], row['anciennete'], 
                    row['prix'], row['appels'], row['retards'], 
                    row['service'], row['contrat']
                ), axis=1)
                
                df_input['Risque %'] = [round(r['probabilite'] * 100) for r in results]
                df_input['Statut'] = [r['niveau'] for r in results]
                
                # Affichage des statistiques globales
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Clients", len(df_input))
                c2.metric("Risque Moyen", f"{int(df_input['Risque %'].mean())}%")
                c3.metric("Alertes Critiques", len(df_input[df_input['Risque %'] > 70]))
                
                # Graphique de répartition
                chart = alt.Chart(df_input).mark_bar().encode(
                    x=alt.X('Risque %', bin=alt.Bin(maxbins=10)),
                    y='count()',
                    color=alt.condition(alt.datum['Risque %'] > 70, alt.value('#f44336'), alt.value('#4caf50'))
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
                
                st.dataframe(df_input)
                
                # Téléchargement du résultat
                res_csv = df_input.to_csv(index=False).encode('utf-8')
                st.download_button("💾 Télécharger les résultats", res_csv, "resultats_risque.csv", "text/csv")
                
            except Exception as e:
                st.error(f"Erreur formatage : Vérifiez que les noms de colonnes correspondent au modèle. Erreur: {e}")

# SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/891/891012.png", width=100)
    st.info("Cette plateforme utilise des règles métier pour prédire le désabonnement client.")
