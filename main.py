import random
import pandas as pd
from utils import build_deck, draw_card, WEAPON_RANGES, CHARACTER_PERKS, CHARACTERS
from targeting import select_target

DYNAMITE_EXPLOSION_PROB = 8 / 52

def simulate_game(players_count=4, rounds=500):
    assert players_count == 4, "Este script só suporta 4 jogadores por enquanto."

    roles = ["Sheriff", "Outlaw", "Outlaw", "Renegade"]
    random.shuffle(roles)
    characters = random.sample(CHARACTERS, players_count)

    players = []
    for i in range(players_count):
        p = {
            "id": i,
            "role": roles[i],
            "character": characters[i],
            "hp": 5 if roles[i] == "Sheriff" else 4,
            "alive": True,
            "hand": [],
            "weapon": "BASIC",
            "range_bonus": 0,
            "dodge_bonus": 0
        }
        CHARACTER_PERKS[characters[i]](p, "start")
        players.append(p)

    deck = build_deck()
    discard = []
    dynamite_owner = None

    for p in players:
        for _ in range(2):
            card = draw_card(deck, discard)
            if card:
                p["hand"].append(card)

    for round_ in range(rounds):
        for player in players:
            if not player["alive"]:
                continue

            # Dynamite
            if dynamite_owner == player:
                if random.random() < DYNAMITE_EXPLOSION_PROB:
                    player["hp"] -= 3
                    if player["hp"] <= 0:
                        player["alive"] = False
                    dynamite_owner = None

            # Compra
            for _ in range(2):
                card = draw_card(deck, discard)
                if card:
                    player["hand"].append(card)

            # Equipamento
            for card in player["hand"][:]:
                if card in WEAPON_RANGES:
                    player["weapon"] = card
                    player["hand"].remove(card)
                    discard.append(card)
                elif card == "SCOPE":
                    player["range_bonus"] += 1
                    player["hand"].remove(card)
                    discard.append(card)
                elif card == "MUSTANG":
                    player["dodge_bonus"] += 1
                    player["hand"].remove(card)
                    discard.append(card)

            # Beer
            if player["hp"] <= 2 and "BEER" in player["hand"]:
                player["hp"] += 1
                player["hand"].remove("BEER")
                discard.append("BEER")

            # Ataques
            shots = 2 if WEAPON_RANGES.get(player["weapon"], {}).get("multi_shot") else 1
            for _ in range(shots):
                if "BANG" not in player["hand"]:
                    break
                target = select_target(player, players)
                if not target:
                    continue
                player["hand"].remove("BANG")
                discard.append("BANG")
                if "MISSED" in target["hand"]:
                    target["hand"].remove("MISSED")
                    discard.append("MISSED")
                else:
                    target["hp"] -= 1
                    if target["hp"] <= 0:
                        target["alive"] = False

            # Limite de cartas
            while len(player["hand"]) > player["hp"]:
                discard.append(player["hand"].pop())

        # Verificação de vitória
        sheriff_alive = any(p["role"] == "Sheriff" and p["alive"] for p in players)
        outlaws_alive = any(p["role"] == "Outlaw" and p["alive"] for p in players)
        renegade_alive = any(p["role"] == "Renegade" and p["alive"] for p in players)

        if not sheriff_alive and not outlaws_alive and renegade_alive:
            return "Renegade"
        elif sheriff_alive and not outlaws_alive and not renegade_alive:
            return "Sheriff"
        elif not sheriff_alive and outlaws_alive:
            return "Outlaws"

    return "Draw"

if __name__ == "__main__":
    results = {"Sheriff": 0, "Outlaws": 0, "Renegade": 0, "Draw": 0}
    for _ in range(5000):
        res = simulate_game()
        results[res] += 1
    df = pd.DataFrame.from_dict(results, orient="index", columns=["Wins"])
    df["Win Rate (%)"] = df["Wins"] / 50
    print(df)
