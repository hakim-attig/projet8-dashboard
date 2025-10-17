import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Dashboard Scoring Crédit - Accessible WCAG",
    page_icon="💳",
    layout="wide"
)

# CSS pour accessibilité WCAG
st.markdown("""
<style>
    /* Augmenter la taille du texte (WCAG 1.4.4) */
    .stMetricLabel {
        font-size: 18px !important;
    }
    .stMetricValue {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    /* Améliorer les contrastes (WCAG 1.4.3) */
    .st-emotion-cache-1y4p8pa {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "https://api-scoring-credit-final.onrender.com"

# Récupération du seuil optimal depuis l'API
OPTIMAL_THRESHOLD = 0.09  # Valeur par défaut

# Vérification API
try:
    response = requests.get(f"{API_URL}/status", timeout=2)
    api_status = response.json()
    api_ok = api_status['status'] == 'operational'
except:
    api_ok = False

# Titre de page (WCAG 2.4.2)
st.title("💳 Dashboard Scoring Crédit - Prêt à Dépenser")
st.caption("Interface d'analyse de crédit accessible - Compatible WCAG 2.1")

if not api_ok:
    st.error("⚠️ API non accessible. Veuillez patienter ou relancer.")
    st.stop()

# Infos modèle et récupération du vrai seuil
try:
    model_info = requests.get(f"{API_URL}/model/info").json()
    # Récupération du seuil depuis l'API si disponible
    if 'optimal_threshold' in model_info:
        OPTIMAL_THRESHOLD = model_info['optimal_threshold']
    st.success(f"✅ Modèle connecté | Features: {model_info.get('num_features', 254)} | Seuil: {OPTIMAL_THRESHOLD:.1%}")
except:
    st.warning("Modèle en chargement... Seuil par défaut: 9%")

# Chargement des données
@st.cache_data
def load_test_data():
    try:
        df = pd.read_csv("data/all_clients_test.csv")
        return df
    except:
        st.error("Erreur chargement données")
        return None

test_clients = load_test_data()

if test_clients is None:
    st.error("Données non disponibles")
    st.stop()

# SIDEBAR - Sélection client
st.sidebar.header("🔍 Recherche Client")
st.sidebar.markdown("**Navigation accessible** - Utilisez Tab pour naviguer")

client_ids = sorted(test_clients['SK_ID_CURR'].unique())
selected_client_id = st.sidebar.selectbox(
    "Sélectionner un client par ID",
    options=client_ids,
    index=0,
    help="Choisissez un identifiant client dans la liste"
)

st.sidebar.markdown(f"**{len(client_ids)}** clients disponibles")

# NOUVEAUTÉ : Filtrage par groupe
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtrage par groupe")

age_filter = st.sidebar.slider(
    "Filtrer par âge du client",
    min_value=20,
    max_value=70,
    value=(20, 70),
    help="Ajustez pour comparer avec des clients d'âge similaire"
)

income_filter = st.sidebar.slider(
    "Filtrer par revenus (log scale)",
    min_value=10.0,
    max_value=20.0,
    value=(10.0, 20.0),
    step=0.5,
    help="Échelle logarithmique des revenus"
)

# Bouton Analyser
if st.sidebar.button("📊 ANALYSER LE CLIENT", type="primary", use_container_width=True):
    
    with st.spinner("Analyse en cours... Veuillez patienter"):
        try:
            client_row = test_clients[test_clients['SK_ID_CURR'] == selected_client_id].iloc[0]
            
            features_to_drop = ['SK_ID_CURR', 'RISK_SCORE', 'DECISION', 'REAL_TARGET']
            features_list = [col for col in client_row.index if col not in features_to_drop]
            features = client_row[features_list].values.tolist()
            
            # Appel API
            response = requests.post(
                f"{API_URL}/predict",
                json={"features": features},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Header avec ID client
                st.header(f"📋 Analyse du Client #{selected_client_id}")
                st.markdown("---")
                
                # SECTION 1 : Métriques principales
                st.subheader("1️⃣ Résultats de l'analyse")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    risk = result['risk_score']
                    st.metric(
                        label="Risque de Défaut",
                        value=f"{risk:.1%}",
                        help="Probabilité estimée de non-remboursement"
                    )
                
                with col2:
                    decision = result['decision']
                    color = "🟢" if decision == "ACCORD" else "🔴"
                    st.metric(
                        label="Décision",
                        value=f"{color} {decision}",
                        help="Décision basée sur le seuil optimal"
                    )
                
                with col3:
                    st.metric(
                        label="Seuil décisionnel",
                        value=f"{OPTIMAL_THRESHOLD:.1%}",
                        help="Seuil optimisé pour minimiser les coûts métier"
                    )
                
                with col4:
                    real_target = int(client_row['REAL_TARGET'])
                    real_label = "❌ Défaut" if real_target == 1 else "✅ Remboursé"
                    st.metric(
                        label="Statut réel",
                        value=real_label,
                        help="Vérité terrain pour validation"
                    )
                
                # SECTION 2 : Jauge de risque
                st.subheader("2️⃣ Visualisation du niveau de risque")
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=risk * 100,
                    title={'text': "Score de Risque (%)", 'font': {'size': 20}},
                    delta={'reference': OPTIMAL_THRESHOLD * 100},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 2},
                        'bar': {'color': "#FF4B4B" if risk >= OPTIMAL_THRESHOLD else "#00CC00"},
                        'steps': [
                            {'range': [0, OPTIMAL_THRESHOLD*100], 'color': "#E8F5E9"},
                            {'range': [OPTIMAL_THRESHOLD*100, 30], 'color': "#FFF9C4"},
                            {'range': [30, 50], 'color': "#FFE0B2"},
                            {'range': [50, 100], 'color': "#FFCDD2"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.8,
                            'value': OPTIMAL_THRESHOLD * 100
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    height=350,
                    font={'size': 14},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.caption(f"Jauge de risque : Seuil de décision à {OPTIMAL_THRESHOLD:.1%}. Vert = crédit accordé, Rouge = crédit refusé")
                
                # SECTION 3 : Comparaison avec autres clients
                st.subheader("3️⃣ Comparaison avec l'ensemble des clients")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Distribution des risques
                    fig_hist = go.Figure()
                    
                    # Tous les clients
                    all_risks = test_clients['RISK_SCORE'].dropna()
                    fig_hist.add_trace(go.Histogram(
                        x=all_risks,
                        nbinsx=50,
                        name='Tous les clients',
                        opacity=0.6,
                        marker_color='lightblue'
                    ))
                    
                    # Position du client actuel
                    fig_hist.add_vline(
                        x=risk,
                        line_dash="dash",
                        line_color="red",
                        line_width=3,
                        annotation_text=f"Client actuel ({risk:.1%})"
                    )
                    
                    # Seuil
                    fig_hist.add_vline(
                        x=OPTIMAL_THRESHOLD,
                        line_dash="dot",
                        line_color="black",
                        line_width=3,
                        annotation_text=f"Seuil ({OPTIMAL_THRESHOLD:.1%})"
                    )
                    
                    fig_hist.update_layout(
                        title="Distribution des scores de risque",
                        xaxis_title="Score de risque",
                        yaxis_title="Nombre de clients",
                        showlegend=True,
                        height=400
                    )
                    
                    st.plotly_chart(fig_hist, use_container_width=True)
                    st.caption("Histogramme : La ligne noire pointillée montre le seuil de décision à 9%")
                
                with col2:
                    # Comparaison par décision
                    decisions_count = test_clients['DECISION'].value_counts()
                    client_decision = client_row['DECISION']
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=decisions_count.index,
                        values=decisions_count.values,
                        hole=0.4,
                        marker=dict(colors=['#00CC00', '#FF4B4B']),
                        textinfo='label+percent'
                    )])
                    
                    fig_pie.update_layout(
                        title=f"Répartition des décisions (Client: {client_decision})",
                        height=400,
                        font={'size': 14}
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.caption("Diagramme circulaire : Proportion de crédits accordés vs refusés")
                
                # SECTION 4 : Analyse bi-variée
                st.subheader("4️⃣ Analyse bi-variée des caractéristiques")
                
                # Sélection des features pour l'analyse
                numeric_features = ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 
                                  'DAYS_BIRTH', 'AMT_CREDIT', 'AMT_INCOME_TOTAL', 
                                  'AMT_ANNUITY', 'DAYS_EMPLOYED']
                
                available_features = [f for f in numeric_features if f in test_clients.columns]
                
                col1, col2 = st.columns(2)
                with col1:
                    feature_x = st.selectbox(
                        "Axe X - Première variable",
                        options=available_features,
                        index=0,
                        help="Sélectionnez la variable pour l'axe horizontal"
                    )
                
                with col2:
                    feature_y = st.selectbox(
                        "Axe Y - Deuxième variable",
                        options=available_features,
                        index=1,
                        help="Sélectionnez la variable pour l'axe vertical"
                    )
                
                # Graphique bi-varié
                sample_size = min(1000, len(test_clients))
                sample_clients = test_clients.sample(n=sample_size, random_state=42)
                
                fig_scatter = px.scatter(
                    sample_clients,
                    x=feature_x,
                    y=feature_y,
                    color='DECISION',
                    color_discrete_map={'ACCORD': '#00CC00', 'REFUS': '#FF4B4B'},
                    title=f"Analyse bi-variée : {feature_x} vs {feature_y}",
                    opacity=0.6
                )
                
                # Ajouter le point du client actuel
                fig_scatter.add_scatter(
                    x=[client_row[feature_x]],
                    y=[client_row[feature_y]],
                    mode='markers',
                    marker=dict(size=20, color='blue', symbol='star'),
                    name=f'Client #{selected_client_id}'
                )
                
                fig_scatter.update_layout(
                    height=500,
                    xaxis_title=feature_x,
                    yaxis_title=feature_y
                )
                
                st.plotly_chart(fig_scatter, use_container_width=True)
                st.caption(f"Graphique de dispersion : L'étoile bleue représente le client analysé")
                
                # SECTION 5 : Comparaison avec groupe similaire
                st.subheader("5️⃣ Comparaison avec clients similaires")
                
                # Filtrer les clients similaires
                if 'DAYS_BIRTH' in test_clients.columns:
                    client_age = -client_row['DAYS_BIRTH'] / 365.25
                    age_min, age_max = age_filter
                    
                    similar_clients = test_clients[
                        ((-test_clients['DAYS_BIRTH'] / 365.25) >= age_min) &
                        ((-test_clients['DAYS_BIRTH'] / 365.25) <= age_max)
                    ]
                    
                    st.info(f"📊 Comparaison avec {len(similar_clients)} clients d'âge similaire ({age_min}-{age_max} ans)")
                    
                    # Statistiques du groupe
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_risk = similar_clients['RISK_SCORE'].mean()
                        st.metric(
                            "Risque moyen du groupe",
                            f"{avg_risk:.1%}",
                            delta=f"{(risk - avg_risk)*100:.1f}%",
                            help="Différence avec la moyenne du groupe"
                        )
                    
                    with col2:
                        approval_rate = (similar_clients['DECISION'] == 'ACCORD').mean()
                        st.metric(
                            "Taux d'acceptation",
                            f"{approval_rate:.1%}",
                            help="Pourcentage de crédits accordés dans ce groupe"
                        )
                    
                    with col3:
                        default_rate = similar_clients['REAL_TARGET'].mean()
                        st.metric(
                            "Taux de défaut réel",
                            f"{default_rate:.1%}",
                            help="Taux de défaut observé dans ce groupe"
                        )
                
                # SECTION 6 : Feature importance locale (si disponible)
                st.subheader("6️⃣ Facteurs influençant la décision")
                
                try:
                    explain_resp = requests.post(f"{API_URL}/explain", json={"features": features}, timeout=10)
                    if explain_resp.status_code == 200:
                        explanation = explain_resp.json()
                        shap_df = pd.DataFrame(explanation["top_features"])
                        
                        fig_shap = px.bar(
                            shap_df.sort_values("impact", key=abs),
                            x="impact",
                            y="feature",
                            orientation='h',
                            color="direction",
                            color_discrete_map={"AUGMENTE LE RISQUE": "#FF4B4B", "DIMINUE LE RISQUE": "#00CC00"},
                            labels={"impact": "Impact SHAP", "feature": "Variable"},
                            title="Top 10 Facteurs Influençant la Décision"
                        )
                        fig_shap.update_layout(height=500, yaxis=dict(autorange="reversed"))
                        st.plotly_chart(fig_shap, use_container_width=True)
                        st.caption("Graphique SHAP : Rouge = augmente le risque, Vert = diminue le risque")
                        
                        st.info("💡 " + explanation["interpretation"])
                    else:
                        st.info("ℹ️ L'explication détaillée des facteurs n'est pas disponible actuellement")
                except:
                    st.info("ℹ️ Feature importance locale non disponible")
                
                # SECTION 7 : Interprétation finale
                st.subheader("7️⃣ Synthèse et recommandations")
                
                if decision == "ACCORD":
                    st.success(f"""
                    ### ✅ Crédit Accordé
                    - **Score de risque** : {risk:.2%} (inférieur au seuil de {OPTIMAL_THRESHOLD:.1%})
                    - **Positionnement** : Meilleur que {(all_risks > risk).mean():.1%} des clients
                    - **Recommandation** : Profil à faible risque, crédit approuvé
                    """)
                else:
                    st.error(f"""
                    ### ❌ Crédit Refusé
                    - **Score de risque** : {risk:.2%} (supérieur au seuil de {OPTIMAL_THRESHOLD:.1%})
                    - **Positionnement** : Plus risqué que {(all_risks < risk).mean():.1%} des clients
                    - **Recommandation** : Profil à risque élevé, crédit non recommandé
                    """)
                
            else:
                st.error(f"Erreur API : {response.status_code}")
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {str(e)}")

# FOOTER avec infos d'accessibilité
st.markdown("---")
st.markdown("""
**Accessibilité WCAG 2.1** | Projet 8 - OpenClassrooms | Dashboard conforme aux normes d'accessibilité
- ♿ Interface optimisée pour lecteurs d'écran
- 🎨 Contrastes respectant WCAG 1.4.3 (ratio minimum 4.5:1)
- 🔍 Texte redimensionnable jusqu'à 200% (WCAG 1.4.4)
- 🎯 Navigation au clavier complète
- 📝 Descriptions alternatives pour tous les graphiques
""")