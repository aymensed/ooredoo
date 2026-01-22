import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

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
    .main-header {
        color: #E30613;
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #E30613;
        margin-bottom: 30px;
    }
    
    .card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #E30613;
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
    
    .metric-card {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: #f8f9fa;
        margin: 10px;
    }
    
    .stSlider > div > div > div {
        color: #E30613 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #E30613 0%, #C40511 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(227, 6, 19, 0.3);
    }
    
    .tab-content {
        padding: 20px;
        border: 1px solid #dee2e6;
        border-radius: 0 0 8px 8px;
        margin-top: -1px;
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
        "fay9","zmane","raqi w mlih","ferhan bzaf","sahl w mlih","rayi7","sah bzaf","khir",
        "mrahba","sah w mzyan","mlih w sahl","raqi w sahih","tayara bzaf","tawfik","mzayen",
        "tbarkellah","mlih w fr7an","jayed bzaf","tayeb bzaf","hsen bzaf","mabsout bzaf",
        # 🇸🇦 Arabe
        "جيد","ممتاز","راقي","شكرا","خدمة جيدة","سريع","سعيد","جمال","مفيد","مرحبا",
        "مبسوط","سهل","مرتاح","ممتازة","محبوب","مقبول","مطمئن","ممتاز جدا","ناجح","مثالي",
        "فعال","جودة","ممتع","سهل","موثوق","إيجابي","مبسوط جدا","مميز","سهل ومرتاح","خدمة ممتازة",
        "مرتاح جدا","راقي جدا","سعيد","سريع جدا","جمال جدا","مذهل","راقي وممتاز","فرحة كبيرة","سعيد جدا",
        "مطمئن جدا","محترم","محبوب جدا","راقي جدا","ناجح جدا","مثالي جدا","فعال جدا","جودة ممتازة","خدمة ممتازة جدا",
        # 🇫🇷 Français
        "merci","excellent","rapide","parfait","bien","satisfait","au top","nickel","super","formidable",
        "topissime","génial","fantastique","excellent travail","très bien","cool","agréable","efficace",
        "propre","magnifique","superbe","remarquable","impeccable","sensationnel","extraordinaire",
        "fabuleux","splendide","convivial","chouette","heureux","content","satisfaisant","parfaitement bien",
        "excellent service","top qualité","hyper bien","très satisfait","formidablement","nickel chrome",
        "excellentissime","parfaitissime","très cool","fantastique service","génialissime","bien joué","super extra","au top qualité","exceptionnel","magnifique travail",
        # 🇬🇧 English
        "good","excellent","perfect","fast","thank you","satisfied","awesome","great","fantastic","amazing",
        "brilliant","excellent work","well done","top","superb","wonderful","pleased","happy","lovely",
        "efficient","smooth","impressive","marvelous","outstanding","remarkable","flawless","ideal",
        "pleasant","delightful","perfectly","amazing work","excellent service","high quality","very good",
        "super excellent","top notch","incredible","exceptional","best","very pleased","highly satisfied",
        "excellent experience","awesome job","perfect service","fantastic job","great service","well executed","splendid"
    ],
    "negatif": [
        # 🇩🇿 Darja
        "machi mliha","da3if","karitha","ta3 ta3b","raho bti2","ma3tal","machi mlih", "machi mliha", "machi mlih?","mqelleq","mch fahm walo","mkhrbq","khayeb",
        "si2","mza3ej","ta3b","mml","si2 bzaf","mkhib","khayeb bzaf","mrheq","3wis","mhrj",
        "mch monasib","9asi","khta2","ghir wadah","khidma si2a","mza3ej bzaf","mt3b","s3b","la y3jbni","m7bit",
        "ghir kafi","mta2kher","mchkla","mt3b bzaf","khayeb khidma","ma ysl7ch","karthi","si2 khidma","da3if bzaf","ghir maqboul",
        "radi2","mch wadah","mza3ejni","ghir mrdi","khta2 kbir","bti2 bzaf","fashal","khidma si2a jiddan","mkhib lil a3mal","mch mrdi",
        # 🇸🇦 Arabe
        "سيء","ضعيف","كارثة","متعب","بطيء","معطل","مقلق","غير مفهوم","مخرب","خائب",
        "سيء","منزعج","متعب","ممل","سيء جدا","خائب","خائب جدا","مرهق","غاضب","محرج",
        "غير مناسب","قاسي","خطأ","غير واضح","خدمة سيئة","منزعج جدا","متعب","صعب","لا يعجبني","محبط",
        "غير كافي","متأخر","مشكلة","متعب جدا","خدمة سيئة","غير صالح","كارثي","خدمة سيئة","ضعيف جدا","غير مقبول",
        "رديء","غير واضح","منزعج","غير مرضي","خطأ كبير","بطيء جدا","فشل","خدمة سيئة جدا","خائب للعمل","غير مرضي",
        # 🇫🇷 Français
        "lent","problème","mauvais","nul","cher","insatisfait","pas top","difficile","raté","moche",
        "pénible","mauvaise qualité","décevant","catastrophique","fâcheux","problématique","ennuyeux","inacceptable",
        "pas bien","médiocre","triste","lamentable","horrible","désagréable","problème majeur","inefficace","chaotique",
        "raté complet","hors service","faible","non satisfaisant","mauvais service","pas correct","mécontent","très mauvais",
        "problème énorme","terrible","à revoir","insuffisant","difficile à utiliser","déplorable","pénible à gérer","raté service",
        "insatisfaisant","faible performance","problème frustrant","service médiocre","pas top du tout","à améliorer",
        # 🇬🇧 English
        "bad","slow","problem","terrible","expensive","not satisfied","horrible","annoying","poor","disappointing",
        "frustrating","unsatisfactory","ugly","messy","hard","difficult","worse","fail","subpar","unhappy",
        "unpleasant","poor quality","inadequate","faulty","lousy","terrible service","not good","problematic","confusing",
        "slow service","disaster","weak","broken","incompetent","inefficient","unacceptable","flawed","unsuccessful",
        "troublesome","complicated","miserable","frustrated","bad experience","not recommended","problematic service",
        "annoyed","worst","displeased","hopeless","substandard"
    ]
}

