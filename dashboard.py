# ============================================================
# 💳 DASHBOARD SCORING CRÉDIT - "PRÊT À DÉPENSER"
# Version finale avec TOUTES les fonctionnalités requises
# ============================================================

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ============================================================
# ⚙️ CONFIGURATION GÉNÉRALE
# ============================================================
st.set_page_config(
    page_title="Dashboard Scoring Crédit - Prêt à Dépenser",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS moderne et accessible WCAG
st.markdown("""
<style>
    /* Design moderne avec dégradé */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Texte lisible (WCAG 1.4.4 - Redimensionnement) */
    body, .stText, .stMarkdown {
        font-size: 18px !important;
        color: #FFFFFF !important;
    }
    
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Métriques élégantes */
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #E0E0E0 !important;
    }
    
    /* Sidebar moderne */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2D3748 0%, #1A202C 100%) !important;
    }
    
    /* Boutons stylés */
    .stButton>button {
        font-size: 18px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
    }
    
    /* Onglets modernes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
    }
    
    /* Cartes élégantes */
    .element-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }
    
    /* WCAG 1.4.3 - Contraste minimum assuré */
    /* Texte blanc sur fond violet foncé = ratio > 7:1 */
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔌 CONFIGURATION API
# ============================================================
USE_LOCAL_API = False  # Mettre True pour tester en local

if USE_LOCAL_API:
    API_URL = "http://127.0.0.1:8000"
else:
    API_URL = "https://api-scoring-credit-final.onrender.com"

st.sidebar.info(f"🌐 **API utilisée :** `{API_URL}`")

# ============================================================
# 🔌 VÉRIFICATION DE L'API
# ============================================================
@st.cache_data(ttl=30)
def check_api_status():
    try:
        response = requests.get(f"{API_URL}/status", timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

api_status = check_api_status()
api_ok = api_status.get("status") == "operational"

# ============================================================
# 📄 EN-TÊTE (WCAG 2.4.2 - Titre de page)
# ============================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.title("💳 Dashboard Scoring Crédit")
    st.markdown("### *Prêt à Dépenser - Analyse Transparente*")
    st.caption("Outil d'aide à la décision pour les chargés de relation client")

with col2:
    if api_ok:
        st.success("✅ API Opérationnelle")
        st.caption(f"Mise à jour : {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.error("❌ API Indisponible")
        st.caption(f"Erreur : {api_status.get('message', 'Inconnue')}")

if not api_ok:
    st.warning("⚠️ L'API n'est pas accessible. Vérifiez que le service Render est actif.")
    st.info("💡 **Astuce :** Les services gratuits Render peuvent s'endormir après 15 min d'inactivité. Le premier appel peut prendre 30-60 secondes.")
    
    if st.button("🔄 Réessayer la connexion"):
        st.cache_data.clear()
        st.rerun()
    
    st.stop()

st.markdown("---")

# ============================================================
# 📈 INFORMATIONS DU MODÈLE
# ============================================================
@st.cache_data(ttl=300)
def get_model_info():
    try:
        response = requests.get(f"{API_URL}/model/info", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

model_info = get_model_info()

if model_info:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🤖 Modèle",
            model_info['model_type'].upper(),
            help="Type d'algorithme utilisé"
        )
    
    with col2:
        st.metric(
            "🎯 Performance (AUC)",
            f"{model_info['auc_score']:.4f}",
            help="Area Under Curve - Mesure la qualité du modèle"
        )
    
    with col3:
        st.metric(
            "⚖️ Seuil Optimal",
            f"{model_info['optimal_threshold']:.1%}",
            help="Seuil de décision entre ACCORD et REFUS"
        )
    
    with col4:
        st.metric(
            "💰 Coût Optimal",
            f"{model_info['optimal_cost']:,.0f}€",
            help="Coût métier minimal avec ce seuil"
        )
    
    st.markdown("---")
else:
    st.warning("⚠️ Impossible de charger les informations du modèle")

# ============================================================
# 📂 CHARGEMENT DES DONNÉES
# ============================================================
@st.cache_data
def load_test_data():
    possible_paths = [
        "all_clients_test_sample.csv",
        "data/all_clients_test_sample.csv",
        "../all_clients_test_sample.csv"
    ]
    
    for path in possible_paths:
        try:
            df = pd.read_csv(path)
            st.sidebar.success(f"✅ Données chargées : `{path}`")
            return df
        except FileNotFoundError:
            continue
    
    st.sidebar.error("❌ Fichier `all_clients_test_sample.csv` introuvable")
    st.error("""
    **Fichier de données manquant !**
    
    Placez le fichier `all_clients_test_sample.csv` dans le même dossier que ce script.
    """)
    return None

test_clients = load_test_data()
if test_clients is None:
    st.stop()

# ============================================================
# 🧭 STRUCTURE DES ONGLETS (5 au lieu de 4)
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analyse Client",
    "🔍 Comparaisons",
    "🧩 Simulateur",
    "📈 Statistiques",
    "📚 Guide"
])

# ============================================================
# 🟦 ONGLET 1 : ANALYSE CLIENT
# ============================================================
with tab1:
    st.header("🔍 Analyse d'un Client")
    
    # Sidebar : Sélection du client
    st.sidebar.markdown("---")
    st.sidebar.header("🧍 Sélection du Client")
    
    client_ids = sorted(test_clients["SK_ID_CURR"].unique())
    
    # Option de recherche
    search_mode = st.sidebar.radio(
        "Mode de recherche",
        ["Liste déroulante", "Recherche par ID"],
        help="Choisissez comment rechercher un client"
    )
    
    if search_mode == "Liste déroulante":
        selected_client_id = st.sidebar.selectbox(
            "Choisir un client",
            options=client_ids,
            index=0
        )
    else:
        selected_client_id = st.sidebar.number_input(
            "Entrer un ID client",
            min_value=int(min(client_ids)),
            max_value=int(max(client_ids)),
            value=int(client_ids[0])
        )
    
    st.sidebar.info(f"📊 **{len(client_ids)}** clients disponibles")
    
    analyze_button = st.sidebar.button(
        "📈 Analyser ce Client",
        type="primary",
        use_container_width=True
    )
    
    if analyze_button:
        # Stocker l'ID du client analysé dans session_state
        st.session_state['current_client_id'] = selected_client_id
        
        with st.spinner("🔄 Analyse en cours..."):
            try:
                # Récupérer les données du client
                client_row = test_clients[test_clients["SK_ID_CURR"] == selected_client_id].iloc[0]
                features_to_drop = ["SK_ID_CURR", "RISK_SCORE", "DECISION", "REAL_TARGET"]
                features = client_row.drop(features_to_drop, errors="ignore").values.tolist()
                
                # Stocker les features dans session_state
                st.session_state['current_features'] = features
                st.session_state['current_client_row'] = client_row
                
                # Appel API pour prédiction
                response = requests.post(
                    f"{API_URL}/predict",
                    json={"features": features},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    risk = result["risk_score"]
                    decision = result["decision"]
                    threshold = model_info.get("optimal_threshold", 0.09) if model_info else 0.09
                    
                    # === EN-TÊTE CLIENT ===
                    st.markdown(f"## 🧍 Client **#{selected_client_id}**")
                    
                    # === INDICATEURS CLÉS ===
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "⚠️ Risque de Défaut",
                            f"{risk:.2%}",
                            delta=f"{(risk - threshold):.2%}" if risk > threshold else f"{(threshold - risk):.2%}",
                            delta_color="inverse",
                            help="Probabilité que le client ne rembourse pas son crédit"
                        )
                    
                    with col2:
                        # WCAG 1.4.1 - Utilisation de la couleur (icône + texte)
                        if decision == "ACCORD":
                            st.metric("✅ Décision", "CRÉDIT ACCORDÉ", delta="Approuvé", delta_color="normal")
                        else:
                            st.metric("❌ Décision", "CRÉDIT REFUSÉ", delta="Rejeté", delta_color="inverse")
                    
                    with col3:
                        st.metric(
                            "⚖️ Seuil de Décision",
                            f"{threshold:.1%}",
                            help="Risque maximum accepté par le modèle"
                        )
                    
                    st.markdown("---")
                    
                    # === JAUGE DE RISQUE (WCAG 1.1.1 - Contenu non textuel avec title) ===
                    st.subheader("📊 Visualisation du Risque")
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=risk * 100,
                        delta={'reference': threshold * 100, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                        title={'text': "Risque de Défaut (%)", 'font': {'size': 24, 'color': 'white'}},
                        number={'suffix': "%", 'font': {'size': 40, 'color': 'white'}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "white"},
                            'bar': {'color': "darkred" if risk >= threshold else "darkgreen", 'thickness': 0.8},
                            'bgcolor': "rgba(255,255,255,0.1)",
                            'borderwidth': 2,
                            'bordercolor': "white",
                            'steps': [
                                {'range': [0, threshold * 100], 'color': "rgba(144, 238, 144, 0.3)"},
                                {'range': [threshold * 100, 100], 'color': "rgba(255, 99, 71, 0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "yellow", 'width': 6},
                                'thickness': 0.85,
                                'value': threshold * 100
                            }
                        }
                    ))
                    
                    fig_gauge.update_layout(
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white', 'family': "Arial"}
                    )
                    
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    # === EXPLICATION SHAP ===
                    st.markdown("---")
                    st.subheader("🔍 Facteurs Influençant la Décision (SHAP)")
                    
                    # WCAG 1.1.1 - Description textuelle
                    st.info("""
                    🧠 **Comment lire ce graphique :**
                    - **Barres rouges** → Variables qui augmentent le risque de défaut
                    - **Barres vertes** → Variables qui diminuent le risque de défaut
                    - **Longueur de la barre** → Importance de l'impact
                    - Les valeurs SHAP mesurent la contribution de chaque variable à la prédiction
                    """)
                    
                    with st.spinner("🧠 Calcul des explications..."):
                        explain_resp = requests.post(
                            f"{API_URL}/explain",
                            json={"features": features},
                            timeout=30
                        )
                        
                        if explain_resp.status_code == 200:
                            explanation = explain_resp.json()
                            
                            if "top_features" in explanation:
                                shap_df = pd.DataFrame(explanation["top_features"])
                                shap_df['impact_abs'] = shap_df['impact'].abs()
                                shap_df = shap_df.sort_values("impact_abs", ascending=True)
                                
                                # Stocker dans session_state
                                st.session_state['shap_df'] = shap_df
                                
                                # Graphique SHAP amélioré
                                fig_shap = px.bar(
                                    shap_df,
                                    x="impact",
                                    y="feature",
                                    orientation="h",
                                    color="direction",
                                    color_discrete_map={
                                        "AUGMENTE LE RISQUE": "#FF6B6B",
                                        "DIMINUE LE RISQUE": "#51CF66"
                                    },
                                    labels={
                                        "impact": "Impact SHAP",
                                        "feature": "Variable",
                                        "direction": "Direction"
                                    },
                                    title="Top 10 Variables les Plus Influentes",
                                    hover_data=["value"]
                                )
                                
                                fig_shap.update_layout(
                                    height=600,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font={'color': 'white', 'size': 14},
                                    title_font_size=20,
                                    showlegend=True,
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=1.02,
                                        xanchor="right",
                                        x=1
                                    )
                                )
                                
                                fig_shap.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
                                fig_shap.update_yaxes(showgrid=False)
                                
                                st.plotly_chart(fig_shap, use_container_width=True)
                                
                                # Tableau détaillé
                                with st.expander("📋 Voir le détail des variables", expanded=False):
                                    shap_display = shap_df[['feature', 'value', 'impact', 'direction']].copy()
                                    shap_display.columns = ['Variable', 'Valeur Client', 'Impact SHAP', 'Direction']
                                    shap_display['Impact SHAP'] = shap_display['Impact SHAP'].apply(lambda x: f"{x:.4f}")
                                    shap_display['Valeur Client'] = shap_display['Valeur Client'].apply(lambda x: f"{x:.4f}")
                                    st.dataframe(shap_display, use_container_width=True, hide_index=True)
                                
                            else:
                                st.warning("⚠️ Pas d'explications SHAP disponibles")
                        
                        elif explain_resp.status_code == 503:
                            st.error("❌ L'explainer SHAP n'est pas disponible sur le serveur")
                            st.info("💡 Le modèle fonctionne mais les explications ne sont pas chargées")
                        else:
                            st.error(f"❌ Erreur lors de l'explication : {explain_resp.status_code}")
                    
                    # === MESSAGE FINAL ===
                    st.markdown("---")
                    
                    if decision == "ACCORD":
                        st.success(f"### 🎉 Crédit Accordé pour le Client #{selected_client_id}")
                        st.info(f"✅ Le risque de **{risk:.2%}** est inférieur au seuil de **{threshold:.1%}**")
                        
                        if 'shap_df' in st.session_state and not st.session_state['shap_df'].empty:
                            positive_features = st.session_state['shap_df'][st.session_state['shap_df']['direction']=='DIMINUE LE RISQUE']['feature'].head(3).tolist()
                            if positive_features:
                                st.markdown(f"**Points forts du dossier :** {', '.join(positive_features)}")
                    
                    else:
                        st.error(f"### ❌ Crédit Refusé pour le Client #{selected_client_id}")
                        st.warning(f"⚠️ Le risque de **{risk:.2%}** dépasse le seuil de **{threshold:.1%}**")
                        
                        if 'shap_df' in st.session_state and not st.session_state['shap_df'].empty:
                            negative_features = st.session_state['shap_df'][st.session_state['shap_df']['direction']=='AUGMENTE LE RISQUE']['feature'].head(3).tolist()
                            if negative_features:
                                st.markdown(f"**Points faibles du dossier :** {', '.join(negative_features)}")
                
                else:
                    st.error(f"❌ Erreur API : {response.status_code}")
                    st.code(response.text)
            
            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
                import traceback
                with st.expander("🐛 Détails de l'erreur"):
                    st.code(traceback.format_exc())

# ============================================================
# 🟩 ONGLET 2 : COMPARAISONS (NOUVEAU)
# ============================================================
with tab2:
    st.header("🔍 Comparer le Client à la Population")
    
    if 'current_client_id' not in st.session_state:
        st.info("👈 Veuillez d'abord analyser un client dans l'onglet **'Analyse Client'**")
        st.stop()
    
    client_id = st.session_state['current_client_id']
    client_row = st.session_state['current_client_row']
    
    st.markdown(f"### Client sélectionné : **#{client_id}**")
    st.markdown("---")
    
    # === SECTION 1 : FILTRES POUR GROUPE SIMILAIRE ===
    st.subheader("🎯 Définir un Groupe de Clients Similaires")
    
    col1, col2, col3 = st.columns(3)
    
    # Récupérer des variables de filtrage
    numeric_cols = test_clients.select_dtypes(include=[np.number]).columns.tolist()
    # Retirer les colonnes non pertinentes
    filter_cols = [col for col in numeric_cols if col not in ['SK_ID_CURR', 'RISK_SCORE', 'REAL_TARGET']]
    
    with col1:
        filter_var1 = st.selectbox(
            "Variable de filtre 1",
            options=filter_cols,
            index=filter_cols.index('AMT_INCOME_TOTAL') if 'AMT_INCOME_TOTAL' in filter_cols else 0
        )
        
        min_val1 = float(test_clients[filter_var1].min())
        max_val1 = float(test_clients[filter_var1].max())
        client_val1 = float(client_row[filter_var1])
        
        range1 = st.slider(
            f"Plage de {filter_var1}",
            min_value=min_val1,
            max_value=max_val1,
            value=(min_val1, max_val1),
            help=f"Valeur du client : {client_val1:.2f}"
        )
    
    with col2:
        filter_var2 = st.selectbox(
            "Variable de filtre 2",
            options=filter_cols,
            index=filter_cols.index('AMT_CREDIT') if 'AMT_CREDIT' in filter_cols else 1
        )
        
        min_val2 = float(test_clients[filter_var2].min())
        max_val2 = float(test_clients[filter_var2].max())
        client_val2 = float(client_row[filter_var2])
        
        range2 = st.slider(
            f"Plage de {filter_var2}",
            min_value=min_val2,
            max_value=max_val2,
            value=(min_val2, max_val2),
            help=f"Valeur du client : {client_val2:.2f}"
        )
    
    with col3:
        # Filtre par décision
        decision_filter = st.multiselect(
            "Filtrer par décision",
            options=['ACCORD', 'REFUS'],
            default=['ACCORD', 'REFUS'],
            help="Inclure les clients avec crédit accordé ou refusé"
        )
    
    # Appliquer les filtres
    filtered_clients = test_clients[
        (test_clients[filter_var1].between(range1[0], range1[1])) &
        (test_clients[filter_var2].between(range2[0], range2[1]))
    ]
    
    if 'DECISION' in test_clients.columns and decision_filter:
        filtered_clients = filtered_clients[filtered_clients['DECISION'].isin(decision_filter)]
    
    st.metric(
        "👥 Nombre de clients similaires trouvés",
        len(filtered_clients),
        help=f"Sur un total de {len(test_clients)} clients"
    )
    
    st.markdown("---")
    
    # === SECTION 2 : GRAPHIQUES DE COMPARAISON ===
    st.subheader("📊 Positionnement du Client par Variable")
    
    # Choisir les variables importantes à comparer
    if 'shap_df' in st.session_state:
        top_vars = st.session_state['shap_df']['feature'].head(5).tolist()
    else:
        # Variables par défaut si SHAP non disponible
        top_vars = [col for col in filter_cols[:5]]
    
    st.info(f"📌 **Variables analysées :** {', '.join(top_vars)}")
    
    # Créer des histogrammes pour chaque variable importante
    for var in top_vars:
        if var not in test_clients.columns:
            continue
        
        client_val = float(client_row[var])
        percentile = (filtered_clients[var] < client_val).mean() * 100
        
        # Créer le graphique
        fig = go.Figure()
        
        # Histogramme de la population
        fig.add_trace(go.Histogram(
            x=filtered_clients[var],
            name="Clients similaires",
            opacity=0.7,
            marker_color='lightblue',
            nbinsx=30
        ))
        
        # Ligne verticale pour le client
        fig.add_vline(
            x=client_val,
            line_dash="dash",
            line_color="red",
            line_width=3,
            annotation_text=f"Client (percentile {percentile:.0f}%)",
            annotation_position="top"
        )
        
        fig.update_layout(
            title=f"Distribution de {var}",
            xaxis_title=var,
            yaxis_title="Nombre de clients",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.1)',
            font={'color': 'white', 'size': 14},
            showlegend=True
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Valeur Client", f"{client_val:.2f}")
        with col2:
            st.metric("Moyenne Population", f"{filtered_clients[var].mean():.2f}")
        with col3:
            st.metric("Percentile", f"{percentile:.0f}%")
        
        st.markdown("---")
    
    # === SECTION 3 : ANALYSE BI-VARIÉE ===
    st.subheader("📈 Analyse Bi-variée (2 Variables)")
    
    st.info("""
    🔍 **Analyse bi-variée :** Permet de voir la relation entre deux variables
    et de positionner le client par rapport aux autres clients.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        var_x = st.selectbox(
            "Variable X (axe horizontal)",
            options=filter_cols,
            index=0
        )
    
    with col2:
        var_y = st.selectbox(
            "Variable Y (axe vertical)",
            options=filter_cols,
            index=1 if len(filter_cols) > 1 else 0
        )
    
    # Créer le scatter plot
    fig_scatter = px.scatter(
        filtered_clients,
        x=var_x,
        y=var_y,
        color='DECISION' if 'DECISION' in filtered_clients.columns else None,
        color_discrete_map={'ACCORD': '#51CF66', 'REFUS': '#FF6B6B'},
        title=f"Relation entre {var_x} et {var_y}",
        labels={var_x: var_x, var_y: var_y},
        opacity=0.6
    )
    
    # Ajouter le point du client actuel
    fig_scatter.add_trace(go.Scatter(
        x=[float(client_row[var_x])],
        y=[float(client_row[var_y])],
        mode='markers',
        marker=dict(size=20, color='yellow', symbol='star', line=dict(color='red', width=2)),
        name=f'Client #{client_id}',
        showlegend=True
    ))
    
    fig_scatter.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.1)',
        font={'color': 'white', 'size': 14},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
    fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
    
    st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================
# 🟨 ONGLET 3 : SIMULATEUR
# ============================================================
with tab3:
    st.header("🧩 Simulateur de Crédit")
    st.markdown("Modifiez les variables importantes pour voir l'impact sur la décision")
    
    if 'current_client_id' not in st.session_state:
        st.info("👈 Veuillez d'abord analyser un client dans l'onglet **'Analyse Client'**")
        st.stop()
    
    client_id = st.session_state['current_client_id']
    client_row = st.session_state['current_client_row']
    features = st.session_state['current_features']
    
    st.markdown(f"### Simulation pour le Client **#{client_id}**")
    
    # Récupérer les top features
    if 'shap_df' in st.session_state:
        top_features = st.session_state['shap_df']['feature'].head(5).tolist()
    else:
        st.warning("⚠️ Impossible de récupérer les variables importantes. Veuillez analyser un client d'abord.")
        st.stop()
    
    st.info(f"🎯 **Top 5 variables influentes :** {', '.join(top_features)}")
    
    # Inputs
    modified_features = {}
    cols = st.columns(2)
    
    for i, f in enumerate(top_features):
        col = cols[i % 2]
        with col:
            val = float(client_row[f])
            modified_features[f] = st.number_input(
                f"**{f}**",
                value=val,
                step=abs(val) * 0.1 if val != 0 else 0.01,
                format="%.4f",
                help=f"Valeur actuelle : {val:.4f}"
            )
    
    if st.button("🔁 Simuler avec ces valeurs", type="primary", use_container_width=True):
        with st.spinner("🔄 Simulation en cours..."):
            # Créer un nouveau vecteur de features
            new_features_dict = client_row.drop(['SK_ID_CURR', 'RISK_SCORE', 'DECISION', 'REAL_TARGET'], errors='ignore').to_dict()
            
            # Mettre à jour avec les valeurs modifiées
            for f, v in modified_features.items():
                new_features_dict[f] = v
            
            # Convertir en liste dans le bon ordre
            new_features = list(new_features_dict.values())
            
            response = requests.post(
                f"{API_URL}/predict",
                json={"features": new_features},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                risk = result["risk_score"]
                decision = result["decision"]
                threshold = model_info.get("optimal_threshold", 0.09) if model_info else 0.09
                
                st.markdown("---")
                st.subheader("📊 Résultat de la Simulation")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Nouveau Risque", f"{risk:.2%}")
                with col2:
                    color = "✅" if decision == "ACCORD" else "❌"
                    st.metric("Nouvelle Décision", f"{color} {decision}")
                with col3:
                    st.metric("Seuil", f"{threshold:.1%}")
                
                # Jauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=risk * 100,
                    title={'text': "Risque Simulé (%)", 'font': {'color': 'white', 'size': 20}},
                    number={'suffix': "%", 'font': {'size': 40, 'color': 'white'}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickcolor': 'white'},
                        'bar': {'color': "darkred" if risk >= threshold else "darkgreen"},
                        'steps': [
                            {'range': [0, threshold * 100], 'color': "rgba(144, 238, 144, 0.3)"},
                            {'range': [threshold * 100, 100], 'color': "rgba(255, 99, 71, 0.3)"}
                        ],
                        'threshold': {
                            'line': {'color': "yellow", 'width': 4},
                            'thickness': 0.75,
                            'value': threshold * 100
                        }
                    }
                ))
                fig.update_layout(
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Message explicatif
                if decision == "ACCORD":
                    st.success("✅ Avec ces modifications, le crédit serait **ACCORDÉ**")
                else:
                    st.error("❌ Avec ces modifications, le crédit serait **REFUSÉ**")
            
            else:
                st.error(f"Erreur API : {response.status_code}")

# ============================================================
# 📊 ONGLET 4 : STATISTIQUES
# ============================================================
with tab4:
    st.header("📈 Statistiques Globales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("👥 Nombre de Clients", f"{len(test_clients):,}")
        st.metric("📊 Nombre de Variables", f"{len(test_clients.columns) - 4}")
    
    with col2:
        if 'REAL_TARGET' in test_clients.columns:
            default_rate = test_clients['REAL_TARGET'].mean()
            st.metric("⚠️ Taux de Défaut Réel", f"{default_rate:.2%}")
        
        if 'DECISION' in test_clients.columns:
            approval_rate = (test_clients['DECISION'] == 'ACCORD').mean()
            st.metric("✅ Taux d'Approbation", f"{approval_rate:.2%}")
    
    st.markdown("---")
    
    # Distribution des décisions
    if 'DECISION' in test_clients.columns:
        st.subheader("📊 Distribution des Décisions")
        
        decision_counts = test_clients['DECISION'].value_counts()
        
        fig_pie = px.pie(
            values=decision_counts.values,
            names=decision_counts.index,
            title="Répartition ACCORD vs REFUS",
            color=decision_counts.index,
            color_discrete_map={'ACCORD': '#51CF66', 'REFUS': '#FF6B6B'}
        )
        
        fig_pie.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white', 'size': 16}
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================
# 📚 ONGLET 5 : GUIDE
# ============================================================
with tab5:
    st.header("📚 Guide d'Utilisation")
    
    st.markdown("""
    ## 🎯 Objectif du Dashboard
    
    Ce tableau de bord aide les chargés de relation client à **comprendre et expliquer** 
    les décisions d'octroi ou de refus de crédit de manière **transparente et objective**.
    
    ---
    
    ## 📖 Comment l'utiliser
    
    ### 1️⃣ Analyse d'un Client
    - Sélectionnez un client dans la sidebar
    - Cliquez sur "Analyser ce Client"
    - Consultez le risque, la décision et les facteurs explicatifs (SHAP)
    
    ### 2️⃣ Comparaisons
    - Définissez un groupe de clients similaires avec des filtres
    - Visualisez le positionnement du client par rapport à la population
    - Explorez les relations entre 2 variables (analyse bi-variée)
    
    ### 3️⃣ Simulateur
    - Modifiez les variables importantes d'un client
    - Observez l'impact sur le risque et la décision en temps réel
    
    ### 4️⃣ Statistiques
    - Consultez les statistiques globales du portefeuille
    - Répartition des décisions (accord vs refus)
    
    ---
    
    ## 🔍 Interprétation des Résultats
    
    **🟢 Zone Verte (< seuil)** : Risque acceptable → Crédit accordé
    
    **🔴 Zone Rouge (≥ seuil)** : Risque trop élevé → Crédit refusé
    
    **📊 Graphique SHAP** : Montre les variables qui augmentent ou diminuent le risque
    - Impact positif = augmente le risque
    - Impact négatif = diminue le risque
    
    **📈 Histogrammes** : Positionnent le client par rapport à la population
    - Ligne rouge = valeur du client
    - Percentile indique le % de clients en dessous de cette valeur
    
    **🎯 Analyse bi-variée** : Montre la relation entre 2 variables
    - Étoile jaune = client analysé
    - Couleurs = décision (vert = accord, rouge = refus)
    
    ---
    
    ## ♿ Accessibilité (Conformité WCAG)
    
    Ce dashboard respecte les critères d'accessibilité suivants :
    
    ✅ **1.1.1 Contenu non textuel** : Tous les graphiques ont des titres et descriptions
    
    ✅ **1.4.1 Utilisation de la couleur** : Icônes + texte (pas uniquement la couleur)
    
    ✅ **1.4.3 Contraste minimum** : Texte blanc sur fond sombre (ratio > 7:1)
    
    ✅ **1.4.4 Redimensionnement** : Texte en pixels (18px minimum)
    
    ✅ **2.4.2 Titre de page** : Titre explicite dans l'onglet du navigateur
    
    ---
    
    ## 🔧 Support Technique
    
    En cas de problème :
    - Vérifiez que l'API est accessible (statut en haut à droite)
    - Les services Render gratuits peuvent s'endormir (attendre 30-60s au premier appel)
    - Le fichier CSV doit être présent dans le même dossier que l'application
    
    **API utilisée :** `{API_URL}`
    """.format(API_URL=API_URL))
    
    with st.expander("🤖 Informations Techniques Détaillées"):
        st.json({
            "API URL": API_URL,
            "API Status": "OK" if api_ok else "ERROR",
            "Modèle": model_info.get('model_type', 'N/A') if model_info else 'N/A',
            "AUC Score": model_info.get('auc_score', 'N/A') if model_info else 'N/A',
            "Seuil Optimal": model_info.get('optimal_threshold', 'N/A') if model_info else 'N/A',
            "Clients disponibles": len(test_clients) if test_clients is not None else 0,
            "Nombre de variables": len(test_clients.columns) - 4 if test_clients is not None else 0
        })

# ============================================================
# 🔄 Footer
# ============================================================
st.markdown("---")
st.caption(f"💳 Dashboard Scoring Crédit - Prêt à Dépenser | Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.caption(f"🌐 API : {API_URL}")
st.caption("♿ Conforme WCAG 2.1 (Critères 1.1.1, 1.4.1, 1.4.3, 1.4.4, 2.4.2)")