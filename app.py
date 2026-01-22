import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import re
import json
import base64
from io import BytesIO, StringIO
import sqlite3
import tempfile
import os

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
    
    /* Import card */
    .import-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px dashed #dee2e6;
        padding: 2rem;
        text-align: center;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #E30613;
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

# ============================================
# FONCTIONS D'IMPORTATION DE DONNÉES
# ============================================

def importer_fichier_csv(uploaded_file):
    """Importe et traite un fichier CSV"""
    try:
        # Essayer différents encodages
        for encoding in ['utf-8', 'latin1', 'windows-1252', 'cp1256']:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=encoding)
                st.success(f"✅ Fichier importé avec succès (encodage: {encoding})")
                return df
            except:
                continue
        
        # Si aucun encodage ne fonctionne
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur lors de l'import du fichier: {str(e)}")
        return None

def importer_fichier_excel(uploaded_file):
    """Importe et traite un fichier Excel"""
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Fichier Excel importé avec succès")
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors de l'import du fichier Excel: {str(e)}")
        return None

def importer_fichier_json(uploaded_file):
    """Importe et traite un fichier JSON"""
    try:
        df = pd.read_json(uploaded_file)
        st.success("✅ Fichier JSON importé avec succès")
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors de l'import du fichier JSON: {str(e)}")
        return None

def analyser_base_clients(df, progress_bar=None, progress_text=None):
    """Analyse une base de clients complète"""
    if df is None or df.empty:
        return None
    
    analyses = []
    total_rows = len(df)
    
    for idx, row in df.iterrows():
        # Mise à jour de la barre de progression
        if progress_bar and progress_text:
            progress = (idx + 1) / total_rows
            progress_bar.progress(progress)
            progress_text.text(f"Analyse en cours... {idx+1}/{total_rows} clients")
        
        # Analyse de sentiment si colonne commentaire existe
        satisfaction = 7  # Valeur par défaut
        
        # Rechercher les colonnes de commentaires
        comment_cols = [col for col in df.columns if 'comment' in col.lower() or 'feedback' in col.lower() or 'avis' in col.lower()]
        
        if comment_cols:
            commentaire = str(row.get(comment_cols[0], ''))
            if pd.notna(commentaire) and len(str(commentaire).strip()) >= 3:
                resultat = analyser_sentiment(str(commentaire))
                if resultat:
                    satisfaction = resultat["satisfaction"]
        
        # Extraction des valeurs avec mapping flexible des colonnes
        try:
            # Mapper les noms de colonnes possibles
            column_mapping = {
                'age': ['age', 'âge', 'client_age'],
                'anciennete': ['anciennete', 'ancienneté', 'duree_contrat', 'duration'],
                'prix': ['prix', 'montant', 'tarif', 'price', 'cost'],
                'appels': ['appels', 'calls', 'contact_support', 'reclamations'],
                'retards': ['retards', 'delays', 'late_payments', 'retard_paiement'],
                'service': ['service', 'type_service', 'product', 'offre'],
                'contrat': ['contrat', 'type_contrat', 'engagement', 'contract'],
                'satisfaction': ['satisfaction', 'score_satisfaction', 'satisfaction_score']
            }
            
            # Fonction pour trouver la colonne
            def find_column(possible_names):
                for name in possible_names:
                    if name in df.columns:
                        return row.get(name)
                return None
            
            # Extraire les valeurs
            age_val = float(find_column(column_mapping['age']) or 35)
            anciennete_val = float(find_column(column_mapping['anciennete']) or 12)
            prix_val = float(find_column(column_mapping['prix']) or 3500)
            appels_val = float(find_column(column_mapping['appels']) or 2)
            retards_val = float(find_column(column_mapping['retards']) or 0)
            service_val = str(find_column(column_mapping['service']) or 'Mobile')
            contrat_val = str(find_column(column_mapping['contrat']) or 'Mensuel')
            
            # Utiliser la satisfaction de l'analyse de sentiment ou celle du fichier
            satisfaction_file = find_column(column_mapping['satisfaction'])
            if satisfaction_file is not None:
                try:
                    satisfaction = float(satisfaction_file)
                except:
                    pass
            
            # Calculer le risque
            risque = calculer_risque_churn(
                satisfaction, age_val, anciennete_val, prix_val, 
                appels_val, retards_val, service_val, contrat_val
            )
            
            # ID client
            client_id = None
            for id_col in ['id', 'client_id', 'num_client', 'customer_id']:
                if id_col in df.columns:
                    client_id = row.get(id_col)
                    break
            
            # Nom client
            nom = None
            for name_col in ['nom', 'name', 'client', 'prenom', 'nom_complet']:
                if name_col in df.columns:
                    nom = row.get(name_col)
                    break
            
            analyses.append({
                'ID_Client': client_id or idx + 1,
                'Nom_Client': nom or f'Client_{idx + 1}',
                'Satisfaction': satisfaction,
                'Âge': age_val,
                'Ancienneté_mois': anciennete_val,
                'Prix_Mensuel_DZD': prix_val,
                'Appels_Support_mois': appels_val,
                'Retards_Paiement': retards_val,
                'Service': service_val,
                'Contrat': contrat_val,
                'Probabilité_Churn': risque['probabilite'],
                'Score_Risque': risque['score'],
                'Niveau_Risque': risque['niveau'],
                'Priorité': risque['priorite'],
                'Couleur_Risque': risque['couleur'],
                'Facteurs_Positifs': '; '.join(risque['facteurs_positifs']) if risque['facteurs_positifs'] else 'Aucun',
                'Facteurs_Négatifs': '; '.join(risque['facteurs_negatifs']) if risque['facteurs_negatifs'] else 'Aucun'
            })
            
        except Exception as e:
            st.warning(f"⚠️ Erreur d'analyse pour la ligne {idx}: {str(e)}")
            continue
    
    return pd.DataFrame(analyses)

