import random

# Defina uma semente para tornar a simulacao reproduzivel
# A semente fixa facilita os testes e depuracao.
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
from utils import build_deck, draw_card, WEAPON_RANGES, CHARACTER_PERKS, CHARACTERS
from targeting import select_target

DYNAMITE_EXPLOSION_PROB = 8 / 52


def get_roles(players_count):
    """Return a shuffled list of roles for the game."""
    if players_count < 3:
        raise ValueError("O jogo requer no mínimo 3 jogadores.")
    if players_count > 7:
        raise ValueError("O jogo suporta no máximo 7 jogadores.")
    roles = ["Sheriff"] + ["Outlaw"] * (players_count - 2) + ["Renegade"]
    random.shuffle(roles)
    return roles


def generate_setup(fixed_character, fixed_role, players_count):
    """Gera personagens e funcoes com um personagem fixo em determinada funcao."""
    remaining_roles = ["Sheriff"] + ["Outlaw"] * (players_count - 2) + ["Renegade"]
    remaining_roles.remove(fixed_role)
    random.shuffle(remaining_roles)
    roles = [fixed_role] + remaining_roles

    remaining_characters = [c for c in CHARACTERS if c != fixed_character]
    characters = [fixed_character] + random.sample(remaining_characters, players_count - 1)
    return characters, roles


def compute_probability_matrix(players_count=4, games_per_combo=50):
    """Executa simulacoes em paralelo para gerar matriz de vitorias e derrotas."""
    import threading
    import pandas as pd

    outcomes = {
        (char, role): {"wins": 0, "losses": 0}
        for char in CHARACTERS
        for role in ["Sheriff", "Outlaw", "Renegade"]
    }
    lock = threading.Lock()

    def worker(character, role):
        wins = 0
        for _ in range(games_per_combo):
            chars, roles = generate_setup(character, role, players_count)
            result, players = simulate_game(players_count, chars, roles=roles)
            target_team = role if role != "Outlaw" else "Outlaws"
            if result == target_team:
                wins += 1
        with lock:
            outcomes[(character, role)]["wins"] += wins
            outcomes[(character, role)]["losses"] += games_per_combo - wins

    threads = []
    for character in CHARACTERS:
        for role in ["Sheriff", "Outlaw", "Renegade"]:
            t = threading.Thread(target=worker, args=(character, role))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    matrix_rows = []
    for (char, role), data in outcomes.items():
        total = data["wins"] + data["losses"]
        win_rate = data["wins"] / total * 100 if total else 0
        loss_rate = data["losses"] / total * 100 if total else 0
        matrix_rows.append({
            "Character": char,
            "Role": role,
            "Win %": win_rate,
            "Loss %": loss_rate,
        })

    df = pd.DataFrame(matrix_rows)
    return df.sort_values(["Character", "Role"]).reset_index(drop=True)


def compute_statistics(players_count=4, games=500):
    """Executa multiplas partidas para gerar estatisticas agregadas."""
    import pandas as pd

    results_roles = {"Sheriff": 0, "Outlaws": 0, "Renegade": 0, "Draw": 0}
    results_details = {}

    for _ in range(games):
        winner, players = simulate_game(players_count)
        results_roles[winner] += 1

        if winner != "Draw":
            for p in players:
                if winner == "Outlaws" and p["role"] != "Outlaw":
                    continue
                if winner == "Sheriff" and p["role"] != "Sheriff":
                    continue
                if winner == "Renegade" and p["role"] != "Renegade":
                    continue
                key = (p["character"], p["role"])
                results_details[key] = results_details.get(key, 0) + 1

    df_roles = pd.DataFrame.from_dict(results_roles, orient="index", columns=["Wins"])
    df_roles["Win Rate (%)"] = df_roles["Wins"] / games * 100
    df_roles.index.name = "Role"
    df_roles = df_roles.reset_index()

    details_rows = [
        {"Character": k[0], "Role": k[1], "Win Rate (%)": v / games * 100}
        for k, v in results_details.items()
    ]
    df_details = pd.DataFrame(details_rows)
    if not df_details.empty:
        df_details = (
            df_details.pivot_table(index="Character", columns="Role", values="Win Rate (%)")
            .reset_index()
            .fillna(0)
        )

    prob = compute_probability_matrix(players_count, games_per_combo=50)
    prob = prob.pivot_table(index="Character", columns="Role", values=["Win %", "Loss %"])
    prob.columns = [f"{stat} {role}" for stat, role in prob.columns]
    prob = prob.reset_index().fillna(0)

    return {
        "role_stats": df_roles.to_dict(orient="records"),
        "role_character_stats": df_details.to_dict(orient="records") if not df_details.empty else [],
        "probability_matrix": prob.to_dict(orient="records"),
    }

