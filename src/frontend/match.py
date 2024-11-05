import streamlit as st
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go


def show_dashboard():
    global imputer, scaler, rf
    # Carregar dados
    df = pd.read_csv('../../src/data/tratado/matches_tratado.csv')

    # Criando a coluna de resultado
    df['result'] = np.where(df['home_team_goal_count'] > df['away_team_goal_count'], 2, 
                            np.where(df['home_team_goal_count'] < df['away_team_goal_count'], 1, 
                                    0)) 

    # Definindo a variável alvo e os preditores
    y = df['result']
    X = df[['home_team_encoded', 'away_team_encoded', 'Pre-Match PPG (Home)', 'Pre-Match PPG (Away)', 
            'home_ppg', 'away_ppg', 'home_team_goal_count', 'away_team_goal_count', 'home_team_corner_count', 
            'away_team_corner_count', 'home_team_yellow_cards', 'home_team_red_cards', 
            'away_team_yellow_cards', 'away_team_red_cards', 'home_team_shots', 'away_team_shots', 
            'home_team_shots_on_target', 'away_team_shots_on_target', 'home_team_shots_off_target', 
            'away_team_shots_off_target', 'home_team_fouls', 'away_team_fouls', 'home_team_possession', 
            'away_team_possession', 'Home Team Pre-Match xG', 'Away Team Pre-Match xG', 'team_a_xg', 
            'team_b_xg', 'average_goals_per_match_pre_match', 'btts_percentage_pre_match', 
            'average_corners_per_match_pre_match', 'average_cards_per_match_pre_match']]

    # Imputação e padronização
    imputer = SimpleImputer(strategy='mean')
    scaler = StandardScaler()
    X_imputed = imputer.fit_transform(X)
    X_scaled = scaler.fit_transform(X_imputed)

    # Dividindo dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

    # Criando e treinando o modelo
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Função para categorizar a probabilidade
    def categorize_win_probability(prob):
        if prob < 0.2:
            return "Baixíssimas chances de ganhar"
        elif 0.2 <= prob < 0.4:
            return "Baixas chances de ganhar"
        elif 0.4 <= prob < 0.6:
            return "Médias chances de ganhar"
        elif 0.6 <= prob < 0.8:
            return "Muitas chances de ganhar"
        else:
            return "Grandes chances de ganhar"

    def predict_match_result_with_averages(home_team, away_team):
        global imputer, scaler, rf

        if isinstance(home_team, str):
            home_team_encoded = df[df['home_team_name'] == home_team]['home_team_encoded'].values[0]
            home_team_name = home_team
        else:
            home_team_encoded = home_team
            home_team_name = df[df['home_team_encoded'] == home_team_encoded]['home_team_name'].values[0]

        if isinstance(away_team, str):
            away_team_encoded = df[df['away_team_name'] == away_team]['away_team_encoded'].values[0]
            away_team_name = away_team
        else:
            away_team_encoded = away_team
            away_team_name = df[df['away_team_encoded'] == away_team_encoded]['away_team_name'].values[0]

        match_data = df[(df['home_team_encoded'] == home_team_encoded) & (df['away_team_encoded'] == away_team_encoded)].copy()

        if match_data.empty:
            home_team_stats = df[df['home_team_encoded'] == home_team_encoded].select_dtypes(include=[np.number]).mean()
            away_team_stats = df[df['away_team_encoded'] == away_team_encoded].select_dtypes(include=[np.number]).mean()
            
            match_data = pd.DataFrame({
                'Pre-Match PPG (Home)': [home_team_stats['Pre-Match PPG (Home)']],
                'Pre-Match PPG (Away)': [away_team_stats['Pre-Match PPG (Away)']],
                'home_ppg': [home_team_stats['home_ppg']],
                'away_ppg': [away_team_stats['away_ppg']],
                'home_team_corner_count': [home_team_stats['home_team_corner_count']],
                'away_team_corner_count': [away_team_stats['away_team_corner_count']],
                'home_team_yellow_cards': [home_team_stats['home_team_yellow_cards']],
                'home_team_red_cards': [home_team_stats['home_team_red_cards']],
                'away_team_yellow_cards': [away_team_stats['away_team_yellow_cards']],
                'away_team_red_cards': [away_team_stats['away_team_red_cards']],
                'home_team_shots': [home_team_stats['home_team_shots']],
                'away_team_shots': [away_team_stats['away_team_shots']],
                'home_team_shots_on_target': [home_team_stats['home_team_shots_on_target']],
                'away_team_shots_on_target': [away_team_stats['away_team_shots_on_target']],
                'home_team_shots_off_target': [home_team_stats['home_team_shots_off_target']],
                'away_team_shots_off_target': [away_team_stats['away_team_shots_off_target']],
                'home_team_fouls': [home_team_stats['home_team_fouls']],
                'away_team_fouls': [away_team_stats['away_team_fouls']],
                'home_team_possession': [home_team_stats['home_team_possession']],
                'away_team_possession': [away_team_stats['away_team_possession']],
                'Home Team Pre-Match xG': [home_team_stats['Home Team Pre-Match xG']],
                'Away Team Pre-Match xG': [away_team_stats['Away Team Pre-Match xG']],
                'team_a_xg': [home_team_stats['team_a_xg']],
                'team_b_xg': [away_team_stats['team_b_xg']],
                'average_goals_per_match_pre_match': [(home_team_stats['average_goals_per_match_pre_match'] + away_team_stats['average_goals_per_match_pre_match']) / 2],
                'btts_percentage_pre_match': [(home_team_stats['btts_percentage_pre_match'] + away_team_stats['btts_percentage_pre_match']) / 2],
                'average_corners_per_match_pre_match': [(home_team_stats['average_corners_per_match_pre_match'] + away_team_stats['average_corners_per_match_pre_match']) / 2],
                'average_cards_per_match_pre_match': [(home_team_stats['average_cards_per_match_pre_match'] + away_team_stats['average_cards_per_match_pre_match']) / 2],
                'home_team_goal_count': [0],  
                'away_team_goal_count': [0],  
                'home_team_encoded': [home_team_encoded],
                'away_team_encoded': [away_team_encoded]
            })



        match_data = match_data[X.columns]
        match_data_imputed = imputer.transform(match_data)
        match_data_scaled = scaler.transform(match_data_imputed)

        probabilities = rf.predict_proba(match_data_scaled)[0]
        home_win_prob = probabilities[2]
        draw_prob = probabilities[0]
        away_win_prob = probabilities[1]

        return home_win_prob * 100, draw_prob * 100, away_win_prob * 100


    # Função para criar um placeholder de escudo
    def team_shield_placeholder(team_name):
        return st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="
                    width: 100px;
                    height: 100px;
                    background-color: #f0f0f0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    border-radius: 50%;
                    font-weight: bold;
                    color: black;
                    margin: 10px auto;
                ">
                    {team_name[:3].upper()}
                </div>
                <div>{team_name}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # Aplicar tema escuro/claro de acordo com as preferências
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            display: flex;
            justify-content: center;
            margin: 0 auto;
        }
        .stApp.light .stButton>button {
            background-color: #2D7DD2; /* Cor de botão para tema claro */
        }
        .versus {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 24px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)


    st.title("Probabilidade de vitória, derrota e empate em uma partida")

    # Obter lista única de times
    all_teams = sorted(list(set(df['home_team_name'].unique()) | set(df['away_team_name'].unique())))

    # Layout em colunas
    col1, col2, col3 = st.columns([2,1,2])

    with col1:
        home_team = st.selectbox("Time da casa:", all_teams, key="home")
        team_shield_placeholder(home_team)

    with col2:
        st.markdown('<div class="versus">X</div>', unsafe_allow_html=True)

    with col3:
        away_team = st.selectbox("Time visitante:", all_teams, index=1, key="away")
        team_shield_placeholder(away_team)

    if st.button('Prever Resultado'):
        # Prever probabilidades de resultado com base nos times selecionados
        home_win_prob, draw_prob, away_win_prob = predict_match_result_with_averages(home_team, away_team)

        # Título "Resultados"
        st.subheader("Resultados")

        # Definindo as porcentagens normalizadas para somar 100%
        total_prob = home_win_prob + draw_prob + away_win_prob

        home_win_prob_normalized = (home_win_prob / total_prob) * 100
        draw_prob_normalized = (draw_prob / total_prob) * 100
        away_win_prob_normalized = (away_win_prob / total_prob) * 100

        # Criando o gráfico de rosca (donut)
        fig = go.Figure(go.Pie(
            labels=[f'{home_team}', 'Empate', f'{away_team}'],
            values=[home_win_prob_normalized, draw_prob_normalized, away_win_prob_normalized],
            hole=0.4,
            marker=dict(colors=['#1f77b4', '#7f7f7f', '#ffdd57']),  # Ajuste de cores para visibilidade em tema claro e escuro
            textinfo='percent+label',
            textfont_size=14
        ))

        # Ajuste da estética do gráfico
        fig.update_layout(
            title_text='Probabilidades de Resultado',
            annotations=[dict(text='Resultado', x=0.5, y=0.5, font_size=20, showarrow=False)],
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente para funcionar nos dois temas
            paper_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

        # Legendas abaixo do gráfico
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<span style='color: #1f77b4;'>■</span> {home_team}: {home_win_prob_normalized:.2f}%", unsafe_allow_html=True)
        col2.markdown(f"<span style='color: #7f7f7f;'>■</span> Empate: {draw_prob_normalized:.2f}%", unsafe_allow_html=True)
        col3.markdown(f"<span style='color: #ffdd57;'>■</span> {away_team}: {away_win_prob_normalized:.2f}%", unsafe_allow_html=True)