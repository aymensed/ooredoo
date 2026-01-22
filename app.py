# Ajouter ces imports au début
import sqlite3
import io
import tempfile

# Ajouter après la fonction analyser_sentiment
def importer_fichier_csv(uploaded_file):
    """Importe et traite un fichier CSV"""
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        return df
    except:
        try:
            df = pd.read_csv(uploaded_file, encoding='latin1')
            return df
        except Exception as e:
            st.error(f"Erreur d'import: {e}")
            return None

def analyser_base_clients(df):
    """Analyse une base de clients complète"""
    if df is None or df.empty:
        return None
    
    analyses = []
    
    for idx, row in df.iterrows():
        # Analyse de sentiment si colonne commentaire existe
        satisfaction = 7  # Valeur par défaut
        
        if 'commentaire' in df.columns:
            resultat = analyser_sentiment(str(row.get('commentaire', '')))
            if resultat:
                satisfaction = resultat["satisfaction"]
        
        # Extraction des valeurs (avec valeurs par défaut)
        try:
            age = int(row.get('age', 35))
            anciennete = int(row.get('anciennete', 12))
            prix = float(row.get('prix', 3500))
            appels = int(row.get('appels', 2))
            retards = int(row.get('retards', 0))
            service = str(row.get('service', 'Mobile'))
            contrat = str(row.get('contrat', 'Mensuel'))
            
            risque = calculer_risque_churn(
                satisfaction, age, anciennete, prix, appels, retards, service, contrat
            )
            
            analyses.append({
                'client_id': row.get('id', idx),
                'nom': row.get('nom', f'Client_{idx}'),
                'satisfaction': satisfaction,
                'probabilite_churn': risque['probabilite'],
                'niveau_risque': risque['niveau'],
                'couleur': risque['couleur']
            })
        except Exception as e:
            st.warning(f"Erreur analyse client {idx}: {e}")
    
    return pd.DataFrame(analyses)

def generer_rapport(df_analyses):
    """Génère un rapport complet"""
    if df_analyses is None or df_analyses.empty:
        return None
    
    rapport = {
        'clients_total': len(df_analyses),
        'risque_moyen': df_analyses['probabilite_churn'].mean(),
        'haut_risque': len(df_analyses[df_analyses['probabilite_churn'] >= 0.7]),
        'risque_eleve': len(df_analyses[(df_analyses['probabilite_churn'] >= 0.5) & (df_analyses['probabilite_churn'] < 0.7)]),
        'risque_modere': len(df_analyses[(df_analyses['probabilite_churn'] >= 0.3) & (df_analyses['probabilite_churn'] < 0.5)]),
        'faible_risque': len(df_analyses[df_analyses['probabilite_churn'] < 0.3]),
        'top_risques': df_analyses.nlargest(10, 'probabilite_churn')
    }
    
    return rapport

