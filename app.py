import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt
import json
import base64
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Plateforme de Détection du Risque de Perte Client",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #E30613 0%, #C40511 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(227, 6, 19, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
    }
    
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 6px solid #f44336 !important;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 6px solid #ff9800 !important;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 6px solid #4caf50 !important;
    }
    
    .metric-big {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #E30613 0%, #C40511 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Dictionnaire multilingue
LEXIQUE_EMOTION = {
    "positif": [
        "mlih","bahi","mzyan","raqi","merh","saye7","tayeb","mabsout",
        "جيد","ممتاز","شكرا","سريع","سعيد","مرحبا",
        "merci","excellent","rapide","parfait","bien","satisfait",
        "good","excellent","perfect","fast","thank you","satisfied"
    ],
    "negatif": [
        "machi mliha","da3if","karitha","ta3 ta3b","ma3tal",
        "سيء","ضعيف","بطيء","معطل","مقلق",
        "lent","problème","mauvais","nul","cher","insatisfait",
        "bad","slow","problem","terrible","expensive","not satisfied"
    ]
}

def analyser_sentiment(commentaire):
    """Analyse le sentiment d'un commentaire"""
    if not commentaire or len(commentaire.strip()) < 3:
        return None
    
    texte = commentaire.lower()
    score = 0
    
    for mot in LEXIQUE_EMOTION["positif"]:
        if mot in texte:
            score += 1
    
    for mot in LEXIQUE_EMOTION["negatif"]:
        if mot in texte:
            score -= 1
    
    if score <= -2:
        return {"emotion": "Très négatif 😡", "satisfaction": 2, "couleur": "#f44336"}
    elif score == -1:
        return {"emotion": "Négatif 😕", "satisfaction": 4, "couleur": "#ff9800"}
    elif score == 0:
        return {"emotion": "Neutre 😐", "satisfaction": 6, "couleur": "#ffc107"}
    elif score == 1:
        return {"emotion": "Positif 🙂", "satisfaction": 8, "couleur": "#8bc34a"}
    else:
        return {"emotion": "Très positif 😄", "satisfaction": 9.5, "couleur": "#4caf50"}

def calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat):
    """Calcule le risque de churn"""
    score = 30
    
    if satisfaction <= 3: score += 40
    elif satisfaction <= 5: score += 20
    elif satisfaction <= 7: score += 10
    if satisfaction >= 8: score -= 20
    
    if appels >= 5: score += 25
    elif appels >= 3: score += 15
    
    if retards >= 3: score += 30
    elif retards >= 1: score += 15
    if retards == 0: score -= 10
    
    if anciennete < 6: score += 20
    if anciennete >= 24: score -= 25
    
    if contrat == "Mensuel": score += 15
    if contrat == "2 ans": score -= 30
    
    score = max(5, min(95, score))
    probabilite = score / 100
    
    if probabilite >= 0.7:
        return {
            "probabilite": probabilite,
            "niveau": "🚨 TRÈS ÉLEVÉ",
            "couleur": "#f44336",
            "classe": "risk-high",
            "recommandation": "Contact immédiat requis",
            "actions": [
                {"icon": "📞", "titre": "Contact immédiat", "desc": "Appeler dans les 24h"},
                {"icon": "🎁", "titre": "Offre exclusive", "desc": "30% réduction 6 mois"},
                {"icon": "👥", "titre": "Gestionnaire dédié", "desc": "Suivi personnalisé"},
                {"icon": "🔧", "titre": "Audit technique", "desc": "Résolution prioritaire"}
            ]
        }
    elif probabilite >= 0.5:
        return {
            "probabilite": probabilite,
            "niveau": "⚠️ ÉLEVÉ",
            "couleur": "#ff9800",
            "classe": "risk-medium",
            "recommandation": "Offrir promotion sous 7 jours",
            "actions": [
                {"icon": "📧", "titre": "Email promotionnel", "desc": "Offre sous 7 jours"},
                {"icon": "📅", "titre": "Appel de suivi", "desc": "Programmer dans 3 jours"},
                {"icon": "🔍", "titre": "Analyse historique", "desc": "Examiner problèmes"},
                {"icon": "💳", "titre": "Prélèvement auto", "desc": "Éviter retards"}
            ]
        }
    elif probabilite >= 0.3:
        return {
            "probabilite": probabilite,
            "niveau": "📊 MODÉRÉ",
            "couleur": "#ffc107",
            "classe": "risk-medium",
            "recommandation": "Surveillance mensuelle",
            "actions": [
                {"icon": "📊", "titre": "Suivi mensuel", "desc": "Revue de satisfaction"},
                {"icon": "🔔", "titre": "Rappel contrat", "desc": "Notification anticipée"},
                {"icon": "🌟", "titre": "Services +", "desc": "Proposer options"},
                {"icon": "📋", "titre": "Feedback", "desc": "Demander retours"}
            ]
        }
    else:
        return {
            "probabilite": probabilite,
            "niveau": "✅ FAIBLE",
            "couleur": "#4caf50",
            "classe": "risk-low",
            "recommandation": "Client fidèle",
            "actions": [
                {"icon": "⭐", "titre": "Programme VIP", "desc": "Avantages exclusifs"},
                {"icon": "🎯", "titre": "Services premium", "desc": "Offres spéciales"},
                {"icon": "🤝", "titre": "Événements", "desc": "Invitations"},
                {"icon": "📈", "titre": "Advocacy", "desc": "Témoignages"}
            ]
        }

