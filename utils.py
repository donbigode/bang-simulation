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

# ---------------------------------------------------------------------------
# Character abilities
# ---------------------------------------------------------------------------
def bart_cassidy(player, event, deck=None, discard=None, **_):
    """Draw a card every time he loses a life point."""
    if event == "damaged" and deck is not None:
        card = draw_card(deck, discard)
        if card:
            player["hand"].append(card)


def calamity_janet(player, event, **_):
    """BANG! and MISSED! cards are interchangeable."""
    if event == "start":
        player.update({"can_use_missed_as_bang": True, "can_use_bang_as_missed": True})


def jesse_jones(player, event, players=None, deck=None, discard=None, **_):
    """First draw can steal a random card from another player's hand."""
    if event == "draw_phase" and players is not None:
        others = [p for p in players if p["id"] != player["id"] and p["alive"] and p["hand"]]
        if others:
            target = random.choice(others)
            card = random.choice(target["hand"])
            target["hand"].remove(card)
            player["hand"].append(card)
            return True  # card taken
    return False


def lucky_duke(player, event, deck=None, discard=None, **_):
    """Draw two cards and choose one for each draw."""
    if event == "draw" and deck is not None:
        card1 = draw_card(deck, discard)
        card2 = draw_card(deck, discard)
        chosen = card1 if card2 is None else random.choice([card1, card2])
        extra = card2 if chosen is card1 else card1
        if chosen:
            player["hand"].append(chosen)
        if extra:
            discard.append(extra)
        return True
    return False


def paul_regret(player, event, **_):
    """Other players have -1 range when targeting him."""
    if event == "start":
        player["dodge_bonus"] = player.get("dodge_bonus", 0) + 1


def sid_ketchum(player, event, discard=None, **_):
    """May discard two cards at start of turn to regain 1 life."""
    if event == "turn_start" and discard is not None:
        while player["hp"] < player["max_hp"] and len(player["hand"]) >= 2:
            discard.append(player["hand"].pop())
            discard.append(player["hand"].pop())
            player["hp"] += 1


def slab_the_killer(player, event, **_):
    """Targets need two MISSED! cards to cancel his BANG!"""
    # handled in main during attack
    return None


def suzy_lafayette(player, event, deck=None, discard=None, **_):
    """Draw a card if she ends her turn with no cards in hand."""
    if event == "turn_end" and deck is not None and not player["hand"]:
        card = draw_card(deck, discard)
        if card:
            player["hand"].append(card)


def willy_the_kid(player, event, **_):
    """May play any number of BANG! cards."""
    if event == "start":
        player["unlimited_bang"] = True


def el_gringo(player, event, attacker=None, **_):
    """When hit by a player, steals a random card from the attacker."""
    if event == "damaged_by_player" and attacker and attacker["hand"]:
        card = random.choice(attacker["hand"])
        attacker["hand"].remove(card)
        player["hand"].append(card)


def pedro_ramirez(player, event, discard=None, **_):
    """May draw the first card from discard instead of deck."""
    if event == "draw_phase" and discard:
        player["hand"].append(discard.pop())
        return True
    return False


def kit_carlson(player, event, deck=None, **_):
    """Looks at the top three cards and chooses two."""
    if event == "draw_phase" and deck is not None:
        cards = [draw_card(deck, []) for _ in range(3)]
        available = [c for c in cards if c]
        keep = random.sample(available, k=min(2, len(available)))
        for card in keep:
            player["hand"].append(card)
        for card in cards:
            if card and card not in keep:
                deck.append(card)
        return "skip"
    return False


def rose_doolan(player, event, **_):
    """Has +1 range."""
    if event == "start":
        player["range_bonus"] = player.get("range_bonus", 0) + 1


def black_jack(player, event, deck=None, discard=None, **_):
    """If lucky, draws an extra card."""
    if event == "draw_phase" and deck is not None:
        # draw two normal cards first
        for _ in range(2):
            card = draw_card(deck, discard)
            if card:
                player["hand"].append(card)
        if random.random() < 0.5:
            card = draw_card(deck, discard)
            if card:
                player["hand"].append(card)
        return "skip"
    return False


CHARACTER_PERKS = {
    "Bart Cassidy": bart_cassidy,
    "Calamity Janet": calamity_janet,
    "Jesse Jones": jesse_jones,
    "Lucky Duke": lucky_duke,
    "Paul Regret": paul_regret,
    "Sid Ketchum": sid_ketchum,
    "Slab the Killer": slab_the_killer,
    "Suzy Lafayette": suzy_lafayette,
    "Willy the Kid": willy_the_kid,
    "El Gringo": el_gringo,
    "Pedro Ramirez": pedro_ramirez,
    "Kit Carlson": kit_carlson,
    "Rose Doolan": rose_doolan,
    "Black Jack": black_jack,
}

CHARACTER_ABILITY_DESCRIPTIONS = {
    name: func.__doc__.strip() if func.__doc__ else ""
    for name, func in CHARACTER_PERKS.items()
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
