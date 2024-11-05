import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Função para prever vitórias
def prever_vitorias(team_name, model, dados, significant_columns):
    team_data = dados[dados['common_name'] == team_name]
    if not team_data.empty:
        total_rounds = 38
        matches_played = team_data['matches_played'].values[0]
        remaining_rounds = total_rounds - matches_played
        team_X = team_data[significant_columns]
        predicted_wins = model.predict(team_X)
        predicted_wins_adjusted = (predicted_wins / matches_played) * remaining_rounds
        return predicted_wins_adjusted[0]
    else:
        return None

# Configuração do dashboard
def show_dashboard():
    
    # Estilizando o cabeçalho
    st.markdown("""
        <style>
            body {
                background-color: #f0f2f6;
            }
            .title {
                color: #1F618D;
                text-align: center;
                padding: 20px;
                font-size: 36px;
                font-weight: bold;
            }
            .dropdown {
                width: 50%;
                margin: auto;
                padding: 10px;
            }
            .stButton button {
                background-color: #FF6347;
                color: white;
                border-radius: 8px;
                width: 200px;
                height: 40px;
                font-size: 18px;
                display: block;
                margin: 20px auto;
            }
            .result-container {
                text-align: center;
                margin-top: 20px;
                font-family: 'Arial', sans-serif;
            }
            .result-container h3 {
                color: #2E86C1;
                margin-bottom: 10px;
                font-size: 24px;
                font-weight: bold;
            }
            .result-container h2 {
                color: #27AE60;
                font-size: 32px;
                font-weight: bold;
            }
        </style>
        <div class='title'>
            Previsão de Vitórias no Campeonato de Futebol
        </div>
    """, unsafe_allow_html=True)

    # Carregar os dados
    dados = pd.read_csv('../../src/data/tratado/teams_complete.csv')

    # Definir as colunas significativas para a predição
    significant_columns = ['matches_played', 'matches_played_home', 'matches_played_away', 
                        'draws', 'draws_home', 'draws_away', 'losses', 'losses_home', 'losses_away', 'points_per_game', 
                        'points_per_game_home', 'points_per_game_away', 'league_position', 'goals_scored', 'goals_conceded', 
                        'goal_difference', 'total_goal_count', 'shots_on_target', 'shots_off_target', 'average_possession']

    # Preparar a matriz de features (X) e a variável alvo (y)
    X = dados[significant_columns]
    y = dados['wins']

    # Dividir os dados em conjuntos de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

    # Treinar o modelo Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Selecionar o nome do time
    team_name = st.selectbox("Selecione o nome do time:", dados['common_name'].unique(), key='dropdown')

    # Botão centralizado e estilizado
    if st.button("⚽ Prever Vitórias"):
        resultado = prever_vitorias(team_name, model, dados, significant_columns)
        if resultado is not None:
            # Centralizar os resultados com estilo melhorado
            st.markdown(f"""
                <div class='result-container'>
                    <h3>Previsão de vitórias para {team_name} até o final do campeonato:</h3>
                    <h2>{resultado:.2f} vitórias</h2>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Sem dados suficientes para esse time.")

# Rodar a aplicação
if __name__ == '__main__':
    show_dashboard()
