import streamlit as st
from statsbombpy import sb
import pandas as pd
import plotly.express as px
from mplsoccer import Pitch
import time


def pagina_inicial():

    st.title("Métricas do futebol")
    st.subheader("Como a posse de bola de uma equipe afeta o resultado final dos jogos?")
    st.markdown("""
## Para atingir o objetivo e responder a pergunta é necessário selecionar

- Um campeonato específico.
- Uma temporada (ano).
- Uma partida.
""")
        
    competicoes = sb.competitions()

    # Campeonato 
    lista_competicoes = competicoes['competition_name'].unique().tolist()
    campeonato_selecionado = st.selectbox("Selecione um campeonato", lista_competicoes)
    id_campeonato = competicoes[competicoes['competition_name'] == campeonato_selecionado]['competition_id'].values[0]

    # Temporadas
    temporadas = competicoes[competicoes['competition_name'] == campeonato_selecionado]['season_name'].unique().tolist()
    temporada_selecionada = st.selectbox("Selecione uma temporada", temporadas)
    id_temporada = competicoes[competicoes['season_name'] == temporada_selecionada]['season_id'].values[0]

    # Partidas das opções selecionadas
    partidas = sb.matches(competition_id=competicoes[competicoes['competition_name'] == campeonato_selecionado]['competition_id'].iloc[0], 
                          season_id=competicoes[(competicoes['competition_name'] == campeonato_selecionado) & 
                                                 (competicoes['season_name'] == temporada_selecionada)]['season_id'].values[0])
    
    # Criar a lista com os nomes das partidas para usuario
    lista_partidas = partidas[['match_id', 'home_team', 'away_team', 'match_date']].copy()
    lista_partidas['match_info'] = lista_partidas['home_team'] + ' vs ' + lista_partidas['away_team'] + ' (' + lista_partidas['match_date'].astype(str) + ')'
    partida_selecionada = st.selectbox("Selecione uma partida", lista_partidas['match_info'].tolist())
    match_id_selecionada = lista_partidas[lista_partidas['match_info'] == partida_selecionada]['match_id'].values[0]

    # Armazenar escolhas do usuário na session state
    st.session_state['competition_id'] = id_campeonato
    st.session_state['season_id'] = id_temporada
    st.session_state['campeonato_selecionado'] = campeonato_selecionado
    st.session_state['temporada_selecionada'] = temporada_selecionada
    st.session_state['match_info'] = partida_selecionada
    st.session_state['match_id_selecionada'] = match_id_selecionada
    
    # Botão para ir pra próxima página
    if st.button("Visualizar métricas da partida selecionada"):
        st.session_state["pagina_selecionada"] = "Dados da partida"



def metricas_dados_usuario():
    
    # Obtém as informações do campeonato e temporada do estado da sessão
    match_id = st.session_state['match_id_selecionada']
    camp = st.session_state['competition_id']
    temp = st.session_state['season_id']
    camp_nome = st.session_state['campeonato_selecionado']
    temp_nome = st.session_state['temporada_selecionada']

    # Obtém informações sobre as partidas
    partida = sb.matches(competition_id=camp, season_id=temp)

    # Extrair as informações
    if not partida.empty:
        home_team = partida['home_team'].values[0]
        away_team = partida['away_team'].values[0]
        score_home = partida['home_score'].values[0]
        score_away = partida['away_score'].values[0]

        # Cores placar
        score_home_color = "green" if score_home > score_away else "red" if score_home < score_away else "yellow"
        score_away_color = "red" if score_home > score_away else "green" if score_home < score_away else "yellow"

        # Exibe as informações em containers
        with st.container():
            st.subheader("Informações da Partida")
            # Alinha o campeonato e a temporada nas extremidades
            st.markdown(
                f"<div style='display: flex; justify-content: space-between; font-size: 25px;'>"
                f"<div style='text-align: left;'>Campeonato: {camp_nome}</div>" 
                f"<div style='text-align: right;'>Temporada: {temp_nome}</div>"
                f"</div>", unsafe_allow_html=True
            )
            
            # Exibe os times e placar centralizados
            st.markdown(
                f"<div style='text-align: center; font-size: 30px;'>"
                f"<div style='line-height: 1.5;'>{home_team}</div>" 
                f"<div style='line-height: 1.5;'>VS</div>" 
                f"<div style='line-height: 1.5;'>{away_team}</div>"
                f"</div>", unsafe_allow_html=True
            )

            # Exibe o texto "PLACAR"
            st.markdown(
                f"<div style='text-align: center; font-size: 30px;'><strong>PLACAR</strong></div>",
                unsafe_allow_html=True
            )

            # Exibe o placar
            st.write(f"<div style='text-align: center; font-size: 48px;'>"
                        f"<span style='color:{score_home_color};'>{score_home}</span> "
                        f"x "
                        f"<span style='color:{score_away_color};'>{score_away}</span>"
                        f"</div>", unsafe_allow_html=True)
    else:
        st.warning("Partida não encontrada.")



