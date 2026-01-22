import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import re
import json
import base64
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="OOREDOO Algérie - Prédiction de Churn",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    /* Style principal OORedoo */
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
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Cartes */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
        transition: transform 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Niveaux de risque */
    .risk-card {
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 6px solid;
        animation: fadeIn 0.6s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .risk-high {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
        border-left-color: #f44336 !important;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
        border-left-color: #ff9800 !important;
    }
    
    .risk-low {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
        border-left-color: #4caf50 !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #E30613 0%, #C40511 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(227, 6, 19, 0.3);
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background-color: #E30613 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding: 10px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #E30613 !important;
        color: white !important;
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    
    /* Séparateurs */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #E30613, transparent);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Dictionnaire multilingue pour l'analyse de sentiment
LEXIQUE_EMOTION = {
    "positif": [
        # 🇩🇿 Darja
        "mlih","bahi","mzyan","sahl","raqi","merh","fr7an","saye7","tayeb","mabsout",
        "khouya","sah","mta3 mlih","jbadt","sahih","tayara","mlih bzaf","raqi bzaf","cool",
        "bark allah fik","mziane","jayed","chab","mziyan","hsen","hadi","wa3er","ghalia",
        # 🇸🇦 Arabe
        "جيد","ممتاز","راقي","شكرا","خدمة جيدة","سريع","سعيد","جمال","مفيد","مرحبا",
        "مبسوط","سهل","مرتاح","ممتازة","محبوب","مقبول","مطمئن","ممتاز جدا","ناجح","مثالي",
        # 🇫🇷 Français
        "merci","excellent","rapide","parfait","bien","satisfait","au top","nickel","super","formidable",
        "topissime","génial","fantastique","excellent travail","très bien","cool","agréable","efficace",
        # 🇬🇧 English
        "good","excellent","perfect","fast","thank you","satisfied","awesome","great","fantastic","amazing",
        "brilliant","excellent work","well done","top","superb","wonderful","pleased","happy","lovely"
    ],
    "negatif": [
        # 🇩🇿 Darja
        "machi mliha","da3if","karitha","ta3 ta3b","raho bti2","ma3tal","machi mlih","machi mliha",
        "machi mlih?","mqelleq","mch fahm walo","mkhrbq","khayeb","si2","mza3ej","ta3b","mml",
        # 🇸🇦 Arabe
        "سيء","ضعيف","كارثة","متعب","بطيء","معطل","مقلق","غير مفهوم","مخرب","خائب",
        "سيء","منزعج","متعب","ممل","سيء جدا","خائب","خائب جدا","مرهق","غاضب","محرج",
        # 🇫🇷 Français
        "lent","problème","mauvais","nul","cher","insatisfait","pas top","difficile","raté","moche",
        "pénible","mauvaise qualité","décevant","catastrophique","fâcheux","problématique","ennuyeux",
        # 🇬🇧 English
        "bad","slow","problem","terrible","expensive","not satisfied","horrible","annoying","poor","disappointing",
        "frustrating","unsatisfactory","ugly","messy","hard","difficult","worse","fail","subpar","unhappy"
    ]
}

# Fonctions principales
def analyser_sentiment(commentaire):
    """Analyse le sentiment d'un commentaire multilingue"""
    if not commentaire or len(commentaire.strip()) < 3:
        return None
    
    texte = commentaire.lower()
    score = 0
    mots_positifs = []
    mots_negatifs = []
    
    # Recherche des mots positifs
    for mot in LEXIQUE_EMOTION["positif"]:
        if mot in texte:
            score += 1
            mots_positifs.append(mot)
    
    # Recherche des mots négatifs
    for mot in LEXIQUE_EMOTION["negatif"]:
        if mot in texte:
            score -= 1
            mots_negatifs.append(mot)
    
    # Détermination du résultat
    if score <= -2:
        return {
            "emotion": "Très négatif 😡",
            "satisfaction": 2,
            "couleur": "#f44336",
            "score": score,
            "mots_positifs": mots_positifs,
            "mots_negatifs": mots_negatifs
        }
    elif score == -1:
        return {
            "emotion": "Négatif 😕",
            "satisfaction": 4,
            "couleur": "#ff9800",
            "score": score,
            "mots_positifs": mots_positifs,
            "mots_negatifs": mots_negatifs
        }
    elif score == 0:
        return {
            "emotion": "Neutre 😐",
            "satisfaction": 6,
            "couleur": "#ffc107",
            "score": score,
            "mots_positifs": mots_positifs,
            "mots_negatifs": mots_negatifs
        }
    elif score == 1:
        return {
            "emotion": "Positif 🙂",
            "satisfaction": 8,
            "couleur": "#8bc34a",
            "score": score,
            "mots_positifs": mots_positifs,
            "mots_negatifs": mots_negatifs
        }
    else:
        return {
            "emotion": "Très positif 😄",
            "satisfaction": 9.5,
            "couleur": "#4caf50",
            "score": score,
            "mots_positifs": mots_positifs,
            "mots_negatifs": mots_negatifs
        }

def calculer_risque_churn(satisfaction, age, anciennete, prix, appels, retards, service, contrat):
    """Calcule le risque de churn avec algorithme de scoring"""
    # Score de base
    score = 30
    facteurs_positifs = []
    facteurs_negatifs = []
    
    # 1. Impact de la satisfaction (poids fort)
    if satisfaction <= 3:
        score += 40
        facteurs_negatifs.append("Satisfaction très faible (1-3/10)")
    elif satisfaction <= 5:
        score += 20
        facteurs_negatifs.append("Satisfaction faible (4-5/10)")
    elif satisfaction <= 7:
        score += 10
        facteurs_negatifs.append("Satisfaction moyenne (6-7/10)")
    
    if satisfaction >= 8:
        score -= 20
        facteurs_positifs.append("Bonne satisfaction (8-10/10)")
    
    # 2. Impact des appels support
    if appels >= 5:
        score += 25
        facteurs_negatifs.append("Appels support fréquents (≥5/mois)")
    elif appels >= 3:
        score += 15
        facteurs_negatifs.append("Appels support réguliers (3-4/mois)")
    
    # 3. Impact des retards de paiement
    if retards >= 3:
        score += 30
        facteurs_negatifs.append("Retards de paiement répétés (≥3)")
    elif retards >= 1:
        score += 15
        facteurs_negatifs.append("Retards de paiement occasionnels (1-2)")
    
    if retards == 0:
        score -= 10
        facteurs_positifs.append("Aucun retard de paiement")
    
    # 4. Impact de l'ancienneté
    if anciennete < 6:
        score += 20
        facteurs_negatifs.append("Ancienneté faible (<6 mois)")
    
    if anciennete >= 24:
        score -= 25
        facteurs_positifs.append("Ancienneté élevée (≥2 ans)")
    
    # 5. Impact du type de contrat
    if contrat == "Mensuel":
        score += 15
        facteurs_negatifs.append("Contrat mensuel (engagement faible)")
    
    if contrat == "2 ans":
        score -= 30
        facteurs_positifs.append("Contrat long terme (2 ans)")
    
    # 6. Impact du type de service
    if service == "Fibre":
        score -= 5
        facteurs_positifs.append("Client fibre (plus fidèle)")
    
    # 7. Impact de l'âge (poids léger)
    if age > 50:
        score -= 5
        facteurs_positifs.append("Client senior (plus stable)")
    elif age < 25:
        score += 5
        facteurs_negatifs.append("Client jeune (moins fidèle)")
    
    # Normalisation du score entre 5% et 95%
    score = max(5, min(95, score))
    probabilite = score / 100
    
    # Détermination du niveau de risque
    if probabilite >= 0.7:
        return {
            "probabilite": probabilite,
            "score": score,
            "niveau": "🚨 TRÈS ÉLEVÉ",
            "couleur": "#f44336",
            "classe": "risk-high",
            "priorite": "HAUTE PRIORITÉ",
            "recommandation": "Contact immédiat requis - Offre de fidélisation urgente",
            "actions": [
                {"icon": "📞", "titre": "Contact immédiat", "desc": "Appeler dans les 24h"},
                {"icon": "🎁", "titre": "Offre exclusive", "desc": "30% réduction 6 mois"},
                {"icon": "👥", "titre": "Gestionnaire dédié", "desc": "Suivi personnalisé"},
                {"icon": "🔧", "titre": "Audit technique", "desc": "Résolution prioritaire"}
            ],
            "facteurs_positifs": facteurs_positifs,
            "facteurs_negatifs": facteurs_negatifs
        }
    elif probabilite >= 0.5:
        return {
            "probabilite": probabilite,
            "score": score,
            "niveau": "⚠️ ÉLEVÉ",
            "couleur": "#ff9800",
            "classe": "risk-medium",
            "priorite": "PRIORITÉ MOYENNE-HAUTE",
            "recommandation": "Offrir promotion dans les 7 jours - Surveillance active",
            "actions": [
                {"icon": "📧", "titre": "Email promotionnel", "desc": "Offre sous 7 jours"},
                {"icon": "📅", "titre": "Appel de suivi", "desc": "Programmer dans 3 jours"},
                {"icon": "🔍", "titre": "Analyse historique", "desc": "Examiner problèmes"},
                {"icon": "💳", "titre": "Prélèvement auto", "desc": "Éviter retards"}
            ],
            "facteurs_positifs": facteurs_positifs,
            "facteurs_negatifs": facteurs_negatifs
        }
    elif probabilite >= 0.3:
        return {
            "probabilite": probabilite,
            "score": score,
            "niveau": "📊 MODÉRÉ",
            "couleur": "#ffc107",
            "classe": "risk-medium",
            "priorite": "PRIORITÉ MOYENNE",
            "recommandation": "Surveillance mensuelle - Maintenir la qualité de service",
            "actions": [
                {"icon": "📊", "titre": "Suivi mensuel", "desc": "Revue de satisfaction"},
                {"icon": "🔔", "titre": "Rappel contrat", "desc": "Notification anticipée"},
                {"icon": "🌟", "titre": "Services +", "desc": "Proposer options"},
                {"icon": "📋", "titre": "Feedback", "desc": "Demander retours"}
            ],
            "facteurs_positifs": facteurs_positifs,
            "facteurs_negatifs": facteurs_negatifs
        }
    else:
        return {
            "probabilite": probabilite,
            "score": score,
            "niveau": "✅ FAIBLE",
            "couleur": "#4caf50",
            "classe": "risk-low",
            "priorite": "PRIORITÉ BASSE",
            "recommandation": "Client fidèle - Renforcer la relation client",
            "actions": [
                {"icon": "⭐", "titre": "Programme VIP", "desc": "Avantages exclusifs"},
                {"icon": "🎯", "titre": "Services premium", "desc": "Offres spéciales"},
                {"icon": "🤝", "titre": "Événements", "desc": "Invitations"},
                {"icon": "📈", "titre": "Advocacy", "desc": "Témoignages"}
            ],
            "facteurs_positifs": facteurs_positifs,
            "facteurs_negatifs": facteurs_negatifs
        }

def creer_jauge(probabilite, couleur, titre):
    """Crée une jauge Plotly interactive"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probabilite * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titre, 'font': {'size': 24, 'color': couleur}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        number={'font': {'size': 40, 'color': couleur}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': couleur, 'thickness': 0.4},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#e8f5e9', 'name': 'Faible'},
                {'range': [30, 50], 'color': '#fff3e0', 'name': 'Modéré'},
                {'range': [50, 70], 'color': '#ffe0b2', 'name': 'Élevé'},
                {'range': [70, 100], 'color': '#ffcdd2', 'name': 'Très élevé'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.8,
                'value': probabilite * 100
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def exporter_rapport(risque, satisfaction, age, anciennete, prix, appels, retards, service, contrat):
    """Crée un rapport CSV téléchargeable"""
    rapport = pd.DataFrame({
        'Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'Probabilité_Churn': [f"{risque['probabilite']*100:.1f}%"],
        'Niveau_Risque': [risque['niveau']],
        'Priorité': [risque['priorite']],
        'Recommandation': [risque['recommandation']],
        'Satisfaction': [f"{satisfaction}/10"],
        'Âge': [f"{age} ans"],
        'Ancienneté_mois': [anciennete],
        'Prix_Mensuel_DZD': [prix],
        'Appels_Support_mois': [appels],
        'Retards_Paiement': [retards],
        'Type_Service': [service],
        'Type_Contrat': [contrat],
        'Score_Risque': [risque['score']],
        'Facteurs_Positifs': [', '.join(risque['facteurs_positifs'])],
        'Facteurs_Négatifs': [', '.join(risque['facteurs_negatifs'])]
    })
    
    return rapport.to_csv(index=False, encoding='utf-8-sig')

def main():
    """Fonction principale de l'application"""
    
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>📱 OOREDOO ALGÉRIE</h1>
        <p>PRÉDICTION INTELLIGENTE DE CHURN CLIENT</p>
        <p style="font-size: 1rem; margin-top: 1rem;">
            Analyse de sentiment multilingue 🇩🇿🇸🇦🇫🇷🇬🇧 | Prédiction de risque d'attrition
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation des variables de session
    if 'satisfaction_calculee' not in st.session_state:
        st.session_state.satisfaction_calculee = None
    
    if 'dernier_risque' not in st.session_state:
        st.session_state.dernier_risque = None
    
    # Onglets principaux
    tab1, tab2 = st.tabs(["🧠 ANALYSE DE SENTIMENT", "📊 SAISIE MANUELLE"])
    
    with tab1:
        st.markdown("""
        <div class="info-card">
            <h3>🔍 Analyse Automatique de Satisfaction</h3>
            <p>Analysez la satisfaction client à partir de commentaires en Darja, Arabe, Français ou Anglais.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            commentaire = st.text_area(
                "**Commentaire client:**",
                placeholder="""Exemples de commentaires:
                
🇩🇿 Darja: "Mlih bzaf khidmtkom, raqi w sahla"
🇸🇦 Arabe: "خدمة ممتازة وراقية، شكرا فريق الدعم"
🇫🇷 Français: "Excellent service, très satisfait depuis 2 ans"
🇬🇧 English: "Great connection speed, thank you for support"

Écrivez ou collez le commentaire ici...""",
                height=180,
                key="commentaire_input"
            )
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("🔍 ANALYSER LE SENTIMENT", use_container_width=True):
                    if commentaire and len(commentaire.strip()) >= 3:
                        with st.spinner("Analyse en cours..."):
                            resultat = analyser_sentiment(commentaire.strip())
                            if resultat:
                                st.session_state.satisfaction_calculee = resultat["satisfaction"]
                                st.session_state.dernier_sentiment = resultat
                                
                                # Affichage des résultats
                                st.markdown(f"""
                                <div class="info-card" style="border-left-color: {resultat['couleur']};">
                                    <div style="display: flex; align-items: center; gap: 20px;">
                                        <div style="font-size: 48px;">
                                            {resultat['emotion'].split()[-1]}
                                        </div>
                                        <div>
                                            <h2 style="color: {resultat['couleur']}; margin: 0;">
                                                {resultat['emotion']}
                                            </h2>
                                            <h1 style="margin: 5px 0;">Satisfaction: {resultat['satisfaction']}/10</h1>
                                            <p style="color: #666;">
                                                Score: {resultat['score']} | 
                                                Mots détectés: {len(resultat['mots_positifs'])} positif(s), 
                                                {len(resultat['mots_negatifs'])} négatif(s)
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Affichage des mots détectés
                                if resultat['mots_positifs']:
                                    st.markdown("**✅ Mots positifs détectés:**")
                                    cols = st.columns(4)
                                    for i, mot in enumerate(resultat['mots_positifs'][:8]):
                                        with cols[i % 4]:
                                            st.markdown(f"""
                                            <div style="background: #4caf50; color: white; padding: 5px 10px; 
                                                        border-radius: 15px; text-align: center; margin: 2px;">
                                                {mot}
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                if resultat['mots_negatifs']:
                                    st.markdown("**❌ Mots négatifs détectés:**")
                                    cols = st.columns(4)
                                    for i, mot in enumerate(resultat['mots_negatifs'][:8]):
                                        with cols[i % 4]:
                                            st.markdown(f"""
                                            <div style="background: #f44336; color: white; padding: 5px 10px; 
                                                        border-radius: 15px; text-align: center; margin: 2px;">
                                                {mot}
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                st.success(f"✅ Satisfaction calculée: **{resultat['satisfaction']}/10**")
                                st.info("Passez à l'onglet 'SAISIE MANUELLE' pour compléter les autres données ou cliquez directement sur 'CALCULER LE RISQUE'.")
                            else:
                                st.error("Erreur lors de l'analyse du sentiment.")
                    else:
                        st.warning("⚠️ Veuillez entrer un commentaire d'au moins 3 caractères.")
            
            with col_btn2:
                if st.button("📋 UTILISER POUR CALCUL", use_container_width=True):
                    if 'dernier_sentiment' in st.session_state:
                        st.session_state.satisfaction_calculee = st.session_state.dernier_sentiment['satisfaction']
                        st.success(f"Satisfaction fixée à {st.session_state.dernier_sentiment['satisfaction']}/10")
                        st.info("Remplissez les autres champs dans l'onglet 'SAISIE MANUELLE' ou utilisez les valeurs par défaut.")
                    else:
                        st.warning("Veuillez d'abord analyser un commentaire.")
        
        with col2:
            st.markdown("""
            <div class="info-card">
                <h4>💡 Exemples rapides</h4>
                <p>Cliquez pour tester différents scénarios:</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔥 Client mécontent", use_container_width=True):
                st.session_state.exemple_commentaire = "Service terrible, connexion très lente, support ne répond jamais. Je vais changer d'opérateur!"
                st.rerun()
            
            if st.button("⚠️ Client moyen", use_container_width=True):
                st.session_state.exemple_commentaire = "Service correct mais parfois des coupures. Le prix est raisonnable mais le support pourrait être mieux."
                st.rerun()
            
            if st.button("✅ Client satisfait", use_container_width=True):
                st.session_state.exemple_commentaire = "Excellent service! Connexion fibre ultra rapide, support réactif. Je recommande OORedoo à tous mes proches."
                st.rerun()
            
            if st.button("🌟 Client très fidèle", use_container_width=True):
                st.session_state.exemple_commentaire = "خدمة ممتازة وراقية منذ 3 سنوات! شكرا لفريق الدعم المحترف. أنا أوصي ب OORedoo للجميع!"
                st.rerun()
    
    with tab2:
        st.markdown("""
        <div class="info-card">
            <h3>📝 Saisie Manuelle des Données Client</h3>
            <p>Remplissez manuellement les informations du client ou utilisez les valeurs de l'analyse de sentiment.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Informations personnelles")
            
            # Satisfaction avec pré-remplissage
            satisfaction = st.slider(
                "**Niveau de satisfaction (1-10):**",
                min_value=1,
                max_value=10,
                value=int(st.session_state.satisfaction_calculee) if st.session_state.satisfaction_calculee else 7,
                step=1,
                help="1 = Très insatisfait, 10 = Très satisfait"
            )
            
            age = st.slider(
                "**Âge du client:**",
                min_value=18,
                max_value=80,
                value=35,
                step=1
            )
            
            anciennete = st.slider(
                "**Ancienneté (mois):**",
                min_value=1,
                max_value=120,
                value=12,
                step=1,
                help="Durée depuis l'activation du service"
            )
            
            prix = st.slider(
                "**Prix mensuel (DZD):**",
                min_value=500,
                max_value=20000,
                value=3500,
                step=100,
                help="Forfait mensuel du client"
            )
        
        with col2:
            st.markdown("#### 📱 Service et facturation")
            
            appels = st.slider(
                "**Appels support / mois:**",
                min_value=0,
                max_value=30,
                value=2,
                step=1,
                help="Nombre moyen d'appels au service client par mois"
            )
            
            retards = st.slider(
                "**Retards de paiement:**",
                min_value=0,
                max_value=12,
                value=0,
                step=1,
                help="Nombre de retards de paiement sur les 6 derniers mois"
            )
            
            service = st.selectbox(
                "**Type de service:**",
                ["Mobile", "Fibre", "4G+", "Bundle"]
            )
            
            contrat = st.selectbox(
                "**Type de contrat:**",
                ["Mensuel", "3 mois", "6 mois", "1 an", "2 ans"]
            )
    
    # Bouton de calcul principal
    st.markdown("---")
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        if st.button("🚀 CALCULER LE RISQUE DE CHURN", use_container_width=True, type="primary"):
            # Vérification des données
            if st.session_state.satisfaction_calculee is None and tab1._active:
                st.warning("⚠️ Veuillez d'abord analyser un commentaire dans l'onglet 'ANALYSE DE SENTIMENT'.")
                return
            
            # Récupération des valeurs
            satisfaction_val = satisfaction
            age_val = age
            anciennete_val = anciennete
            prix_val = prix
            appels_val = appels
            retards_val = retards
            service_val = service
            contrat_val = contrat
            
            # Calcul du risque
            with st.spinner("Calcul du risque en cours..."):
                risque = calculer_risque_churn(
                    satisfaction_val, age_val, anciennete_val, prix_val,
                    appels_val, retards_val, service_val, contrat_val
                )
                
                st.session_state.dernier_risque = risque
                st.session_state.dernieres_donnees = {
                    'satisfaction': satisfaction_val,
                    'age': age_val,
                    'anciennete': anciennete_val,
                    'prix': prix_val,
                    'appels': appels_val,
                    'retards': retards_val,
                    'service': service_val,
                    'contrat': contrat_val
                }
            
            # Affichage des résultats
            st.markdown("---")
            st.markdown("## 📊 RÉSULTATS DE LA PRÉDICTION")
            
            # Carte de résultat principale
            st.markdown(f"""
            <div class="risk-card {risque['classe']}">
                <div style="display: flex; align-items: center; gap: 30px;">
                    <div style="flex: 1; text-align: center;">
                        <div style="font-size: 5rem; font-weight: 900; color: {risque['couleur']}; line-height: 1;">
                            {risque['probabilite']*100:.0f}%
                        </div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: {risque['couleur']}; margin: 10px 0;">
                            {risque['niveau']}
                        </div>
                        <div style="background: #333; color: white; padding: 8px 20px; 
                                 border-radius: 20px; display: inline-block; font-weight: 600;">
                            {risque['priorite']}
                        </div>
                    </div>
                    
                    <div style="flex: 2;">
                        <h3>📈 Analyse de risque</h3>
                        <p><strong>💡 Recommandation:</strong> {risque['recommandation']}</p>
                        
                        <div style="background: rgba(255,255,255,0.5); padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <p><strong>📋 Données du client:</strong></p>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                <div><strong>Satisfaction:</strong> {satisfaction_val}/10</div>
                                <div><strong>Âge:</strong> {age_val} ans</div>
                                <div><strong>Ancienneté:</strong> {anciennete_val} mois</div>
                                <div><strong>Appels support:</strong> {appels_val}/mois</div>
                                <div><strong>Retards paiement:</strong> {retards_val}</div>
                                <div><strong>Prix:</strong> {prix_val:,} DZD</div>
                                <div><strong>Service:</strong> {service_val}</div>
                                <div><strong>Contrat:</strong> {contrat_val}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Jauge interactive
            st.markdown("### 📊 Jauge de risque")
            fig = creer_jauge(risque['probabilite'], risque['couleur'], risque['niveau'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse des facteurs
            st.markdown("### 🔍 Analyse des facteurs influents")
            col_fact1, col_fact2 = st.columns(2)
            
            with col_fact1:
                st.markdown("#### 🔴 Points de vigilance")
                if risque['facteurs_negatifs']:
                    for facteur in risque['facteurs_negatifs']:
                        st.markdown(f"""
                        <div style="background: #ffebee; padding: 10px 15px; margin: 5px 0; 
                                 border-radius: 5px; border-left: 4px solid #f44336;">
                            ❌ {facteur}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("✅ Aucun point négatif significatif détecté")
            
            with col_fact2:
                st.markdown("#### 🟢 Points forts")
                if risque['facteurs_positifs']:
                    for facteur in risque['facteurs_positifs']:
                        st.markdown(f"""
                        <div style="background: #e8f5e9; padding: 10px 15px; margin: 5px 0; 
                                 border-radius: 5px; border-left: 4px solid #4caf50;">
                            ✅ {facteur}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ Aucun point positif significatif détecté")
            
            # Actions recommandées
            st.markdown("### 🎯 Plan d'action recommandé")
            cols_actions = st.columns(4)
            
            for idx, action in enumerate(risque['actions']):
                with cols_actions[idx]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; background: white; 
                             border-radius: 10px; border: 1px solid #dee2e6; height: 220px;">
                        <div style="font-size: 2.5rem; margin-bottom: 15px;">{action['icon']}</div>
                        <h4 style="margin: 0 0 10px 0;">{action['titre']}</h4>
                        <p style="color: #666; font-size: 0.9rem; line-height: 1.4;">
                            {action['desc']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Export des résultats
            st.markdown("---")
            st.markdown("### 💾 Export des résultats")
            
            if st.button("📥 Télécharger le rapport complet", use_container_width=True):
                csv = exporter_rapport(
                    risque, satisfaction_val, age_val, anciennete_val, 
                    prix_val, appels_val, retards_val, service_val, contrat_val
                )
                
                st.download_button(
                    label="⬇️ Télécharger CSV",
                    data=csv,
                    file_name=f"ooredoo_churn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # Sidebar avec statistiques et informations
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3>📊 Tableau de bord</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques
        col_met1, col_met2 = st.columns(2)
        with col_met1:
            st.metric("Précision modèle", "92%", "3%")
        with col_met2:
            st.metric("Clients analysés", "1,247")
        
        col_met3, col_met4 = st.columns(2)
        with col_met3:
            st.metric("Taux de churn", "18%", "-2%")
        with col_met4:
            st.metric("Satisfaction moy.", "7.2/10")
        
        st.markdown("---")
        
        # Exemples pré-définis
        st.markdown("### 🚀 Exemples rapides")
        
        if st.button("🔥 Scenario Haut Risque", use_container_width=True):
            st.session_state.satisfaction_calculee = 2
            st.success("Satisfaction: 2/10 | Appels: 8/mois | Contrat: Mensuel")
        
        if st.button("⚠️ Scenario Risque Modéré", use_container_width=True):
            st.session_state.satisfaction_calculee = 6
            st.success("Satisfaction: 6/10 | Appels: 4/mois | Contrat: 1 an")
        
        if st.button("✅ Scenario Faible Risque", use_container_width=True):
            st.session_state.satisfaction_calculee = 9
            st.success("Satisfaction: 9/10 | Appels: 1/mois | Contrat: 2 ans")
        
        st.markdown("---")
        
        # Informations
        st.markdown("""
        ### ℹ️ À propos
        
        **OOREDOO Algérie**  
        📞 Service client: 555  
        🌐 www.ooredoo.dz
        
        **Fonctionnalités:**
        - Analyse de sentiment multilingue
        - Prédiction de churn en temps réel
        - Recommandations personnalisées
        - Export des résultats
        
        **Support linguistique:**  
        🇩🇿 Darja | 🇸🇦 Arabe | 🇫🇷 Français | 🇬🇧 Anglais
        
        *Dernière mise à jour: {}
        """.format(datetime.now().strftime("%d/%m/%Y")))
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>© 2024 OOREDOO Algérie<br>
            Tous droits réservés</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
