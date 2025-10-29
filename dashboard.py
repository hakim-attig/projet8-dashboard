# ============================================================
# 💳 DASHBOARD SCORING CRÉDIT - "PRÊT À DÉPENSER"
# Version améliorée pour API Render avec design moderne
# ============================================================

import streamlit as st
import requests
import pandas as pd
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

# Style CSS moderne et accessible
st.markdown("""
<style>
    /* Design moderne avec dégradé */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Texte lisible */
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
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔌 CONFIGURATION API (LOCAL OU RENDER)
# ============================================================
# Choisir entre API locale ou Render
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
# 📄 EN-TÊTE
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
# 🧭 STRUCTURE DES ONGLETS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Analyse Client",
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
        with st.spinner("🔄 Analyse en cours..."):
            try:
                # Récupérer les données du client
                client_row = test_clients[test_clients["SK_ID_CURR"] == selected_client_id].iloc[0]
                features_to_drop = ["SK_ID_CURR", "RISK_SCORE", "DECISION", "REAL_TARGET"]
                features = client_row.drop(features_to_drop, errors="ignore").values.tolist()
                
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
                    
                    # === JAUGE DE RISQUE ===
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
                    st.caption("Les valeurs SHAP indiquent l'impact de chaque variable sur le risque")
                    
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
                        
                        if 'shap_df' in locals() and not shap_df.empty:
                            positive_features = shap_df[shap_df['direction']=='DIMINUE LE RISQUE']['feature'].head(3).tolist()
                            if positive_features:
                                st.markdown(f"**Points forts du dossier :** {', '.join(positive_features)}")
                    
                    else:
                        st.error(f"### ❌ Crédit Refusé pour le Client #{selected_client_id}")
                        st.warning(f"⚠️ Le risque de **{risk:.2%}** dépasse le seuil de **{threshold:.1%}**")
                        
                        if 'shap_df' in locals() and not shap_df.empty:
                            negative_features = shap_df[shap_df['direction']=='AUGMENTE LE RISQUE']['feature'].head(3).tolist()
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
# 🟨 ONGLET 2 : SIMULATEUR
# ============================================================
with tab2:
    st.header("🧩 Simulateur de Crédit")
    st.markdown("Modifiez les variables importantes pour voir l'impact sur la décision")
    
    if 'selected_client_id' not in locals():
        st.info("👈 Veuillez d'abord analyser un client dans l'onglet 'Analyse Client'")
    else:
        client_row = test_clients[test_clients["SK_ID_CURR"] == selected_client_id].iloc[0]
        features_to_drop = ["SK_ID_CURR", "RISK_SCORE", "DECISION", "REAL_TARGET"]
        features = client_row.drop(features_to_drop, errors="ignore")
        
        # Récupérer les top features
        response = requests.post(
            f"{API_URL}/explain",
            json={"features": features.values.tolist()},
            timeout=30
        )
        
        top_features = []
        if response.status_code == 200:
            explanation = response.json()
            if "top_features" in explanation:
                top_features = [f["feature"] for f in explanation["top_features"][:5]]
        
        if not top_features:
            st.warning("⚠️ Impossible de récupérer les variables importantes")
            st.stop()
        
        st.info(f"🎯 **Top 5 variables influentes :** {', '.join(top_features)}")
        
        # Inputs
        modified_features = {}
        cols = st.columns(2)
        
        for i, f in enumerate(top_features):
            col = cols[i % 2]
            with col:
                val = float(features[f])
                modified_features[f] = st.number_input(
                    f"**{f}**",
                    value=val,
                    step=abs(val) * 0.1 if val != 0 else 0.01,
                    format="%.4f",
                    help=f"Valeur actuelle : {val:.4f}"
                )
        
        if st.button("🔁 Simuler avec ces valeurs", type="primary", use_container_width=True):
            with st.spinner("🔄 Simulation en cours..."):
                new_features = features.copy()
                for f, v in modified_features.items():
                    new_features[f] = v
                
                response = requests.post(
                    f"{API_URL}/predict",
                    json={"features": new_features.values.tolist()},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    risk = result["risk_score"]
                    decision = result["decision"]
                    threshold = model_info.get("optimal_threshold", 0.09) if model_info else 0.09
                    
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
                        title={'text': "Risque Simulé (%)", 'font': {'color': 'white'}},
                        gauge={
                            'axis': {'range': [None, 100],'tickcolor':'white'},
                            'bar': {'color': "darkred" if risk >= threshold else "darkgreen"},
                            'steps': [
                                {'range': [0, threshold * 100], 'color': "lightgreen"},
                                {'range': [threshold * 100, 100], 'color': "lightcoral"}
                            ],
                            'threshold': {
                                'line': {'color': "yellow", 'width': 4},
                                'thickness': 0.75,
                                'value': threshold * 100
                            }
                        }
                    ))
                    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Erreur : {response.status_code}")

# ============================================================
# 📊 ONGLET 3 : STATISTIQUES
# ============================================================
with tab3:
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

# ============================================================
# 📚 ONGLET 4 : GUIDE
# ============================================================
with tab4:
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
    - Consultez le risque, la décision et les facteurs explicatifs
    
    ### 2️⃣ Simulateur
    - Modifiez les variables importantes d'un client
    - Observez l'impact sur le risque et la décision
    
    ### 3️⃣ Interprétation des Résultats
    
    **🟢 Zone Verte (< seuil)** : Risque acceptable → Crédit accordé
    
    **🔴 Zone Rouge (≥ seuil)** : Risque trop élevé → Crédit refusé
    
    **📊 Graphique SHAP** : Montre les variables qui augmentent ou diminuent le risque
    
    ---
    
    ## ♿ Accessibilité (WCAG)
    
    ✅ Contraste élevé (texte blanc sur fond sombre)
    
    ✅ Taille de texte >= 18px
    
    ✅ Couleurs + icônes (pas uniquement la couleur)
    
    ✅ Descriptions textuelles des graphiques
    
    ---
    
    ## 🔧 Support Technique
    
    En cas de problème, vérifiez que l'API est bien accessible : 
    `{API_URL}`
    """)
    
    with st.expander("🤖 Informations Techniques"):
        st.json({
            "API URL": API_URL,
            "API Status": "OK" if api_ok else "ERROR",
            "Modèle": model_info.get('model_type', 'N/A') if model_info else 'N/A',
            "Clients disponibles": len(test_clients) if test_clients is not None else 0
        })

# ============================================================
# 🔄 Footer
# ============================================================
st.markdown("---")
st.caption(f"💳 Dashboard Scoring Crédit - Prêt à Dépenser | Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.caption(f"🌐 API : {API_URL}")