def tipos_passes():

    # Obtém os eventos da partida selecionada e obtem times unicos
    st.title("Tipos de passes e quantidades totais")
    match_id = st.session_state['match_id_selecionada']
    eventos = sb.events(match_id=match_id)
    df_eventos = pd.DataFrame(eventos)
    times = df_eventos["team"].unique()
    
    # Tipos de passes
    for time in times:
        df_final = df_eventos[df_eventos["team"] == time]
        df_tipo_passes = df_final.groupby('pass_type').size().reset_index(name='quantidade')

        if not df_tipo_passes.empty:
            # Gráfico de barras
            fig_home = px.bar(df_tipo_passes, 
                              x='pass_type', 
                              y='quantidade', 
                              color='pass_type', 
                              title=f'Quantidade de Passes - {time}',
                              labels={'quantidade': 'Quantidade de Passes', 'pass_type': 'Tipo de Passe'},
                              color_discrete_sequence=px.colors.qualitative.Set2,
                              height=500)

            fig_home.update_layout(title={'x': 0.5},
                                   xaxis_title='Tipo de Passe', 
                                   yaxis_title='Quantidade de Passes',
                                   template='plotly_white')

            st.plotly_chart(fig_home)
        else:
            st.write(f"Não há dados de passes para o time: {time}")


def exibir_df_init():
     
    # Exibe o dataframe
    st.title("Dados utilizados para as visualizações")
    match_id = st.session_state['match_id_selecionada']
    eventos = sb.events(match_id=match_id)
    df_eventos = pd.DataFrame(eventos)
    st.dataframe(df_eventos)




def posse_de_bola():

    st.title("Posse de Bola por Time")

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)

    # Contar o número de eventos e fazer os cálculos
    posse_by_team = events['possession_team'].value_counts()
    total_posse_events = posse_by_team.sum()
    posse_porcentagem = (posse_by_team / total_posse_events) * 100

    # Criar um DataFrame com os resultados
    df_posse = pd.DataFrame({
        'team': posse_porcentagem.index,
        'possession_percentage': posse_porcentagem.values
    })

    # Gráfico de barras
    fig_posse = px.bar(df_posse,
                    x='team',
                    y='possession_percentage',
                    color='team',
                    title='Posse de Bola por Time',
                    labels={'possession_percentage': 'Posse de Bola (%)', 'team': 'Time'},
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    height=500)

    st.plotly_chart(fig_posse)



def mapa_passes():

    st.title("Mapas de passes")

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)
    team1, team2 = events['team'].unique()

    # Função para criar o mapa de passes para um time
    def create_pass_map(team):
        mask_team = (events['type'] == 'Pass') & (events['team'] == team)
        df_pass = events.loc[mask_team, ['location', 'pass_end_location', 'pass_outcome']]

        # Separar coordenadas x e y
        df_pass['x'] = df_pass['location'].apply(lambda x: x[0])
        df_pass['y'] = df_pass['location'].apply(lambda x: x[1])
        df_pass['end_x'] = df_pass['pass_end_location'].apply(lambda x: x[0])
        df_pass['end_y'] = df_pass['pass_end_location'].apply(lambda x: x[1])

        # Criar máscara para passes completos
        mask_complete = df_pass['pass_outcome'].isnull()

        # Configurar o campo
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        fig.set_facecolor('#0e1117')

        # Plotar passes completos
        pitch.arrows(df_pass[mask_complete].x, df_pass[mask_complete].y,
                     df_pass[mask_complete].end_x, df_pass[mask_complete].end_y, width=2,
                     headwidth=10, headlength=10, color='#66c2a5', ax=ax, label='Passes Completos')

        # Plotar passes incompletos
        pitch.arrows(df_pass[~mask_complete].x, df_pass[~mask_complete].y,
                     df_pass[~mask_complete].end_x, df_pass[~mask_complete].end_y, width=2,
                     headwidth=6, headlength=5, headaxislength=12,
                     color='#fc8d62', ax=ax, label='Passes Incompletos')

        # Configurar a legenda
        ax.legend(facecolor='#ffffff', handlelength=5, edgecolor='None', fontsize=12, loc='upper left')

        return fig

    # Exibir os mapas
    st.subheader(f"Mapa de Passes - {team1}")
    fig_team1 = create_pass_map(team1)
    st.pyplot(fig_team1)

    st.subheader(f"Mapa de Passes - {team2}")
    fig_team2 = create_pass_map(team2)
    st.pyplot(fig_team2)