def telecharger_resultats(df_analyses):
    """Prépare les résultats pour téléchargement"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_analyses.to_excel(writer, sheet_name='Analyse_Churn', index=False)
        
        # Ajouter un résumé
        rapport = generer_rapport(df_analyses)
        if rapport:
            df_rapport = pd.DataFrame({
                'Métrique': [
                    'Total clients analysés',
                    'Probabilité de churn moyenne',
                    'Clients à haut risque (≥70%)',
                    'Clients à risque élevé (50-70%)',
                    'Clients à risque modéré (30-50%)',
                    'Clients à faible risque (<30%)'
                ],
                'Valeur': [
                    rapport['clients_total'],
                    f"{rapport['risque_moyen']*100:.1f}%",
                    rapport['haut_risque'],
                    rapport['risque_eleve'],
                    rapport['risque_modere'],
                    rapport['faible_risque']
                ]
            })
            df_rapport.to_excel(writer, sheet_name='Résumé', index=False)
    
    output.seek(0)
    return output

# Modifier la fonction main() pour ajouter un nouvel onglet
def main():
    """Application principale"""
    
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>📱 Aymen Telecom</h1>
        <p>Plateforme de Détection du Risque de Perte Client</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation
    if 'satisfaction' not in st.session_state:
        st.session_state.satisfaction = 7
    if 'analyse_batch' not in st.session_state:
        st.session_state.analyse_batch = None
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["🧠 ANALYSE SENTIMENT", "📊 SAISIE MANUELLE", "📁 IMPORT DONNÉES"])
    
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
    
    with tab3:
        st.markdown("### 📁 Import de données")
        
        option_import = st.radio(
            "Choisissez le mode d'import:",
            ["Fichier CSV", "Base de données SQL", "Saisie manuelle multiple"]
        )
        
        if option_import == "Fichier CSV":
            uploaded_file = st.file_uploader(
                "Choisissez un fichier CSV",
                type=['csv'],
                help="Format attendu: colonnes optionnelles: id, nom, age, anciennete, prix, appels, retards, service, contrat, commentaire"
            )
            
            if uploaded_file is not None:
                df = importer_fichier_csv(uploaded_file)
                
                if df is not None:
                    st.success(f"✅ {len(df)} clients importés")
                    
                    with st.expander("📋 Aperçu des données"):
                        st.dataframe(df.head(), use_container_width=True)
                    
                    if st.button("📊 ANALYSER LA BASE", type="primary"):
                        with st.spinner("Analyse en cours..."):
                            df_analyses = analyser_base_clients(df)
                            
                            if df_analyses is not None:
                                st.session_state.analyse_batch = df_analyses
                                st.success("✅ Analyse terminée!")
                                
                                # Afficher les résultats
                                st.markdown("### 📈 Résultats de l'analyse")
                                
                                # Métriques globales
                                col1, col2, col3, col4 = st.columns(4)
                                rapport = generer_rapport(df_analyses)
                                
                                if rapport:
                                    with col1:
                                        st.metric("Total clients", rapport['clients_total'])
                                    with col2:
                                        st.metric("Churn moyen", f"{rapport['risque_moyen']*100:.1f}%")
                                    with col3:
                                        st.metric("Haut risque", rapport['haut_risque'])
                                    with col4:
                                        st.metric("Faible risque", rapport['faible_risque'])
                                    
                                    # Graphique de répartition
                                    st.markdown("### 📊 Répartition des risques")
                                    df_distribution = pd.DataFrame({
                                        'Niveau de risque': ['Faible (<30%)', 'Modéré (30-50%)', 'Élevé (50-70%)', 'Très élevé (≥70%)'],
                                        'Nombre de clients': [
                                            rapport['faible_risque'],
                                            rapport['risque_modere'],
                                            rapport['risque_eleve'],
                                            rapport['haut_risque']
                                        ]
                                    })
                                    
                                    chart = alt.Chart(df_distribution).mark_bar().encode(
                                        x=alt.X('Niveau de risque', sort=None),
                                        y='Nombre de clients',
                                        color=alt.Color('Niveau de risque', scale=alt.Scale(
                                            domain=['Faible (<30%)', 'Modéré (30-50%)', 'Élevé (50-70%)', 'Très élevé (≥70%)'],
                                            range=['#4caf50', '#ffc107', '#ff9800', '#f44336']
                                        ))
                                    )
                                    st.altair_chart(chart, use_container_width=True)
                                    
                                    # Top 10 risques
                                    st.markdown("### 🚨 Top 10 clients à risque")
                                    st.dataframe(
                                        rapport['top_risques'][['client_id', 'nom', 'probabilite_churn', 'niveau_risque']].reset_index(drop=True),
                                        use_container_width=True,
                                        column_config={
                                            'client_id': 'ID Client',
                                            'nom': 'Nom',
                                            'probabilite_churn': st.column_config.NumberColumn(
                                                'Probabilité Churn',
                                                format='%.1f%%'
                                            ),
                                            'niveau_risque': 'Niveau de risque'
                                        }
                                    )
                                    
                                    # Bouton de téléchargement
                                    st.markdown("### 💾 Télécharger les résultats")
                                    excel_data = telecharger_resultats(df_analyses)
                                    
                                    st.download_button(
                                        label="📥 Télécharger rapport Excel",
                                        data=excel_data,
                                        file_name=f"analyse_churn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
        
        elif option_import == "Base de données SQL":
            st.info("Fonctionnalité base de données - à configurer selon votre environnement")
            
            # Exemple de connexion SQLite
            db_file = st.file_uploader("Base SQLite (.db)", type=['db'])
            
            if db_file:
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                    tmp.write(db_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    conn = sqlite3.connect(tmp_path)
                    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
                    
                    if not tables.empty:
                        selected_table = st.selectbox("Sélectionnez la table:", tables['name'].tolist())
                        
                        if selected_table:
                            df_db = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 1000", conn)
                            st.dataframe(df_db.head(), use_container_width=True)
                            
                            if st.button("📊 ANALYSER BASE SQL"):
                                st.info("Implémentez l'analyse spécifique à votre schéma de base")
                    conn.close()
                except Exception as e:
                    st.error(f"Erreur connexion base: {e}")
        
        else:  # Saisie manuelle multiple
            st.markdown("### Saisie de plusieurs clients")
            
            with st.form("form_multiple_clients"):
                num_clients = st.number_input("Nombre de clients", min_value=1, max_value=50, value=3)
                
                clients_data = []
                for i in range(int(num_clients)):
                    st.markdown(f"#### Client {i+1}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nom = st.text_input(f"Nom Client {i+1}", value=f"Client_{i+1}")
                        satisfaction = st.slider(f"Satisfaction {i+1}", 1, 10, 7, key=f"sat_{i}")
                        age = st.slider(f"Âge {i+1}", 18, 70, 35, key=f"age_{i}")
                    
                    with col2:
                        anciennete = st.slider(f"Ancienneté {i+1}", 1, 60, 12, key=f"anc_{i}")
                        appels = st.slider(f"Appels {i+1}", 0, 20, 2, key=f"app_{i}")
                        retards = st.slider(f"Retards {i+1}", 0, 10, 0, key=f"ret_{i}")
                    
                    clients_data.append({
                        'nom': nom,
                        'satisfaction': satisfaction,
                        'age': age,
                        'anciennete': anciennete,
                        'appels': appels,
                        'retards': retards
                    })
                
                submitted = st.form_submit_button("ANALYSER LES CLIENTS")
                
                if submitted:
                    df_multiple = pd.DataFrame(clients_data)
                    df_analyses = analyser_base_clients(df_multiple)
                    st.session_state.analyse_batch = df_analyses
                    st.success(f"✅ {len(df_analyses)} clients analysés!")
    
    # Bouton calcul pour l'analyse individuelle
    if st.button("🚀 CALCULER RISQUE", use_container_width=True):
        risque = calculer_risque_churn(
            satisfaction, age, anciennete, prix, appels, retards, service, contrat
        )
        
        # Reste du code inchangé...
        st.markdown("---")
        st.markdown("## 📊 RÉSULTATS")
        
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
        
        st.markdown("### 📈 Niveau de risque")
        chart = creer_jauge_altair(risque['probabilite'], risque['couleur'])
        st.altair_chart(chart, use_container_width=True)
        
        st.markdown(f"""
        <div class="info-card {risque['classe']}">
            <h3>💡 Recommandation</h3>
            <p>{risque['recommandation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        if st.session_state.analyse_batch is not None:
            st.markdown("---")
            st.markdown("### 📁 Dernière analyse")
            st.info(f"{len(st.session_state.analyse_batch)} clients traités")
        
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