# Fonction d'analyse de sentiment
def analyser_sentiment(commentaire):
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
    
    # Détermination du sentiment
    if score <= -2:
        emotion = "Très négatif 😡"
        satisfaction = 2
        couleur = "#f44336"
        classe_css = "risk-high"
    elif score == -1:
        emotion = "Négatif 😕"
        satisfaction = 4
        couleur = "#ff9800"
        classe_css = "risk-medium"
    elif score == 0:
        emotion = "Neutre 😐"
        satisfaction = 6
        couleur = "#ffc107"
        classe_css = "risk-medium"
    elif score == 1:
        emotion = "Positif 🙂"
        satisfaction = 8
        couleur = "#8bc34a"
        classe_css = "risk-low"
    else:
        emotion = "Très positif 😄"
        satisfaction = 9.5
        couleur = "#4caf50"
        classe_css = "risk-low"
    
    return {
        "emotion": emotion,
        "satisfaction": satisfaction,
        "couleur": couleur,
        "classe_css": classe_css,
        "score": score,
        "mots_positifs": mots_positifs,
        "mots_negatifs": mots_negatifs
    }

# Fonction de calcul du risque de churn
def calculer_risque_churn(satisfaction, age, anciennete, prix_mensuel, appels_support, retards_paiement, type_service, type_contrat):
    # Calcul du score de base
    score_risque = 30
    facteurs_positifs = []
    facteurs_negatifs = []
    
    # Impact de la satisfaction
    if satisfaction <= 3:
        score_risque += 40
        facteurs_negatifs.append("Très faible satisfaction client")
    elif satisfaction <= 5:
        score_risque += 20
        facteurs_negatifs.append("Satisfaction client moyenne")
    elif satisfaction <= 7:
        score_risque += 10
        facteurs_negatifs.append("Satisfaction légèrement inférieure")
    
    if satisfaction >= 8:
        score_risque -= 20
        facteurs_positifs.append("Bonne satisfaction client")
    
    # Impact des appels support
    if appels_support >= 5:
        score_risque += 25
        facteurs_negatifs.append("Appels support très fréquents")
    elif appels_support >= 3:
        score_risque += 15
        facteurs_negatifs.append("Appels support fréquents")
    
    # Impact des retards de paiement
    if retards_paiement >= 3:
        score_risque += 30
        facteurs_negatifs.append("Retards de paiement répétés")
    elif retards_paiement >= 1:
        score_risque += 15
        facteurs_negatifs.append("Retards de paiement occasionnels")
    
    if retards_paiement == 0:
        score_risque -= 10
        facteurs_positifs.append("Aucun retard de paiement")
    
    # Impact de l'ancienneté
    if anciennete < 6:
        score_risque += 20
        facteurs_negatifs.append("Ancienneté très faible")
    
    if anciennete >= 24:
        score_risque -= 25
        facteurs_positifs.append("Ancienneté élevée")
    
    # Impact du type de contrat
    if type_contrat == "Mensuel":
        score_risque += 15
        facteurs_negatifs.append("Contrat mensuel facile à résilier")
    elif type_contrat == "2 ans":
        score_risque -= 30
        facteurs_positifs.append("Contrat long terme")
    
    # Normalisation du score
    score_risque = max(5, min(95, score_risque))
    probabilite = score_risque / 100
    
    # Détermination du niveau de risque
    if probabilite >= 0.7:
        niveau = "🚨 TRÈS ÉLEVÉ"
        couleur = "#f44336"
        classe_css = "risk-high"
        emoji = "🔥"
        priorite = "HAUTE PRIORITÉ"
        recommandation = "Contact immédiat requis - Offre de fidélisation urgente"
        actions = [
            {"icon": "📞", "titre": "Contact immédiat", "description": "Appeler dans les 24h pour comprendre les problèmes"},
            {"icon": "🎁", "titre": "Offre promotionnelle", "description": "Proposer 30% de réduction pour 6 mois"},
            {"icon": "👥", "titre": "Gestionnaire dédié", "description": "Assigner un responsable client spécifique"},
            {"icon": "🔧", "titre": "Audit technique", "description": "Analyser et résoudre les problèmes techniques"}
        ]
    elif probabilite >= 0.5:
        niveau = "⚠️ ÉLEVÉ"
        couleur = "#ff9800"
        classe_css = "risk-medium"
        emoji = "⚠️"
        priorite = "PRIORITÉ MOYENNE-HAUTE"
        recommandation = "Offrir promotion dans les 7 jours - Surveillance active"
        actions = [
            {"icon": "📧", "titre": "Email personnalisé", "description": "Envoyer une offre sous 7 jours"},
            {"icon": "📅", "titre": "Rendez-vous satisfaction", "description": "Programmer un appel de suivi"},
            {"icon": "🔍", "titre": "Analyse historique", "description": "Examiner les problèmes récurrents"},
            {"icon": "💳", "titre": "Facilitation paiement", "description": "Proposer le prélèvement automatique"}
        ]
    elif probabilite >= 0.3:
        niveau = "📊 MODÉRÉ"
        couleur = "#ffc107"
        classe_css = "risk-medium"
        emoji = "📊"
        priorite = "PRIORITÉ MOYENNE"
        recommandation = "Surveillance mensuelle - Maintenir la qualité de service"
        actions = [
            {"icon": "📊", "titre": "Suivi mensuel", "description": "Revue régulière de la satisfaction"},
            {"icon": "🔔", "titre": "Rappel renouvellement", "description": "Notification anticipée de fin de contrat"},
            {"icon": "🌟", "titre": "Upselling", "description": "Proposer des services complémentaires"},
            {"icon": "📋", "titre": "Feedback client", "description": "Demander régulièrement des retours"}
        ]
    else:
        niveau = "✅ FAIBLE"
        couleur = "#4caf50"
        classe_css = "risk-low"
        emoji = "✅"
        priorite = "PRIORITÉ BASSE"
        recommandation = "Client fidèle - Renforcer la relation client"
        actions = [
            {"icon": "⭐", "titre": "Programme fidélité", "description": "Inviter au programme VIP client"},
            {"icon": "🎯", "titre": "Offres premium", "description": "Proposer des services exclusifs"},
            {"icon": "🤝", "titre": "Événements clients", "description": "Invitation aux événements OORedoo"},
            {"icon": "📈", "titre": "Advocacy", "description": "Encourager les témoignages positifs"}
        ]
    
    return {
        "probabilite": probabilite,
        "score_risque": score_risque,
        "niveau": niveau,
        "couleur": couleur,
        "classe_css": classe_css,
        "emoji": emoji,
        "priorite": priorite,
        "recommandation": recommandation,
        "actions": actions,
        "facteurs_positifs": facteurs_positifs,
        "facteurs_negatifs": facteurs_negatifs
    }