def mapa_chutes():

    st.title("Mapas de chutes")

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)
    team1, team2 = events['team'].unique()

    # Função para criar o mapa de passes para um time
    def create_pass_map(team):
        mask_team_chute = (events['type'] == 'Shot') & (events['team'] == team)
        df_chute = events.loc[mask_team_chute, ['location', 'shot_end_location', 'shot_outcome']]

        # Separar coordenadas x e y
        df_chute['x'] = df_chute['location'].apply(lambda x: x[0])
        df_chute['y'] = df_chute['location'].apply(lambda x: x[1])
        df_chute['end_x'] = df_chute['shot_end_location'].apply(lambda x: x[0])
        df_chute['end_y'] = df_chute['shot_end_location'].apply(lambda x: x[1])

        # Criar máscara para passes completos
        mask_complete_chute = df_chute['shot_outcome'].isnull()

        # Configurar o campo
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        fig.set_facecolor('#0e1117')

        # Plotar passes completos
        pitch.arrows(df_chute[mask_complete_chute].x, df_chute[mask_complete_chute].y,
                     df_chute[mask_complete_chute].end_x, df_chute[mask_complete_chute].end_y, width=2,
                     headwidth=10, headlength=10, color='#66c2a5', ax=ax, label='Chutes Completos')

        # Plotar passes incompletos
        pitch.arrows(df_chute[~mask_complete_chute].x, df_chute[~mask_complete_chute].y,
                     df_chute[~mask_complete_chute].end_x, df_chute[~mask_complete_chute].end_y, width=2,
                     headwidth=6, headlength=5, headaxislength=12,
                     color='#fc8d62', ax=ax, label='Chutes Incompletos')

        # Configurar a legenda
        ax.legend(facecolor='#ffffff', handlelength=5, edgecolor='None', fontsize=12, loc='upper left')

        return fig

    # Mapas de passes
    st.subheader(f"Mapa de Chutes - {team1}")
    fig_team1 = create_pass_map(team1)
    st.pyplot(fig_team1)

    st.subheader(f"Mapa de Chutes - {team2}")
    fig_team2 = create_pass_map(team2)
    st.pyplot(fig_team2)




def chutes_durante_jogo():

    st.title("Chutes ao gol ao longo da partida")

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)
    
    # Filtrar eventos de chutes
    shots = events[events['type'] == 'Shot']

    # Criar uma coluna com contagem cumulativa de chutes para cada time ao longo do tempo
    shots['timestamp'] = pd.to_datetime(shots['timestamp'])
    shots_grouped = shots.groupby(['timestamp', 'team']).size().reset_index(name='shot_count')

    # Criar gráfico de linha
    fig = px.line(
        shots_grouped,
        x='timestamp',
        y='shot_count',
        color='team',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=px.colors.qualitative.Set2,
        title='Chutes ao Longo do Tempo por Time',
        labels={'shot_count': 'Número de Chutes', 'timestamp': 'Tempo'}
    )
    fig.update_traces(texttemplate='%{y}', textposition='top center')
    fig.update_layout(
        xaxis_title='Tempo',
        yaxis_title='Número de Chutes',
        xaxis=dict(tickangle=-45)
    )

    st.plotly_chart(fig)




def posse_de_bola_vs_eficiencia():

    st.title("Eficiência de chutes com base na posse de bola")

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)
    
    # Filtrar eventos possesão de bola dos times
    possession_counts = events['possession_team'].value_counts().reset_index()
    possession_counts.columns = ['team', 'possession_time']

    # Filtrar chutes a gol e gols
    shots_on_target = events[events['type'] == 'Shot']
    goals = events[events['shot_outcome'] == 'Goal']

    # Calcular chutes a gol e gols para cada time
    shots_count = shots_on_target.groupby('team').size().reset_index(name='shots')
    goals_count = goals.groupby('team').size().reset_index(name='goals')

    # Combinar os dados
    stats = possession_counts.merge(shots_count, on='team', how='left').merge(goals_count, on='team', how='left').fillna(0)
    
    # Calcular a eficiência (gols / chutes)
    stats['efficiency'] = stats['goals'] / stats['shots'].replace(0, pd.NA)  # Evitar divisão por zero
    
    # Adicionar coluna de posse de bola em porcentagem
    total_possession_time = stats['possession_time'].sum()
    stats['possession_percentage'] = (stats['possession_time'] / total_possession_time) * 100

    # Criar gráfico de dispersão
    fig = px.scatter(
        stats,
        x='possession_percentage',
        y='efficiency',
        text='team',
        title='Posse de Bola vs Eficiência (Chutes a Gol/Conversão de Gols)',
        labels={'possession_percentage': 'Posse de Bola (%)', 'efficiency': 'Eficiência (Gols/Chutes)'},
        color='team',
        color_discrete_sequence=px.colors.qualitative.Set2,
        size='shots',
        size_max=15
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        xaxis_title='Posse de Bola (%)',
        yaxis_title='Eficiência (Gols/Chutes)',
        yaxis=dict(range=[0, 1]),
    )

    st.plotly_chart(fig)