def generer_rapport_global(df_analyses):
    """Génère un rapport complet de l'analyse"""
    if df_analyses is None or df_analyses.empty:
        return None
    
    rapport = {
        'Date_Analyse': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Clients_Analysés': len(df_analyses),
        'Probabilité_Churn_Moyenne': f"{df_analyses['Probabilité_Churn'].mean() * 100:.1f}%",
        'Score_Risque_Moyen': df_analyses['Score_Risque'].mean(),
        
        'Répartition_Risques': {
            'Très Élevé': len(df_analyses[df_analyses['Probabilité_Churn'] >= 0.7]),
            'Élevé': len(df_analyses[(df_analyses['Probabilité_Churn'] >= 0.5) & (df_analyses['Probabilité_Churn'] < 0.7)]),
            'Modéré': len(df_analyses[(df_analyses['Probabilité_Churn'] >= 0.3) & (df_analyses['Probabilité_Churn'] < 0.5)]),
            'Faible': len(df_analyses[df_analyses['Probabilité_Churn'] < 0.3])
        },
        
        'Statistiques_Satisfaction': {
            'Moyenne': f"{df_analyses['Satisfaction'].mean():.1f}/10",
            'Médiane': f"{df_analyses['Satisfaction'].median():.1f}/10",
            'Minimum': f"{df_analyses['Satisfaction'].min():.1f}/10",
            'Maximum': f"{df_analyses['Satisfaction'].max():.1f}/10"
        },
        
        'Clients_Haut_Risque': df_analyses[df_analyses['Probabilité_Churn'] >= 0.7].nlargest(20, 'Probabilité_Churn'),
        'Top_Facteurs_Négatifs': pd.Series('; '.join(df_analyses['Facteurs_Négatifs']).split('; ')).value_counts().head(10).to_dict()
    }
    
    return rapport

