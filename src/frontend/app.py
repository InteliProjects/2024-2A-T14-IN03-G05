import streamlit as st
import match  # Importe os arquivos que contêm os dashboards
import teams
import placar
import players

# Configuração da página deve ser a primeira chamada do Streamlit
st.set_page_config(page_title="StrikersAI Dashboard", layout="wide")

# Título da aplicação
st.markdown("<h1 style='text-align: center;'>StrikersAI Dashboard</h1>", unsafe_allow_html=True)

# Navegação com st.selectbox na barra lateral
selected_tab = st.sidebar.selectbox("Selecione o dashboard", ["", "Match", "Teams", "Placar", "Players"])

# Exibir conteúdo de acordo com a aba selecionada
if selected_tab == "Match":
    match.show_dashboard()  # Chama a função que exibe o dashboard de match
elif selected_tab == "Teams":
    teams.show_dashboard()  # Chama a função que exibe o dashboard de teams
elif selected_tab == "Placar":
    placar.show_dashboard()  # Chama a função que exibe o dashboard de placar
elif selected_tab == "Players":
    players.show_dashboard()  # Chama a função que exibe o dashboard de players
else:
    st.info("Por favor, selecione um dashboard na barra lateral.")
