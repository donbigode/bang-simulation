import random

# Defina uma semente para tornar a simulacao reproduzivel
# A semente fixa facilita os testes e depuracao.
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
import pandas as pd
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

def simulate_game(players_count=4, characters=None, rounds=500, roles=None):
    """Simula uma partida e retorna o time vencedor e os jogadores."""

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
            return "Renegade", players
        elif sheriff_alive and not outlaws_alive and not renegade_alive:
            return "Sheriff", players
        elif not sheriff_alive and outlaws_alive:
            return "Outlaws", players

    return "Draw", players

if __name__ == "__main__":
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