# Fonction pour créer le graphique jauge
def creer_jauge(probabilite, couleur, titre):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probabilite * 100,
        title={"text": titre, "font": {"size": 22, "color": couleur}},
        number={"font": {"size": 42, "color": couleur}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkgray"},
            "bar": {"color": couleur, "thickness": 0.4},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, 30], "color": "#e8f5e9", "name": "Faible"},
                {"range": [30, 50], "color": "#fff3e0", "name": "Modéré"},
                {"range": [50, 70], "color": "#ffe0b2", "name": "Élevé"},
                {"range": [70, 100], "color": "#ffcdd2", "name": "Très élevé"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.8,
                "value": 50
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin={"t": 60, "b": 30, "l": 30, "r": 30},
        font={"family": "Arial"}
    )
    
    return fig

# Interface principale
def main():
    # En-tête
    st.markdown("<h1 class='main-header'>📱 OOREDOO ALGÉRIE - PRÉDICTION DE CHURN INTELLIGENTE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>Analyse de sentiment multilingue + prédiction de risque d'attrition</p>", unsafe_allow_html=True)
    
    # Initialisation de l'état de session
    if 'satisfaction_calculee' not in st.session_state:
        st.session_state.satisfaction_calculee = None
    
    if 'dernier_calcul' not in st.session_state:
        st.session_state.dernier_calcul = None
    
    # Onglets
    tab1, tab2 = st.tabs(["🧠 Analyse de Sentiment", "📊 Saisie Manuelle"])
    
    with tab1:
        st.markdown("### Analyse Automatique de Satisfaction")
        st.markdown("Analysez automatiquement la satisfaction client à partir d'un commentaire.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            commentaire = st.text_area(
                "Commentaire client:",
                placeholder="✍️ Tapez ou collez le commentaire du client dans n'importe quelle langue...",
                height=200,
                help="Support multilingue : Darja 🇩🇿 | Arabe 🇸🇦 | Français 🇫🇷 | English 🇬🇧"
            )
            
            if st.button("🔍 ANALYSER LE SENTIMENT", use_container_width=True):
                if len(commentaire.strip()) < 3:
                    st.error("⚠️ Veuillez entrer un commentaire d'au moins 3 caractères")
                else:
                    resultat_sentiment = analyser_sentiment(commentaire)
                    st.session_state.satisfaction_calculee = resultat_sentiment["satisfaction"]
                    
                    # Affichage des résultats du sentiment
                    with st.container():
                        st.markdown(f"""
                        <div class='card {resultat_sentiment["classe_css"]}'>
                            <div style='display: flex; align-items: center; margin-bottom: 20px;'>
                                <span style='font-size: 48px; margin-right: 20px;'>{resultat_sentiment["emotion"].split()[-1]}</span>
                                <div>
                                    <h2 style='margin: 0; color: {resultat_sentiment["couleur"]};'>{resultat_sentiment["emotion"]}</h2>
                                    <h1 style='margin: 0;'>Satisfaction estimée: {resultat_sentiment["satisfaction"]}/10</h1>
                                </div>
                            </div>
                            
                            <div style='margin: 20px 0;'>
                                <strong>Score de sentiment:</strong> {resultat_sentiment["score"]} 
                                ({len(resultat_sentiment["mots_positifs"])} positif{'s' if len(resultat_sentiment["mots_positifs"]) > 1 else ''}, 
                                {len(resultat_sentiment["mots_negatifs"])} négatif{'s' if len(resultat_sentiment["mots_negatifs"]) > 1 else ''})
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Affichage des mots détectés
                    if resultat_sentiment["mots_positifs"]:
                        st.markdown("**Mots positifs détectés:**")
                        cols = st.columns(4)
                        for i, mot in enumerate(resultat_sentiment["mots_positifs"][:8]):
                            with cols[i % 4]:
                                st.markdown(f"<div style='background: #4caf50; color: white; padding: 5px 10px; border-radius: 15px; text-align: center; margin: 2px;'>{mot}</div>", unsafe_allow_html=True)
                    
                    if resultat_sentiment["mots_negatifs"]:
                        st.markdown("**Mots négatifs détectés:**")
                        cols = st.columns(4)
                        for i, mot in enumerate(resultat_sentiment["mots_negatifs"][:8]):
                            with cols[i % 4]:
                                st.markdown(f"<div style='background: #f44336; color: white; padding: 5px 10px; border-radius: 15px; text-align: center; margin: 2px;'>{mot}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 💡 Exemples de commentaires")
            
            exemples = {
                "Client très satisfait": "خدمة ممتازة وراقية، سرعة الانترنت جيدة جدا، شكرا فريق الدعم المحترف. Je recommande OORedoo!",
                "Client moyennement satisfait": "Service correct mais parfois des coupures le soir. Le support répond mais pas toujours de solution rapide.",
                "Client insatisfait": "Service très mauvais, connexion lente tout le temps. Déçu depuis le début, je vais changer d'opérateur."
            }
            
            for titre, exemple in exemples.items():
                if st.button(f"📝 {titre}", key=f"ex_{titre}", use_container_width=True):
                    st.session_state.commentaire_exemple = exemple
                    st.rerun()
    
    with tab2:
        st.markdown("### Saisie Manuelle des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Informations personnelles")
            
            if st.session_state.satisfaction_calculee:
                satisfaction = st.slider(
                    "Satisfaction client (1-10):",
                    min_value=1, max_value=10, value=int(st.session_state.satisfaction_calculee),
                    help=f"Satisfaction calculée: {st.session_state.satisfaction_calculee}/10"
                )
            else:
                satisfaction = st.slider(
                    "Satisfaction client (1-10):",
                    min_value=1, max_value=10, value=7
                )
            
            age = st.slider(
                "Âge du client:",
                min_value=18, max_value=70, value=35
            )
            
            anciennete = st.slider(
                "Ancienneté (mois):",
                min_value=1, max_value=60, value=12
            )
        
        with col2:
            st.markdown("#### 📱 Service et facturation")
            
            appels_support = st.slider(
                "Appels support / mois:",
                min_value=0, max_value=20, value=2
            )
            
            retards_paiement = st.slider(
                "Retards de paiement:",
                min_value=0, max_value=10, value=0
            )
            
            prix_mensuel = st.slider(
                "Prix mensuel (DZD):",
                min_value=500, max_value=15000, value=3500, step=100
            )
            
            type_service = st.selectbox(
                "Type de service:",
                ["Mobile", "Fibre"]
            )
            
            type_contrat = st.selectbox(
                "Type de contrat:",
                ["Mensuel", "3 mois", "1 an", "2 ans"]
            )
    
    # Bouton de calcul principal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 CALCULER LE RISQUE DE CHURN", use_container_width=True):
            # Vérification des données
            donnees_valides = True
            
            # Récupération des données selon l'onglet actif
            if tab1._active and 'satisfaction_calculee' in st.session_state and st.session_state.satisfaction_calculee:
                satisfaction = st.session_state.satisfaction_calculee
            elif tab2._active:
                satisfaction = satisfaction
            else:
                st.error("⚠️ Veuillez d'abord analyser un commentaire ou utiliser l'onglet 'Saisie Manuelle'")
                donnees_valides = False
            
            if donnees_valides:
                # Calcul du risque
                resultat = calculer_risque_churn(
                    satisfaction=satisfaction,
                    age=age,
                    anciennete=anciennete,
                    prix_mensuel=prix_mensuel,
                    appels_support=appels_support,
                    retards_paiement=retards_paiement,
                    type_service=type_service,
                    type_contrat=type_contrat
                )
                
                st.session_state.dernier_calcul = resultat
                
                # Affichage des résultats
                st.markdown("---")
                st.markdown("<h2 style='color: #E30613;'>📊 Résultats de la prédiction</h2>", unsafe_allow_html=True)
                
                # Carte de résultat principal
                st.markdown(f"""
                <div class='card {resultat["classe_css"]}'>
                    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
                        <div style='flex: 1;'>
                            <h1 style='font-size: 82px; color: {resultat["couleur"]}; margin: 0; text-align: center;'>{resultat["probabilite"]*100:.0f}%</h1>
                            <h2 style='color: {resultat["couleur"]}; text-align: center; margin: 10px 0;'>{resultat["niveau"]}</h2>
                            <div style='text-align: center;'>
                                <span class='badge' style='background: #333; color: white; padding: 8px 16px; border-radius: 20px;'>{resultat["priorite"]}</span>
                            </div>
                        </div>
                        <div style='flex: 2; padding-left: 30px;'>
                            <h3><i class='fas fa-chart-line'></i> Analyse du risque de churn</h3>
                            <p><i class='fas fa-lightbulb'></i> <strong>Recommandation:</strong> {resultat["recommandation"]}</p>
                            <div class='row' style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
                                <div>
                                    <strong>Satisfaction:</strong> {satisfaction}/10<br>
                                    <strong>Ancienneté:</strong> {anciennete} mois<br>
                                    <strong>Service:</strong> {type_service}
                                </div>
                                <div>
                                    <strong>Appels support:</strong> {appels_support}/mois<br>
                                    <strong>Retards:</strong> {retards_paiement}<br>
                                    <strong>Contrat:</strong> {type_contrat}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Jauge interactive
                fig = creer_jauge(resultat["probabilite"], resultat["couleur"], resultat["niveau"])
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyse des facteurs
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🔴 Points de vigilance")
                    if resultat["facteurs_negatifs"]:
                        for facteur in resultat["facteurs_negatifs"]:
                            st.markdown(f"<div style='background: #ffebee; padding: 10px 15px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #f44336;'>❌ {facteur}</div>", unsafe_allow_html=True)
                    else:
                        st.info("✅ Aucun point négatif significatif détecté")
                
                with col2:
                    st.markdown("#### 🟢 Points forts")
                    if resultat["facteurs_positifs"]:
                        for facteur in resultat["facteurs_positifs"]:
                            st.markdown(f"<div style='background: #e8f5e9; padding: 10px 15px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #4caf50;'>✅ {facteur}</div>", unsafe_allow_html=True)
                    else:
                        st.info("ℹ️ Aucun point positif significatif détecté")
                
                # Actions recommandées
                st.markdown("#### 🎯 Plan d'action recommandé")
                cols = st.columns(4)
                for i, action in enumerate(resultat["actions"]):
                    with cols[i]:
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; text-align: center; height: 200px;'>
                            <div style='font-size: 32px; margin-bottom: 15px;'>{action["icon"]}</div>
                            <h4 style='margin: 0 0 10px 0;'>{action["titre"]}</h4>
                            <p style='color: #666; font-size: 14px;'>{action["description"]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Export des résultats
                st.markdown("---")
                st.markdown("#### 💾 Export des résultats")
                
                if st.button("📥 Télécharger le rapport", use_container_width=True):
                    # Création du rapport
                    rapport = {
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Probabilité_Churn": f"{resultat['probabilite']*100:.1f}%",
                        "Niveau_Risque": resultat["niveau"],
                        "Priorité": resultat["priorite"],
                        "Recommandation": resultat["recommandation"],
                        "Satisfaction": f"{satisfaction}/10",
                        "Âge": f"{age} ans",
                        "Ancienneté": f"{anciennete} mois",
                        "Appels_Support": f"{appels_support}/mois",
                        "Retards_Paiement": retards_paiement,
                        "Prix_Mensuel": f"{prix_mensuel:,} DZD",
                        "Type_Service": type_service,
                        "Type_Contrat": type_contrat
                    }
                    
                    df = pd.DataFrame([rapport])
                    
                    # Conversion en CSV
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    
                    # Téléchargement
                    st.download_button(
                        label="⬇️ Télécharger CSV",
                        data=csv,
                        file_name=f"prediction_churn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
    
    # Section d'exemples
    st.markdown("---")
    st.markdown("<h3 style='color: #E30613;'>💡 Exemples de scénarios</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔥 Client à haut risque", use_container_width=True):
            st.session_state.satisfaction_calculee = 2
            st.session_state.exemple_charge = "high"
            st.rerun()
    
    with col2:
        if st.button("⚠️ Risque modéré", use_container_width=True):
            st.session_state.satisfaction_calculee = 6
            st.session_state.exemple_charge = "medium"
            st.rerun()
    
    with col3:
        if st.button("✅ Client fidèle", use_container_width=True):
            st.session_state.satisfaction_calculee = 9
            st.session_state.exemple_charge = "low"
            st.rerun()
    
    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>© 2024 OOREDOO Algérie - Système intelligent de prédiction de churn</p>
        <p style='font-size: 14px;'>
            <i class='fas fa-info-circle'></i> 
            Cet outil combine l'analyse de sentiment multilingue avec des algorithmes prédictifs pour estimer 
            le risque d'attrition client. Les résultats sont indicatifs et doivent être utilisés comme aide à la décision.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Fonction pour gérer les exemples pré-remplis
def charger_exemple(type_exemple):
    if type_exemple == "high":
        return {
            "satisfaction": 2,
            "age": 28,
            "anciennete": 4,
            "prix_mensuel": 2500,
            "appels_support": 8,
            "retards_paiement": 2,
            "type_service": "Mobile",
            "type_contrat": "Mensuel"
        }
    elif type_exemple == "medium":
        return {
            "satisfaction": 6,
            "age": 42,
            "anciennete": 18,
            "prix_mensuel": 4500,
            "appels_support": 4,
            "retards_paiement": 1,
            "type_service": "Fibre",
            "type_contrat": "1 an"
        }
    elif type_exemple == "low":
        return {
            "satisfaction": 9,
            "age": 55,
            "anciennete": 36,
            "prix_mensuel": 6000,
            "appels_support": 1,
            "retards_paiement": 0,
            "type_service": "Fibre",
            "type_contrat": "2 ans"
        }
    return None

if __name__ == "__main__":
    main()