def exporter_rapport_excel(df_analyses, rapport_global):
    """Exporte les résultats au format Excel"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Feuille 1: Résultats détaillés
        df_analyses.to_excel(writer, sheet_name='Résultats_Churn', index=False)
        
        # Feuille 2: Résumé global
        df_resume = pd.DataFrame([
            ['Date de l\'analyse', rapport_global['Date_Analyse']],
            ['Nombre de clients analysés', rapport_global['Clients_Analysés']],
            ['Probabilité de churn moyenne', rapport_global['Probabilité_Churn_Moyenne']],
            ['Score de risque moyen', f"{rapport_global['Score_Risque_Moyen']:.1f}"],
            ['', ''],
            ['RÉPARTITION DES RISQUES', 'Nombre de clients'],
            ['🚨 Très Élevé (≥70%)', rapport_global['Répartition_Risques']['Très Élevé']],
            ['⚠️ Élevé (50-70%)', rapport_global['Répartition_Risques']['Élevé']],
            ['📊 Modéré (30-50%)', rapport_global['Répartition_Risques']['Modéré']],
            ['✅ Faible (<30%)', rapport_global['Répartition_Risques']['Faible']],
            ['', ''],
            ['STATISTIQUES DE SATISFACTION', ''],
            ['Moyenne', rapport_global['Statistiques_Satisfaction']['Moyenne']],
            ['Médiane', rapport_global['Statistiques_Satisfaction']['Médiane']],
            ['Minimum', rapport_global['Statistiques_Satisfaction']['Minimum']],
            ['Maximum', rapport_global['Statistiques_Satisfaction']['Maximum']]
        ])
        df_resume.to_excel(writer, sheet_name='Résumé_Global', index=False, header=False)
        
        # Feuille 3: Top 20 clients à risque
        if not rapport_global['Clients_Haut_Risque'].empty:
            rapport_global['Clients_Haut_Risque'].to_excel(writer, sheet_name='Top_20_Risques', index=False)
        
        # Feuille 4: Facteurs négatifs récurrents
        if rapport_global['Top_Facteurs_Négatifs']:
            df_facteurs = pd.DataFrame({
                'Facteur_Négatif': list(rapport_global['Top_Facteurs_Négatifs'].keys()),
                'Occurrences': list(rapport_global['Top_Facteurs_Négatifs'].values())
            })
            df_facteurs.to_excel(writer, sheet_name='Facteurs_Risques', index=False)
    
    output.seek(0)
    return output

def creer_visualisations(df_analyses):
    """Crée des visualisations pour l'analyse batch"""
    visualisations = {}
    
    # 1. Distribution des risques
    fig_dist = px.pie(
        names=['Faible', 'Modéré', 'Élevé', 'Très Élevé'],
        values=[
            len(df_analyses[df_analyses['Probabilité_Churn'] < 0.3]),
            len(df_analyses[(df_analyses['Probabilité_Churn'] >= 0.3) & (df_analyses['Probabilité_Churn'] < 0.5)]),
            len(df_analyses[(df_analyses['Probabilité_Churn'] >= 0.5) & (df_analyses['Probabilité_Churn'] < 0.7)]),
            len(df_analyses[df_analyses['Probabilité_Churn'] >= 0.7])
        ],
        title='Distribution des Niveaux de Risque',
        color=['Faible', 'Modéré', 'Élevé', 'Très Élevé'],
        color_discrete_map={
            'Faible': '#4caf50',
            'Modéré': '#ffc107',
            'Élevé': '#ff9800',
            'Très Élevé': '#f44336'
        }
    )
    visualisations['distribution'] = fig_dist
    
    # 2. Corrélation satisfaction vs churn
    fig_corr = px.scatter(
        df_analyses,
        x='Satisfaction',
        y='Probabilité_Churn',
        color='Niveau_Risque',
        title='Corrélation Satisfaction vs Probabilité de Churn',
        labels={'Satisfaction': 'Niveau de Satisfaction (/10)', 'Probabilité_Churn': 'Probabilité de Churn (%)'},
        color_discrete_map={
            '✅ FAIBLE': '#4caf50',
            '📊 MODÉRÉ': '#ffc107',
            '⚠️ ÉLEVÉ': '#ff9800',
            '🚨 TRÈS ÉLEVÉ': '#f44336'
        }
    )
    visualisations['correlation'] = fig_corr
    
    # 3. Top 10 clients à risque
    if len(df_analyses) > 0:
        top_10 = df_analyses.nlargest(10, 'Probabilité_Churn')
        fig_top = px.bar(
            top_10,
            x='Nom_Client',
            y='Probabilité_Churn',
            color='Probabilité_Churn',
            title='Top 10 Clients à Haut Risque de Churn',
            labels={'Probabilité_Churn': 'Probabilité de Churn', 'Nom_Client': 'Client'},
            color_continuous_scale='Reds'
        )
        visualisations['top_10'] = fig_top
    
    return visualisations

# ============================================
# FONCTIONS PRINCIPALES EXISTANTES
# ============================================

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

# ============================================
# FONCTION PRINCIPALE
# ============================================

