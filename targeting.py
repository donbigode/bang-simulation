import random
from utils import WEAPON_RANGES

def select_target(player, players):
    weapon = player.get("weapon", "BASIC")
    weapon_range = WEAPON_RANGES.get(weapon, {}).get("range", 1)
    total_range = weapon_range + player.get("range_bonus", 0)

    possible_targets = []
    for target in players:
        if target["id"] == player["id"] or not target["alive"]:
            continue
        distance = 1 + target.get("dodge_bonus", 0)
        if distance <= total_range:
            possible_targets.append(target)

    if player["role"] == "Outlaw":
        targets = [t for t in possible_targets if t["role"] == "Sheriff"]
        if not targets:
            targets = possible_targets
    elif player["role"] == "Sheriff":
        targets = [t for t in possible_targets if t["role"] not in ["Sheriff", "Deputy"]]
    elif player["role"] == "Renegade":
        outlaw_count = sum(1 for p in players if p["alive"] and p["role"] == "Outlaw")
        law_count = sum(1 for p in players if p["alive"] and p["role"] in ["Sheriff", "Deputy"])

        if outlaw_count > law_count:
            prefer_role = "Outlaw"
        else:
            prefer_role = "Sheriff"

        targets = [t for t in possible_targets if t["role"] == prefer_role]
        if not targets:
            targets = possible_targets
    else:
        targets = possible_targets

    return random.choice(targets) if targets else None
