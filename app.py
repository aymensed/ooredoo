import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="OOREDOO Algérie - Prédiction de Churn",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LEXIQUE POUR ANALYSE DE SENTIMENT ---
LEXIQUE_EMOTION = {
    "positif": ["mlih","bahi","mzyan","sahl","raqi","merh","fr7an","saye7","tayeb","mabsout",
                "merci","excellent","parfait","good","awesome","fantastic","super"],
    "negatif": ["machi mliha","da3if","karitha","ta3 ta3b","raho bti2","ma3tal",
                "mauvais","lent","bad","problem","terrible","horrible"]
}

# --- FONCTIONS ---
def analyser_sentiment(commentaire):
    if not commentaire or len(commentaire.strip()) < 3:
        return None
    texte = commentaire.lower()
    score = 0
    mots_positifs, mots_negatifs = [], []

    for mot in LEXIQUE_EMOTION["positif"]:
        if mot in texte:
            score += 1
            mots_positifs.append(mot)
    for mot in LEXIQUE_EMOTION["negatif"]:
        if mot in texte:
            score -= 1
            mots_negatifs.append(mot)
    
    if score <= -2:
        emotion, satisfaction, couleur = "Très négatif 😡", 2, "#f44336"
    elif score == -1:
        emotion, satisfaction, couleur = "Négatif 😕", 4, "#ff9800"
    elif score == 0:
        emotion, satisfaction, couleur = "Neutre 😐", 6, "#ffc107"
    elif score == 1:
        emotion, satisfaction, couleur = "Positif 🙂", 8, "#8bc34a"
    else:
        emotion, satisfaction, couleur = "Très positif 😄", 9.5, "#4caf50"
    
    return {
        "emotion": emotion,
        "satisfaction": satisfaction,
        "couleur": couleur,
        "score": score,
        "mots_positifs": mots_positifs,
        "mots_negatifs": mots_negatifs
    }

def calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat):
    score = 30
    facteurs_positifs, facteurs_negatifs = [], []

    # Satisfaction
    if satisfaction <= 3: score += 40; facteurs_negatifs.append("Satisfaction très faible")
    elif satisfaction <= 5: score += 20; facteurs_negatifs.append("Satisfaction faible")
    elif satisfaction <= 7: score += 10; facteurs_negatifs.append("Satisfaction moyenne")
    if satisfaction >= 8: score -= 20; facteurs_positifs.append("Bonne satisfaction")
    
    # Appels support
    if appels >= 5: score += 25; facteurs_negatifs.append("Appels support fréquents")
    elif appels >= 3: score += 15; facteurs_negatifs.append("Appels support réguliers")
    
    # Retards paiement
    if retards >= 3: score += 30; facteurs_negatifs.append("Retards de paiement répétés")
    elif retards >= 1: score += 15; facteurs_negatifs.append("Retards de paiement occasionnels")
    if retards == 0: score -= 10; facteurs_positifs.append("Aucun retard de paiement")
    
    # Ancienneté
    if anciennete < 6: score += 20; facteurs_negatifs.append("Ancienneté faible")
    if anciennete >= 24: score -= 25; facteurs_positifs.append("Ancienneté élevée")
    
    # Contrat
    if contrat == "Mensuel": score += 15; facteurs_negatifs.append("Contrat mensuel")
    if contrat == "2 ans": score -= 30; facteurs_positifs.append("Contrat long terme")
    
    # Service
    if service == "Fibre": score -= 5; facteurs_positifs.append("Client fibre")
    
    # Âge
    if age > 50: score -= 5; facteurs_positifs.append("Client senior")
    elif age < 25: score += 5; facteurs_negatifs.append("Client jeune")
    
    score = max(5, min(95, score))
    probabilite = score / 100

    # Détermination niveau de risque
    if probabilite >= 0.7: niveau, couleur, classe, priorite, reco = "🚨 TRÈS ÉLEVÉ","#f44336","risk-high","HAUTE PRIORITÉ","Contact immédiat requis"
    elif probabilite >= 0.5: niveau, couleur, classe, priorite, reco = "⚠️ ÉLEVÉ","#ff9800","risk-medium","PRIORITÉ MOYENNE-HAUTE","Offrir promotion sous 7 jours"
    elif probabilite >= 0.3: niveau, couleur, classe, priorite, reco = "📊 MODÉRÉ","#ffc107","risk-medium","PRIORITÉ MOYENNE","Surveillance mensuelle"
    else: niveau, couleur, classe, priorite, reco = "✅ FAIBLE","#4caf50","risk-low","PRIORITÉ BASSE","Client fidèle"

    return {
        "probabilite": probabilite,
        "score": score,
        "niveau": niveau,
        "couleur": couleur,
        "classe": classe,
        "priorite": priorite,
        "recommandation": reco,
        "facteurs_positifs": facteurs_positifs,
        "facteurs_negatifs": facteurs_negatifs
    }

