import random

DECK_COUNTS = {
    "BANG": 25,
    "MISSED": 12,
    "BEER": 6,
    "INDIANS": 2,
    "GATLING": 1,
    "STAGECOACH": 4,
    "WELLSFARGO": 3,
    "DYNAMITE": 1,
    "VOLCANIC": 1,
    "SCHOFIELD": 3,
    "REMINGTON": 2,
    "REV.CARABINE": 1,
    "WINCHESTER": 1,
    "MUSTANG": 2,
    "SCOPE": 1
}

WEAPON_RANGES = {
    "VOLCANIC": {"range": 1, "multi_shot": True},
    "SCHOFIELD": {"range": 2, "multi_shot": False},
    "REMINGTON": {"range": 3, "multi_shot": False},
    "REV.CARABINE": {"range": 4, "multi_shot": False},
    "WINCHESTER": {"range": 5, "multi_shot": False},
}

CHARACTER_PERKS = {
    "Bart Cassidy": lambda p, e: p.update({"hp": p["hp"] + 1}) if e == "damaged" and p["hp"] < 4 else None,
    "Calamity Janet": lambda p, e: p.update({"can_use_missed_as_bang": True}) if e == "start" else None,
    "Jesse Jones": lambda p, e: None,
    "Lucky Duke": lambda p, e: None,
    "Paul Regret": lambda p, e: p.update({"dodge_bonus": 1}) if e == "start" else None,
    "Sid Ketchum": lambda p, e: None,
    "Slab the Killer": lambda p, e: None,
    "Suzy Lafayette": lambda p, e: None,
    "Willy the Kid": lambda p, e: p.update({"bonus_shot": 1}) if e == "start" else None,
    "El Gringo": lambda p, e: None,
    "Pedro Ramirez": lambda p, e: None,
    "Kit Carlson": lambda p, e: None,
    "Rose Doolan": lambda p, e: p.update({"range_bonus": 1}) if e == "start" else None,
    "Black Jack": lambda p, e: None
}

CHARACTERS = list(CHARACTER_PERKS.keys())

def build_deck():
    deck = []
    for card, count in DECK_COUNTS.items():
        deck.extend([card] * count)
    random.shuffle(deck)
    return deck

def draw_card(deck, discard):
    if not deck:
        deck.extend(discard)
        discard.clear()
        random.shuffle(deck)
    return deck.pop() if deck else None
