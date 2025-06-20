import os
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from targeting import select_target


def make_player(player_id, role):
    return {
        "id": player_id,
        "role": role,
        "alive": True,
        "weapon": "BASIC",
        "range_bonus": 10,
        "dodge_bonus": 0,
        "hand": []
    }


def test_renegade_targets_majority():
    renegade = make_player(0, "Renegade")
    sheriff = make_player(1, "Sheriff")
    outlaw1 = make_player(2, "Outlaw")
    outlaw2 = make_player(3, "Outlaw")
    players = [renegade, sheriff, outlaw1, outlaw2]

    target = select_target(renegade, players)
    assert target["role"] == "Outlaw"

    outlaw1["alive"] = False
    target = select_target(renegade, players)
    assert target["role"] == "Sheriff"
