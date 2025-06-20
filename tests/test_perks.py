import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import CHARACTER_PERKS, draw_card


def test_bart_cassidy_draw_on_damage():
    deck = ["BANG"]
    discard = []
    player = {"hand": [], "hp": 3}
    CHARACTER_PERKS["Bart Cassidy"](player, "damaged", deck=deck, discard=discard)
    assert player["hand"] == ["BANG"]
    assert deck == []


def test_sid_ketchum_heal():
    player = {"hand": ["BANG", "MISSED", "BEER"], "hp": 2, "max_hp": 4}
    discard = []
    CHARACTER_PERKS["Sid Ketchum"](player, "turn_start", discard=discard)
    assert player["hp"] == 3
    assert len(player["hand"]) == 1
    assert len(discard) == 2


def test_suzy_lafayette_draw_when_empty():
    deck = ["BANG"]
    discard = []
    player = {"hand": []}
    CHARACTER_PERKS["Suzy Lafayette"](player, "turn_end", deck=deck, discard=discard)
    assert player["hand"] == ["BANG"]
    assert deck == []


def test_jesse_jones_steals_card():
    deck = ["BANG"]
    discard = []
    jesse = {"id": 0, "hand": [], "alive": True}
    victim = {"id": 1, "hand": ["MISSED"], "alive": True}
    taken = CHARACTER_PERKS["Jesse Jones"](
        jesse, "draw_phase", players=[jesse, victim], deck=deck, discard=discard
    )
    assert taken is True
    assert jesse["hand"] == ["MISSED"]
    assert victim["hand"] == []