def plot_team_formations():
    st.title("Formação dos Times")

    # Definir as posições padrão no campo
    position_mapping = {
        "Goalkeeper": (2, 40),
        "Right Back": (15, 15),
        "Right Center Back": (15, 30),
        "Center Back": (15, 40),
        "Left Center Back": (15, 50),
        "Left Back": (15, 65),
        "Right Wing Back": (30, 10),
        "Left Wing Back": (30, 70),
        "Right Defensive Midfield": (35, 30),
        "Center Defensive Midfield": (35, 40),
        "Left Defensive Midfield": (35, 50),
        "Right Center Midfield": (45, 30),
        "Center Midfield": (45, 40),
        "Left Center Midfield": (45, 50),
        "Right Attacking Midfield": (60, 30),
        "Center Attacking Midfield": (60, 40),
        "Left Attacking Midfield": (60, 50),
        "Right Wing": (70, 15),
        "Left Wing": (70, 65),
        "Right Center Forward": (80, 30),
        "Center Forward": (80, 40),
        "Left Center Forward": (80, 50),
        "Secondary Striker": (75, 40),
        "Right Midfield": (50, 20),
        "Left Midfield": (50, 60),
        "Sweeper": (10, 40),
        "Right Forward": (75, 25),
        "Left Forward": (75, 55)
    }

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)

    # Extrair dados táticos
    tactics_data = events[events['tactics'].notnull()][['team', 'tactics']]
    formations = {}

    # Extrair a formação e as posições dos jogadores para ambos os times
    for index, row in tactics_data.iterrows():
        team = row['team']
        formation = row['tactics']['formation']
        player_numbers = []
        player_positions = []
        player_info = []
        
        for player in row['tactics']['lineup']:
            player_numbers.append(player['jersey_number'])
            position_name = player['position']['name']
            player_positions.append(position_mapping.get(position_name, (50, 40)))
            player_info.append({
                'number': player['jersey_number'],
                'name': player['player']['name'],
                'position': position_name
            })
        
        formations[team] = (formation, player_numbers, player_positions, player_info)

    # Criar um gráfico separado para cada time
    for team, (formation, player_numbers, player_positions, player_info) in formations.items():
        st.write(f"Formação do time: {team}")

        # Desenhar o campo usando Pitch
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        fig.set_facecolor('#0e1117')

        # Adicionar os jogadores ao campo
        for number, pos in zip(player_numbers, player_positions):
            ax.text(pos[0], pos[1], str(number), ha='center', va='center', fontsize=12,
                    color='white', bbox=dict(facecolor='#DA291C', edgecolor='white', boxstyle='circle,pad=0.5'))
        st.pyplot(fig)

        # Adicionar uma legenda com os nomes dos jogadores
        st.write("Legenda:")
        for player in player_info:
            st.write(f"{player['number']} - {player['name']} ({player['position']})")

        st.write("---")



def interatividade_eventos():
    st.subheader("Realize o filtro como preferir para realizar o download!")

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)

    # Extrair os jogadores únicos dos eventos, removendo NaN
    player_names = events['player'].dropna().unique()

    # Adicionar um seletor para escolher jogadores
    selected_players = st.multiselect("Selecione os jogadores", player_names)

    # Adicionar um seletor para escolher as colunas
    columns = events.columns.tolist()
    selected_columns = st.multiselect("Selecione as colunas que deseja visualizar", columns, default=columns)

    # Armazenar eventos filtrados
    filtered_events = pd.DataFrame()

    # Botão para filtrar eventos
    if st.button("Filtrar"):
        filtered_events = events[events['player'].isin(selected_players)]
        
        if not filtered_events.empty and selected_columns:
            filtered_events = filtered_events[selected_columns]
            st.write(f"Eventos para {', '.join(selected_players)}:")
            st.dataframe(filtered_events)
        else:
            st.write("Nenhum evento encontrado para os jogadores selecionados ou colunas não foram selecionadas.")

    # Botão para download
    if st.button("Preparar arquivo para download"):
        if not filtered_events.empty:
            with st.spinner("Preparando dados..."):
                time.sleep(5)
                csv = filtered_events.to_csv(index=False).encode('utf-8')

                # Exibir botão de download
                st.download_button(
                    label="Baixar eventos filtrados como CSV",
                    data=csv,
                    file_name='eventos_filtrados.csv',
                    mime='text/csv',
                    key="download_eventos"
                )