def creer_jauge(probabilite, couleur, titre):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probabilite*100,
        domain={'x':[0,1],'y':[0,1]},
        title={'text': titre, 'font': {'color': couleur, 'size':24}},
        gauge={
            'axis': {'range':[0,100]},
            'bar': {'color': couleur, 'thickness':0.4},
            'steps':[{'range':[0,30],'color':'#e8f5e9'},
                     {'range':[30,50],'color':'#fff3e0'},
                     {'range':[50,70],'color':'#ffe0b2'},
                     {'range':[70,100],'color':'#ffcdd2'}],
            'threshold': {'line':{'color':'black','width':4}, 'thickness':0.8, 'value':probabilite*100}
        }
    ))
    fig.update_layout(height=350, margin=dict(t=20,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- MAIN ---
def main():
    st.title("📱 OOREDOO Algérie - Prédiction Churn")
    
    # Onglets
    tab1, tab2 = st.tabs(["🧠 Analyse de Sentiment", "📊 Saisie Manuelle"])
    
    with tab1:
        commentaire = st.text_area("Commentaire client:", height=150)
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("🔥 Client mécontent"): commentaire="Service terrible, très lent!"
        if col2.button("⚠️ Client moyen"): commentaire="Service correct, quelques coupures"
        if col3.button("✅ Client satisfait"): commentaire="Excellent service, très satisfait"
        if col4.button("🌟 Client fidèle"): commentaire="خدمة ممتازة وراقية منذ 3 سنوات!"
        
        if st.button("🔍 Analyser le sentiment"):
            resultat = analyser_sentiment(commentaire)
            if resultat:
                st.success(f"Satisfaction calculée: {resultat['satisfaction']}/10 | {resultat['emotion']}")
                st.session_state.satisfaction_calculee = resultat['satisfaction']
    
    with tab2:
        satisfaction = st.slider("Satisfaction", 1, 10, int(st.session_state.satisfaction_calculee) if 'satisfaction_calculee' in st.session_state else 7)
        age = st.slider("Âge",18,80,35)
        anciennete = st.slider("Ancienneté (mois)",1,120,12)
        prix = st.slider("Prix mensuel (DZD)",500,20000,3500)
        appels = st.slider("Appels support/mois",0,30,2)
        retards = st.slider("Retards paiement",0,12,0)
        service = st.selectbox("Type de service", ["Mobile","Fibre","4G+","Bundle"])
        contrat = st.selectbox("Type de contrat", ["Mensuel","3 mois","6 mois","1 an","2 ans"])
        
        if st.button("🚀 Calculer le risque de churn"):
            risque = calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat)
            st.metric("Probabilité de churn", f"{risque['probabilite']*100:.0f}%")
            st.markdown(f"**Niveau:** {risque['niveau']} | **Priorité:** {risque['priorite']}")
            st.plotly_chart(creer_jauge(risque['probabilite'], risque['couleur'], risque['niveau']))
            
            st.subheader("🔍 Points de vigilance")
            for f in risque['facteurs_negatifs']: st.write(f"❌ {f}")
            st.subheader("🟢 Points forts")
            for f in risque['facteurs_positifs']: st.write(f"✅ {f}")

if __name__=="__main__":
    main()
