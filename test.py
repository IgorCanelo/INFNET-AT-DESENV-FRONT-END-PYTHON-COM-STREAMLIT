from statsbombpy import sb

competicoes = sb.competitions()

# Exibir todas as competições disponíveis
print(competicoes[['competition_id', 'competition_name']])