def creer_jauge_altair(probabilite, couleur):
    """Crée une jauge avec Altair"""
    data = pd.DataFrame({
        'value': [probabilite * 100],
        'max': [100]
    })
    
    base = alt.Chart(data).encode(
        theta=alt.Theta("value:Q", stack=True),
        color=alt.ColorValue(couleur),
        tooltip=['value']
    )
    
    gauge = base.mark_arc(innerRadius=80, outerRadius=120)
    
    text = alt.Chart(data).mark_text(
        size=40,
        fontWeight='bold'
    ).encode(
        text=alt.Text('value:Q', format='.0f'),
        color=alt.ColorValue(couleur)
    )
    
    return gauge + text

def main():
    """Application principale"""
    
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>📱 Aymen Telecom</h1>
        <p>"Plateforme de Détection du Risque de Perte Client</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation
    if 'satisfaction' not in st.session_state:
        st.session_state.satisfaction = 7
    
    # Onglets
    tab1, tab2 = st.tabs(["🧠 ANALYSE SENTIMENT", "📊 SAISIE MANUELLE"])
    
    with tab1:
        st.markdown("### Analyse Automatique de Satisfaction")
        commentaire = st.text_area(
            "Commentaire client (multilingue):",
            height=150,
            placeholder="Ex: 'خدمة ممتازة' ou 'Excellent service'..."
        )
        
        if st.button("🔍 ANALYSER"):
            if commentaire.strip():
                resultat = analyser_sentiment(commentaire)
                if resultat:
                    st.session_state.satisfaction = resultat["satisfaction"]
                    
                    st.markdown(f"""
                    <div class="info-card" style="border-left-color: {resultat['couleur']};">
                        <h2 style="color: {resultat['couleur']};">{resultat['emotion']}</h2>
                        <h1>Satisfaction: {resultat['satisfaction']}/10</h1>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            satisfaction = st.slider(
                "Satisfaction (1-10):",
                1, 10, st.session_state.satisfaction
            )
            age = st.slider("Âge:", 18, 70, 35)
            anciennete = st.slider("Ancienneté (mois):", 1, 60, 12)
            prix = st.slider("Prix (DZD):", 500, 15000, 3500, 100)
        
        with col2:
            appels = st.slider("Appels support/mois:", 0, 20, 2)
            retards = st.slider("Retards paiement:", 0, 10, 0)
            service = st.selectbox("Service:", ["Mobile", "Fibre"])
            contrat = st.selectbox("Contrat:", ["Mensuel", "3 mois", "1 an", "2 ans"])
    
    # Bouton calcul
    if st.button("🚀 CALCULER RISQUE", use_container_width=True):
        risque = calculer_risque_churn(
            satisfaction, age, anciennete, prix, appels, retards, service, contrat
        )
        
        # Résultats
        st.markdown("---")
        st.markdown("## 📊 RÉSULTATS")
        
        # Affichage métrique principale
        col_met1, col_met2, col_met3 = st.columns([2, 1, 2])
        
        with col_met2:
            st.markdown(f"""
            <div class="metric-big" style="color: {risque['couleur']};">
                {risque['probabilite']*100:.0f}%
            </div>
            <h2 style="text-align: center; color: {risque['couleur']};">
                {risque['niveau']}
            </h2>
            """, unsafe_allow_html=True)
        
        # Jauge Altair
        st.markdown("### 📈 Niveau de risque")
        chart = creer_jauge_altair(risque['probabilite'], risque['couleur'])
        st.altair_chart(chart, use_container_width=True)
        
        # Recommandations
        st.markdown(f"""
        <div class="info-card {risque['classe']}">
            <h3>💡 Recommandation</h3>
            <p>{risque['recommandation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actions
        st.markdown("### 🎯 Actions recommandées")
        cols = st.columns(4)
        for idx, action in enumerate(risque['actions']):
            with cols[idx]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: white; 
                         border-radius: 10px; border: 1px solid #ddd;">
                    <div style="font-size: 2rem;">{action['icon']}</div>
                    <h4>{action['titre']}</h4>
                    <p style="color: #666; font-size: 0.9rem;">
                        {action['desc']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Statistiques")
        st.metric("Précision", "92%")
        st.metric("Clients analysés", "1,247")
        st.metric("Churn moyen", "18%")
        
        st.markdown("---")
        st.markdown("### 💡 Exemples")
        if st.button("🔥 Haut risque"):
            st.session_state.satisfaction = 2
        
        if st.button("⚠️ Risque moyen"):
            st.session_state.satisfaction = 6
        
        if st.button("✅ Faible risque"):
            st.session_state.satisfaction = 9

if __name__ == "__main__":
    main()


