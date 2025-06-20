import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import CHARACTER_PERKS
from main import get_roles


def test_kit_carlson_handles_small_deck():
    deck = ["BANG"]
    player = {"hand": []}

    result = CHARACTER_PERKS["Kit Carlson"](player, "draw_phase", deck=deck)

    assert result == "skip"
    assert player["hand"] == ["BANG"]
    assert deck == []


def test_get_roles_rejects_more_than_seven_players():
    try:
        get_roles(8)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_get_roles_distribution():
    from collections import Counter

    assert Counter(get_roles(3)) == Counter({"Sheriff": 1, "Outlaw": 1, "Renegade": 1})
    assert Counter(get_roles(4)) == Counter({"Sheriff": 1, "Outlaw": 2, "Renegade": 1})
    assert Counter(get_roles(5)) == Counter({"Sheriff": 1, "Outlaw": 2, "Renegade": 1, "Deputy": 1})
    assert Counter(get_roles(6)) == Counter({"Sheriff": 1, "Outlaw": 3, "Renegade": 1, "Deputy": 1})
    assert Counter(get_roles(7)) == Counter({"Sheriff": 1, "Outlaw": 3, "Renegade": 1, "Deputy": 2})

