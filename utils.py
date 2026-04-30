import json
import os
from datetime import datetime, timedelta

def carregar_json(arquivo):
    if not os.path.exists(arquivo):
        with open(arquivo, 'w') as f:
            json.dump({} if arquivo not in ["fila_mediadores.json"] else [], f)
    with open(arquivo, 'r') as f:
        return json.load(f)

def salvar_json(arquivo, dados):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=4)

def add_pontos_ranking(user_id, pontos):
    ranking = carregar_json("ranking.json")
    user_id = str(user_id)
    if user_id not in ranking:
        ranking[user_id] = {
            "geral": 0, "semanal": 0, "mensal": 0, 
            "vitorias": 0, "derrotas": 0, 
            "ultimo_reset_semanal": str(datetime.now()), 
            "ultimo_reset_mensal": str(datetime.now())
        }

    ultimo_semanal = datetime.fromisoformat(ranking[user_id]["ultimo_reset_semanal"])
    if datetime.now() - ultimo_semanal > timedelta(days=7):
        ranking[user_id]["semanal"] = 0
        ranking[user_id]["ultimo_reset_semanal"] = str(datetime.now())

    ultimo_mensal = datetime.fromisoformat(ranking[user_id]["ultimo_reset_mensal"])
    if datetime.now() - ultimo_mensal > timedelta(days=30):
        ranking[user_id]["mensal"] = 0
        ranking[user_id]["ultimo_reset_mensal"] = str(datetime.now())

    ranking[user_id]["geral"] += pontos
    ranking[user_id]["semanal"] += pontos if pontos > 0 else 0
    ranking[user_id]["mensal"] += pontos if pontos > 0 else 0
    
    if pontos > 0:
        ranking[user_id]["vitorias"] += 1
    else:
        ranking[user_id]["derrotas"] += 1
    
    salvar_json("ranking.json", ranking)

def tem_cargo_suporte(member, CARGOS_SUPORTE):
    import discord
    return any(discord.utils.get(member.guild.roles, name=cargo) in member.roles for cargo in CARGOS_SUPORTE)