def mostrar_estatisticas_eventos():

    # Pegar os eventos da partida selecionada pelo usuário
    match_id = st.session_state['match_id_selecionada']
    events = sb.events(match_id=match_id)

    # Nem todos as partidas tem esse campo então setar em 0 caso não tenha
    if 'bad_behaviour_card' not in events.columns:
        events['bad_behaviour_card'] = 0
    team1, team2 = events['team'].unique()

    # Função para calcular as estatísticas
    def calcular_estatisticas(team):
        team_events = events[events['team'] == team]

        # Contar os passes e chutes
        total_passes = len(team_events[team_events['type'] == 'Pass'])
        total_shots = len(team_events[team_events['type'] == 'Shot'])
        
        # Contar cartões
        yellow_cards = len(team_events[team_events['bad_behaviour_card'] == 'Yellow Card'])
        red_cards = len(team_events[team_events['bad_behaviour_card'] == 'Red Card'])

        return total_passes, total_shots, yellow_cards, red_cards

    # Calcular para os dois times
    stats_team1 = calcular_estatisticas(team1)
    stats_team2 = calcular_estatisticas(team2)

    # Função para exibir métricas com cor personalizada para os cartões
    def mostrar_metricas_com_cores(team_name, stats):
        st.subheader(f"Estatísticas do {team_name}")

        # Exibir Total de Passes e Chutes com cor padrão
        st.metric(label="Total de Passes", value=stats[0])
        st.metric(label="Total de Chutes", value=stats[1])

        # Exibir Cartões Amarelos com fundo amarelo
        yellow_style = "background-color:yellow; color:black; padding:5px; border-radius:5px;" if stats[2] > 0 else ""
        st.markdown(f"<div style='{yellow_style}'>Cartões Amarelos: {stats[2]}</div>", unsafe_allow_html=True)

        # Exibir Cartões Vermelhos com fundo vermelho
        red_style = "background-color:red; color:black; padding:5px; border-radius:5px;" if stats[3] > 0 else ""
        st.markdown(f"<div style='{red_style}'>Cartões Vermelhos: {stats[3]}</div>", unsafe_allow_html=True)

    # Exibir as métricas
    mostrar_metricas_com_cores(team1, stats_team1)
    mostrar_metricas_com_cores(team2, stats_team2)



    
########################################################### EXIBIÇÃO ##############################################################




#Função referente a página inicial
def pagina_home():
    pagina_inicial()


#Função referente a página dos dados da partida selecionada
def pagina_metricas():
    st.title("Métricas da partida selecionada")

    metricas_dados_usuario()
    mostrar_estatisticas_eventos()
    plot_team_formations()
    posse_de_bola()
    tipos_passes()
    mapa_passes()
    mapa_chutes()
    chutes_durante_jogo()
    posse_de_bola_vs_eficiencia()
    exibir_df_init()


#Função referente a página de downloads
def pagina_download():
    st.title("Download dos arquivos utilizados")
    interatividade_eventos()

#Função principal que chama as páginas
def Main():
    st.sidebar.title("Menu principal")
    if "pagina_selecionada" not in st.session_state:
        st.session_state["pagina_selecionada"] = "Página Inicial"

    if st.sidebar.button("Página Inicial"):
        st.session_state["pagina_selecionada"] = "Página Inicial"

    if st.sidebar.button("Dados da partida"):
        st.session_state["pagina_selecionada"] = "Dados da partida"

    if st.sidebar.button("Download arquivos"):
        st.session_state["pagina_selecionada"] = "Download arquivos"

    if st.session_state["pagina_selecionada"] == "Página Inicial":
        pagina_home()
    elif st.session_state["pagina_selecionada"] == "Dados da partida":
        pagina_metricas()
    elif st.session_state["pagina_selecionada"] == "Download arquivos":
        pagina_download()

if __name__ == "__main__":
    Main()