import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def show_dashboard():
    # Carregar e preparar os dados
    df_matches = pd.read_csv('../../src/data/matches_table.csv')  # Substitua pelo caminho do seu arquivo de dados

    # Features e target
    train_features = [
        'Pre-Match PPG (Home)', 'Pre-Match PPG (Away)', 'away_gols_recentes',
        'away_ppg', 'away_team_corner_count', 'home_team_corner_count',
        'home_ppg', 'possession_diff', 'home_corners_per_possession',
        'away_corners_per_possession', 'cards_diff', 'xg_x_btts', 'xg_diff',
        'home_efficiency_offense', 'away_efficiency_offense', 'ppg_diff',
        'ppg_x_xg_diff', 'ppg_x_xg', 'corner_diff', 'xg_x_corner'
    ]

    df_matches['match_outcome'] = df_matches.apply(lambda row: f"{row['home_team_goal_count']}x{row['away_team_goal_count']}", axis=1)
    X = df_matches[train_features]  # Features
    y = df_matches['match_outcome']  # Target

    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treinar o modelo Random Forest
    clf = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)

    # Função para prever os 3 placares mais prováveis
    def prever_top_3_placares_futuro(home_team_name, away_team_name):
        # Verificar existência dos times
        if home_team_name not in df_matches['home_team_name'].values:
            return f"Time da casa '{home_team_name}' não encontrado."
        if away_team_name not in df_matches['away_team_name'].values:
            return f"Time visitante '{away_team_name}' não encontrado."

        # Dados dos times
        home_team_data = df_matches[df_matches['home_team_name'] == home_team_name].select_dtypes(include='number').mean()
        away_team_data = df_matches[df_matches['away_team_name'] == away_team_name].select_dtypes(include='number').mean()

        # Construir as features para a previsão
        estimated_data = {
            'Pre-Match PPG (Home)': home_team_data['Pre-Match PPG (Home)'],
            'Pre-Match PPG (Away)': away_team_data['Pre-Match PPG (Away)'],
            'away_gols_recentes': away_team_data['away_gols_recentes'],
            'away_ppg': away_team_data['away_ppg'],
            'away_team_corner_count': away_team_data['away_team_corner_count'],
            'home_team_corner_count': home_team_data['home_team_corner_count'],
            'home_ppg': home_team_data['home_ppg'],
            'possession_diff': home_team_data['home_team_possession'] - away_team_data['away_team_possession'],
            'home_corners_per_possession': home_team_data['home_team_corner_count'] / home_team_data['home_team_possession'],
            'away_corners_per_possession': away_team_data['away_team_corner_count'] / away_team_data['away_team_possession'],
            'cards_diff': (home_team_data['home_team_yellow_cards'] + home_team_data['home_team_red_cards']) -
                        (away_team_data['away_team_yellow_cards'] + away_team_data['away_team_red_cards']),
            'xg_x_btts': home_team_data['team_b_xg'] * home_team_data['btts_percentage_pre_match'],
            'xg_diff': away_team_data['team_b_xg'] - home_team_data['team_a_xg'],
            'home_efficiency_offense': home_team_data['home_team_goal_count'] / home_team_data['home_team_possession'],
            'away_efficiency_offense': away_team_data['away_team_goal_count'] / away_team_data['away_team_possession'],
            'ppg_diff': away_team_data['away_ppg'] - home_team_data['home_ppg'],
            'ppg_x_xg_diff': (away_team_data['away_ppg'] - home_team_data['home_ppg']) * (away_team_data['team_b_xg'] - home_team_data['team_a_xg']),
            'ppg_x_xg': (away_team_data['away_ppg'] * away_team_data['team_b_xg']),
            'corner_diff': home_team_data['home_team_corner_count'] - away_team_data['away_team_corner_count'],
            'xg_x_corner': (away_team_data['team_b_xg'] - home_team_data['team_a_xg']) * (home_team_data['home_team_corner_count'] - away_team_data['away_team_corner_count'])
        }

        input_data = pd.DataFrame([estimated_data])
        probabilities = clf.predict_proba(input_data)
        top_3_indices = probabilities[0].argsort()[-3:][::-1]
        top_3_outcomes = [clf.classes_[i] for i in top_3_indices]

        return top_3_outcomes

    # Streamlit app
    st.title('Previsão de Resultados de Futebol')
    st.write("Escolha os times para prever os resultados mais prováveis.")

    # Inputs para o usuário selecionar os times
    home_team = st.selectbox('Selecione o time da casa', df_matches['home_team_name'].unique())
    away_team = st.selectbox('Selecione o time visitante', df_matches['away_team_name'].unique())

    if st.button('Prever Resultados'):
        resultados = prever_top_3_placares_futuro(home_team, away_team)
        if isinstance(resultados, list):
            st.write(f"Top 3 resultados mais prováveis para {home_team} vs {away_team}:")
            for i, resultado in enumerate(resultados, 1):
                st.write(f"{i}. {resultado}")
        else:
            st.write(resultados)