def simulate_game(players_count=4, characters=None, rounds=500, roles=None, return_log=False):
    """Simula uma partida e retorna o time vencedor e os jogadores.

    Quando ``return_log`` é ``True`` uma lista de eventos da partida é
    retornada como terceiro elemento da tupla.
    """

    log = [] if return_log else None

    roles = roles if roles is not None else get_roles(players_count)
    if len(roles) != players_count:
        raise ValueError("Numero de funcoes diferente do numero de jogadores.")

    if characters is not None:
        if len(characters) != players_count:
            raise ValueError("Quantidade de personagens diferente do numero de jogadores.")
        for c in characters:
            if c not in CHARACTERS:
                raise ValueError(f"Personagem invalido: {c}")
    else:
        characters = random.sample(CHARACTERS, players_count)

    players = []
    for i in range(players_count):
        base_hp = 5 if roles[i] == "Sheriff" else 4
        p = {
            "id": i,
            "role": roles[i],
            "character": characters[i],
            "hp": base_hp,
            "max_hp": base_hp,
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
            if return_log:
                log.append(f"Rodada {round_ + 1} - turno de {player['character']}")

            # habilidades no inicio do turno
            CHARACTER_PERKS[player["character"]](player, "turn_start", discard=discard)

            # Dynamite
            if dynamite_owner == player:
                if random.random() < DYNAMITE_EXPLOSION_PROB:
                    for _ in range(3):
                        player["hp"] -= 1
                        CHARACTER_PERKS[player["character"]](player, "damaged", deck=deck, discard=discard)
                        if player["hp"] <= 0:
                            player["alive"] = False
                            break
                    dynamite_owner = None

            # Compra
            handled = CHARACTER_PERKS[player["character"]](
                player,
                "draw_phase",
                players=players,
                deck=deck,
                discard=discard,
            )
            draw_cards = 2
            if handled:
                if handled == "skip":
                    draw_cards = 0
                else:
                    draw_cards -= 1
            for _ in range(draw_cards):
                if player["character"] == "Lucky Duke":
                    CHARACTER_PERKS[player["character"]](player, "draw", deck=deck, discard=discard)
                else:
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
            if player.get("unlimited_bang"):
                shots = player["hand"].count("BANG")
                if player.get("can_use_missed_as_bang"):
                    shots += player["hand"].count("MISSED")
            for _ in range(shots):
                if "BANG" in player["hand"]:
                    use_card = "BANG"
                elif player.get("can_use_missed_as_bang") and "MISSED" in player["hand"]:
                    use_card = "MISSED"
                else:
                    break

                target = select_target(player, players)
                if not target:
                    continue
                if return_log:
                    log.append(f"{player['character']} atacou {target['character']}")
                player["hand"].remove(use_card)
                discard.append(use_card)

                misses_needed = 2 if player["character"] == "Slab the Killer" else 1
                used_misses = 0
                while used_misses < misses_needed:
                    if "MISSED" in target["hand"]:
                        target["hand"].remove("MISSED")
                        discard.append("MISSED")
                        used_misses += 1
                    elif target.get("can_use_bang_as_missed") and "BANG" in target["hand"]:
                        target["hand"].remove("BANG")
                        discard.append("BANG")
                        used_misses += 1
                    else:
                        break

                if used_misses < misses_needed:
                    target["hp"] -= 1
                    if return_log:
                        log.append(
                            f"{target['character']} perdeu 1 de vida (hp={target['hp']})"
                        )
                    if target["character"] == "Bart Cassidy":
                        CHARACTER_PERKS[target["character"]](target, "damaged", deck=deck, discard=discard)
                    if target["character"] == "El Gringo":
                        CHARACTER_PERKS[target["character"]](target, "damaged_by_player", attacker=player)
                    if target["hp"] <= 0:
                        target["alive"] = False
                        if return_log:
                            log.append(f"{target['character']} morreu")

            # Limite de cartas
            while len(player["hand"]) > player["hp"]:
                discard.append(player["hand"].pop())

            CHARACTER_PERKS[player["character"]](
                player, "turn_end", deck=deck, discard=discard
            )

        # Verificação de vitória
        sheriff_alive = any(p["role"] == "Sheriff" and p["alive"] for p in players)
        outlaws_alive = any(p["role"] == "Outlaw" and p["alive"] for p in players)
        renegade_alive = any(p["role"] == "Renegade" and p["alive"] for p in players)

        winner = None
        if not sheriff_alive and not outlaws_alive and renegade_alive:
            winner = "Renegade"
        elif sheriff_alive and not outlaws_alive and not renegade_alive:
            winner = "Sheriff"
        elif not sheriff_alive and outlaws_alive:
            winner = "Outlaws"

        if winner:
            if return_log:
                log.append(f"Vencedor: {winner}")
                return winner, players, log
            return winner, players

    if return_log:
        log.append("Vencedor: Draw")
        return "Draw", players, log

    return "Draw", players

if __name__ == "__main__":
    import pandas as pd
    total_games = 5000
    players_count = int(input("Numero de jogadores (3-7): "))
    if not 3 <= players_count <= 7:
        raise ValueError("Numero de jogadores deve estar entre 3 e 7.")
    print("Personagens disponiveis:")
    print(", ".join(CHARACTERS))
    chars_input = input(
        "Digite os personagens separados por virgula ou pressione Enter para aleatorio: "
    ).strip()
    if chars_input:
        selected_characters = [c.strip() for c in chars_input.split(',')]
    else:
        selected_characters = None

    results_roles = {"Sheriff": 0, "Outlaws": 0, "Renegade": 0, "Draw": 0}
    results_details = {}

    for _ in range(total_games):
        winner, players = simulate_game(players_count, selected_characters)
        results_roles[winner] += 1

        if winner != "Draw":
            for p in players:
                if winner == "Outlaws" and p["role"] != "Outlaw":
                    continue
                if winner == "Sheriff" and p["role"] != "Sheriff":
                    continue
                if winner == "Renegade" and p["role"] != "Renegade":
                    continue
                key = (p["role"], p["character"])
                results_details[key] = results_details.get(key, 0) + 1

    df_roles = pd.DataFrame.from_dict(results_roles, orient="index", columns=["Wins"])
    df_roles["Win Rate (%)"] = df_roles["Wins"] / total_games * 100

    details_rows = [
        {"Role": k[0], "Character": k[1], "Wins": v, "Win Rate (%)": v / total_games * 100}
        for k, v in results_details.items()
    ]
    df_details = pd.DataFrame(details_rows)

    print("\nEstatisticas por funcao:")
    print(df_roles)
    print("\nEstatisticas por funcao e personagem:")
    if not df_details.empty:
        print(df_details.sort_values(["Role", "Character"]).to_string(index=False))
    else:
        print("Nenhum dado disponivel")

    print("\nMatriz de probabilidades (personagem x funcao):")
    matrix = compute_probability_matrix(players_count, games_per_combo=50)
    print(matrix.to_string(index=False))
