import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def show_dashboard():
    global df, original_columns, imputer, scaler, model
    # Carregar os dados
    df = pd.read_csv('../../src/data/tratado/players_tratado.csv')
    player_table = pd.read_csv('../../src/data/player_table.csv')

    # Ajuste para criação da tabela de id e full_name de acordo com o estilo do código do usuário

    # Resetando o índice para criar uma coluna de 'id'
    player_table = df.reset_index()[['index', 'full_name']]
    player_table.columns = ['id', 'table_name']

    # Exibindo a tabela ajustada no Jupyter Notebook
    # Salvando a tabela em CSV
    player_table.to_csv('player_table.csv', index=False)


    # Selecionar as features e a target
    df['target'] = df['goals_overall'].apply(lambda x: 1 if x > 0 else 0)
    X = df.drop(columns=['goals_overall', 'full_name', 'target'])  # Remove as colunas desnecessárias
    y = df['target']  # Define a coluna 'target' como alvo

    # Dividir os dados em conjunto de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.6, random_state=42)

    # Treinar o modelo
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Padronizar os dados com a mesma escala
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)  # Aplica a padronização nos dados de treino
    X_test = scaler.transform(X_test)  # Aplica a mesma padronização nos dados de teste

    # Treinar o modelo
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)


    columns_to_remove = ['goals_overall', 'full_name', 'target']
    columns_to_remove = [col for col in columns_to_remove if col in df.columns]
    original_columns = df.drop(columns=columns_to_remove).columns

    # Seleciona apenas as colunas numéricas
    X_numeric = X.select_dtypes(include=[np.number])

    scaler = StandardScaler()
    imputer = SimpleImputer()

    X_imputed = imputer.fit_transform(X_numeric)
    X_scaled = scaler.fit_transform(X_imputed)


    # Função para prever a probabilidade de gol
    def predict_player_goal(table_name):
        global imputer, scaler, model, original_columns, df

        # Verifica se o nome do jogador existe na tabela player_table
        if table_name not in player_table['table_name'].values:
            return f"Jogador com nome '{table_name}' não encontrado."

        # Obtém o id do jogador
        player_id = player_table.loc[player_table['table_name'] == table_name, 'id'].values[0]

        # Verifica se o nome completo (full_name) existe no DataFrame original
        if table_name not in df['full_name'].values:
            return f"Jogador com nome completo '{table_name}' não encontrado no DataFrame original."

        # Seleciona os dados do jogador usando o full_name
        player_data = df[df['full_name'] == table_name].copy()

        # Remove as colunas desnecessárias, verifica se elas existem
        columns_to_drop = ['goals_overall', 'target', 'full_name']
        columns_to_drop = [col for col in columns_to_drop if col in player_data.columns]
        player_data = player_data.drop(columns=columns_to_drop)

        # Realinhar as colunas do player_data para que correspondam ao original_columns
        player_data = player_data.reindex(columns=original_columns, fill_value=0)

        # Seleciona apenas as colunas numéricas
        player_data_numeric = player_data.select_dtypes(include=[np.number])


        # Imputação de dados
        player_data_imputed = imputer.transform(player_data_numeric)

        # Padronização dos dados
        player_data_scaled = scaler.transform(player_data_imputed)

        # Previsão da probabilidade de marcar um gol
        probabilidade = model.predict_proba(player_data)[:, 1]

        return f"A probabilidade do jogador '{table_name}' (ID: {player_id}) marcar um gol é de {probabilidade[0]*100:.2f}%."

    # Exemplo de uso
    table_name = "Alan Kardec de Souza Pereira Junior"
    print(predict_player_goal(table_name))


    # Criação do Dashboard com Streamlit
    st.title('Predição de Gols de Jogadores')

    # Selecionar um jogador da lista
    selected_player = st.selectbox('Escolha um jogador:', player_table['table_name'].tolist())

    # Mostrar a previsão para o jogador selecionado
    if st.button('Prever Probabilidade de Gol'):
        resultado = predict_player_goal(selected_player)
        st.write(resultado)