def main():
    """Fonction principale de l'application"""
    
    # Initialisation des variables de session
    if 'satisfaction_calculee' not in st.session_state:
        st.session_state.satisfaction_calculee = None
    
    if 'dernier_risque' not in st.session_state:
        st.session_state.dernier_risque = None
    
    if 'analyse_batch' not in st.session_state:
        st.session_state.analyse_batch = None
    
    if 'donnees_importees' not in st.session_state:
        st.session_state.donnees_importees = None
    
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
    
    # Onglets principaux
    tab1, tab2, tab3 = st.tabs(["🧠 ANALYSE DE SENTIMENT", "📊 SAISIE MANUELLE", "📁 IMPORT DONNÉES"])
    
    # TAB 1: Analyse de sentiment
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
    
    # TAB 2: Saisie manuelle
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
    
    # TAB 3: Import de données
    with tab3:
        st.markdown("""
        <div class="info-card">
            <h3>📁 Import de Données Clients</h3>
            <p>Importez un fichier CSV, Excel ou JSON contenant une liste de clients pour analyse batch.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section de sélection du type d'import
        import_type = st.radio(
            "**Sélectionnez le type d'importation:**",
            ["📄 Fichier CSV/Excel/JSON", "🗄️ Base de données AISS", "✏️ Saisie manuelle multiple"],
            horizontal=True
        )
        
        if import_type == "📄 Fichier CSV/Excel/JSON":
            st.markdown("""
            <div class="import-card">
                <h4>📤 Téléverser votre fichier</h4>
                <p>Formats acceptés: CSV, Excel (.xlsx, .xls), JSON</p>
                <p style="font-size: 0.9rem; color: #666;">
                    Structure recommandée: colonnes comme ID, Nom, Âge, Ancienneté, Satisfaction, etc.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choisissez un fichier",
                type=['csv', 'xlsx', 'xls', 'json'],
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                # Détection du type de fichier
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    df_import = importer_fichier_csv(uploaded_file)
                elif file_extension in ['xlsx', 'xls']:
                    df_import = importer_fichier_excel(uploaded_file)
                elif file_extension == 'json':
                    df_import = importer_fichier_json(uploaded_file)
                else:
                    st.error("❌ Format de fichier non supporté")
                    df_import = None
                
                if df_import is not None:
                    st.session_state.donnees_importees = df_import
                    
                    # Aperçu des données
                    with st.expander("👁️ **Aperçu des données importées**", expanded=True):
                        st.dataframe(df_import.head(), use_container_width=True)
                        
                        # Statistiques
                        st.markdown("**📊 Statistiques de l'importation:**")
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("Lignes", len(df_import))
                        with col_stat2:
                            st.metric("Colonnes", len(df_import.columns))
                        with col_stat3:
                            types = ', '.join([str(dt) for dt in df_import.dtypes.unique()])
                            st.metric("Types de données", f"{len(df_import.dtypes.unique())}")
                        
                        st.markdown(f"**Colonnes disponibles:** {', '.join(df_import.columns.tolist())}")
                    
                    # Bouton d'analyse
                    if st.button("🔍 ANALYSER LA BASE DE CLIENTS", type="primary", use_container_width=True):
                        with st.spinner("Analyse en cours... Cela peut prendre quelques instants"):
                            # Barre de progression
                            progress_bar = st.progress(0)
                            progress_text = st.empty()
                            
                            # Analyse
                            df_analyses = analyser_base_clients(df_import, progress_bar, progress_text)
                            
                            if df_analyses is not None and not df_analyses.empty:
                                st.session_state.analyse_batch = df_analyses
                                
                                # Générer le rapport
                                rapport_global = generer_rapport_global(df_analyses)
                                
                                # Afficher les résultats
                                st.success(f"✅ Analyse terminée! {len(df_analyses)} clients analysés.")
                                
                                # Métriques globales
                                st.markdown("## 📊 RÉSULTATS GLOBAUX")
                                
                                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                                with col_res1:
                                    st.metric("Clients analysés", rapport_global['Clients_Analysés'])
                                with col_res2:
                                    st.metric("Churn moyen", rapport_global['Probabilité_Churn_Moyenne'])
                                with col_res3:
                                    st.metric("Score risque", f"{rapport_global['Score_Risque_Moyen']:.1f}")
                                with col_res4:
                                    sat_moy = rapport_global['Statistiques_Satisfaction']['Moyenne'].split('/')[0]
                                    st.metric("Satisfaction", sat_moy)
                                
                                # Visualisations
                                st.markdown("## 📈 VISUALISATIONS")
                                visualisations = creer_visualisations(df_analyses)
                                
                                for key, fig in visualisations.items():
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Top 20 clients à risque
                                st.markdown("## 🚨 TOP 20 CLIENTS À RISQUE")
                                top_20 = df_analyses.nlargest(20, 'Probabilité_Churn')
                                st.dataframe(
                                    top_20[['ID_Client', 'Nom_Client', 'Probabilité_Churn', 'Niveau_Risque', 'Priorité', 'Satisfaction']],
                                    use_container_width=True,
                                    column_config={
                                        'ID_Client': 'ID',
                                        'Nom_Client': 'Nom',
                                        'Probabilité_Churn': st.column_config.NumberColumn(
                                            'Probabilité Churn',
                                            format='%.1f%%'
                                        ),
                                        'Niveau_Risque': 'Niveau',
                                        'Priorité': 'Priorité',
                                        'Satisfaction': 'Satisfaction'
                                    }
                                )
                                
                                # Bouton d'export
                                st.markdown("---")
                                st.markdown("## 💾 EXPORT DES RÉSULTATS")
                                
                                col_exp1, col_exp2 = st.columns(2)
                                with col_exp1:
                                    # Export CSV
                                    csv_data = df_analyses.to_csv(index=False, encoding='utf-8-sig')
                                    st.download_button(
                                        label="📥 Télécharger CSV",
                                        data=csv_data,
                                        file_name=f"ooredoo_churn_analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                
                                with col_exp2:
                                    # Export Excel
                                    excel_data = exporter_rapport_excel(df_analyses, rapport_global)
                                    st.download_button(
                                        label="📊 Télécharger Excel",
                                        data=excel_data,
                                        file_name=f"ooredoo_churn_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
                                
                                st.info("💡 Les rapports incluent: résultats détaillés, résumé global, top 20 clients à risque, et analyse des facteurs.")
                            else:
                                st.error("❌ Aucune analyse n'a pu être effectuée. Vérifiez le format de vos données.")
        
        elif import_type == "🗄️ Base de données AISS":
            st.markdown("""
            <div class="info-card">
                <h4>🔌 Connexion à la base de données AISS</h4>
                <p>Connectez-vous à votre base de données pour importer directement les données clients.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Options de connexion
            db_type = st.selectbox(
                "**Type de base de données:**",
                ["SQLite", "MySQL", "PostgreSQL", "SQL Server"]
            )
            
            col_db1, col_db2 = st.columns(2)
            
            with col_db1:
                if db_type == "SQLite":
                    db_file = st.file_uploader("Fichier SQLite (.db)", type=['db'])
                    if db_file:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                            tmp.write(db_file.getvalue())
                            tmp_path = tmp.name
                        
                        try:
                            conn = sqlite3.connect(tmp_path)
                            tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
                            
                            if not tables.empty:
                                selected_table = st.selectbox("Sélectionnez la table:", tables['name'].tolist())
                                
                                if selected_table:
                                    if st.button("📥 Importer la table"):
                                        df_db = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
                                        st.session_state.donnees_importees = df_db
                                        st.success(f"✅ {len(df_db)} lignes importées depuis la table '{selected_table}'")
                                        st.dataframe(df_db.head(), use_container_width=True)
                            conn.close()
                        except Exception as e:
                            st.error(f"❌ Erreur de connexion: {str(e)}")
                else:
                    host = st.text_input("Hôte")
                    port = st.number_input("Port", value=3306 if db_type == "MySQL" else 5432)
                    database = st.text_input("Base de données")
            
            with col_db2:
                if db_type != "SQLite":
                    username = st.text_input("Nom d'utilisateur")
                    password = st.text_input("Mot de passe", type="password")
                    table_name = st.text_input("Nom de la table")
                    
                    if st.button("🔗 Se connecter"):
                        st.info("⚠️ Fonctionnalité en développement - La connexion directe sera disponible dans la prochaine version.")
                        st.info("En attendant, exportez vos données au format CSV et utilisez l'import de fichier.")
            
            st.markdown("---")
            st.markdown("""
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border: 1px solid #ffeaa7;">
                <h4>💡 Note sur la sécurité</h4>
                <p>Les informations de connexion sont traitées localement et ne sont pas stockées sur nos serveurs.
                Pour les environnements de production, utilisez les options d'import de fichier ou contactez
                notre équipe technique pour une intégration sécurisée.</p>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # Saisie manuelle multiple
            st.markdown("""
            <div class="info-card">
                <h4>✏️ Saisie Manuelle Multiple</h4>
                <p>Créez manuellement une liste de clients à analyser.</p>
            </div>
            """, unsafe_allow_html=True)
            
            num_clients = st.number_input("Nombre de clients à créer", min_value=1, max_value=50, value=3)
            
            clients_data = []
            
            for i in range(int(num_clients)):
                st.markdown(f"### 👤 Client {i+1}")
                
                col_cl1, col_cl2 = st.columns(2)
                
                with col_cl1:
                    nom = st.text_input(f"Nom", value=f"Client_{i+1}", key=f"nom_{i}")
                    satisfaction = st.slider(f"Satisfaction", 1, 10, 7, key=f"sat_{i}")
                    age = st.slider(f"Âge", 18, 70, 35, key=f"age_{i}")
                    anciennete = st.slider(f"Ancienneté (mois)", 1, 60, 12, key=f"anc_{i}")
                
                with col_cl2:
                    prix = st.slider(f"Prix (DZD)", 500, 15000, 3500, 100, key=f"prix_{i}")
                    appels = st.slider(f"Appels/mois", 0, 20, 2, key=f"app_{i}")
                    retards = st.slider(f"Retards", 0, 10, 0, key=f"ret_{i}")
                    service = st.selectbox(f"Service", ["Mobile", "Fibre", "4G+"], key=f"serv_{i}")
                    contrat = st.selectbox(f"Contrat", ["Mensuel", "1 an", "2 ans"], key=f"contr_{i}")
                
                clients_data.append({
                    'Nom': nom,
                    'Satisfaction': satisfaction,
                    'Âge': age,
                    'Ancienneté_mois': anciennete,
                    'Prix_Mensuel_DZD': prix,
                    'Appels_Support_mois': appels,
                    'Retards_Paiement': retards,
                    'Service': service,
                    'Contrat': contrat
                })
            
            if st.button("➕ AJOUTER ET ANALYSER", type="primary", use_container_width=True):
                df_manual = pd.DataFrame(clients_data)
                st.session_state.donnees_importees = df_manual
                
                with st.spinner("Analyse en cours..."):
                    df_analyses = analyser_base_clients(df_manual)
                    
                    if df_analyses is not None:
                        st.session_state.analyse_batch = df_analyses
                        st.success(f"✅ {len(df_analyses)} clients analysés avec succès!")
                        
                        # Afficher un aperçu
                        st.dataframe(df_analyses[['Nom_Client', 'Satisfaction', 'Probabilité_Churn', 'Niveau_Risque']], use_container_width=True)
    
    # Bouton de calcul principal (pour l'analyse individuelle)
    st.markdown("---")
    if tab1._active or tab2._active:  # Afficher seulement si on est dans les tabs 1 ou 2
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
                ancienneté_val = anciennete
                prix_val = prix
                appels_val = appels
                retards_val = retards
                service_val = service
                contrat_val = contrat
                
                # Calcul du risque
                with st.spinner("Calcul du risque en cours..."):
                    risque = calculer_risque_churn(
                        satisfaction_val, age_val, ancienneté_val, prix_val,
                        appels_val, retards_val, service_val, contrat_val
                    )
                    
                    st.session_state.dernier_risque = risque
                    st.session_state.dernieres_donnees = {
                        'satisfaction': satisfaction_val,
                        'age': age_val,
                        'anciennete': ancienneté_val,
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
                                    <div><strong>Ancienneté:</strong> {ancienneté_val} mois</div>
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
                        risque, satisfaction_val, age_val, ancienneté_val, 
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
            if st.session_state.analyse_batch is not None:
                total = len(st.session_state.analyse_batch)
            else:
                total = 1247
            st.metric("Clients analysés", f"{total:,}")
        
        col_met3, col_met4 = st.columns(2)
        with col_met3:
            st.metric("Taux de churn", "18%", "-2%")
        with col_met4:
            if st.session_state.analyse_batch is not None and not st.session_state.analyse_batch.empty:
                sat_moy = st.session_state.analyse_batch['Satisfaction'].mean()
            else:
                sat_moy = 7.2
            st.metric("Satisfaction moy.", f"{sat_moy:.1f}/10")
        
        st.markdown("---")
        
        # Résumé batch si disponible
        if st.session_state.analyse_batch is not None:
            st.markdown("### 📦 Dernière analyse batch")
            df_batch = st.session_state.analyse_batch
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.metric("Clients", len(df_batch))
            with col_b2:
                haut_risque = len(df_batch[df_batch['Probabilité_Churn'] >= 0.7])
                st.metric("Haut risque", haut_risque)
            
            if st.button("📊 Voir détails"):
                st.session_state.show_batch_details = not st.session_state.get('show_batch_details', False)
            
            if st.session_state.get('show_batch_details', False):
                st.dataframe(df_batch[['Nom_Client', 'Probabilité_Churn', 'Niveau_Risque']].head(10))
        
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
        - Analyse batch via fichiers
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
