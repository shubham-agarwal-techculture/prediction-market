import random
from django.utils import timezone


def generate_sports_outcome(event):
    entities = list(event.entities.all())
    if not entities:
        return {"result": "draw", "winner": None}

    team1, team2 = entities[0], entities[1] if len(entities) > 1 else None

    if team2:
        team1_strength = team1.current_state.get("strength", 50)
        team2_strength = team2.current_state.get("strength", 50)

        total_strength = team1_strength + team2_strength
        team1_prob = team1_strength / total_strength

        random_factor = random.random()
        if random_factor < team1_prob * 0.7:
            winner = team1.name
        elif random_factor < team1_prob * 0.7 + (1 - team1_prob) * 0.7:
            winner = team2.name
        else:
            winner = "draw"

        return {
            "result": winner,
            "winner": winner if winner != "draw" else None,
            "team1": team1.name,
            "team2": team2.name,
            "team1_score": random.randint(0, 5),
            "team2_score": random.randint(0, 5),
        }
    else:
        return {"result": team1.name, "winner": team1.name}


def generate_financial_outcome(event):
    entities = list(event.entities.all())
    if not entities:
        return {"result": "no_change", "percentage": 0}

    entity = entities[0]
    current_price = entity.current_state.get("price", 100)

    change_percent = random.uniform(-10, 10)
    new_price = current_price * (1 + change_percent / 100)

    if change_percent > 0:
        result = "up"
    elif change_percent < 0:
        result = "down"
    else:
        result = "no_change"

    return {
        "result": result,
        "previous_price": current_price,
        "new_price": round(new_price, 2),
        "percentage": round(change_percent, 2),
    }


def generate_random_outcome(event):
    random_type = event.description.lower() if event.description else ""

    if "coin" in random_type:
        result = random.choice(["heads", "tails"])
        return {"result": result, "type": "coin_flip"}
    elif "dice" in random_type:
        result = random.randint(1, 6)
        return {"result": result, "type": "dice_roll"}
    elif "number" in random_type:
        result = random.randint(1, 100)
        return {"result": result, "type": "random_number"}
    else:
        result = random.choice(["option_a", "option_b", "option_c"])
        return {"result": result, "type": "random_choice"}


def generate_custom_outcome(event):
    entities = list(event.entities.all())
    if entities:
        random_entity = random.choice(entities)
        return {
            "result": random_entity.name,
            "type": "custom_entity_selection",
            "entities": [e.name for e in entities],
        }
    else:
        return {"result": random.choice(["outcome_1", "outcome_2", "outcome_3"]), "type": "custom"}
