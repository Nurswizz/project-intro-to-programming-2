import random
from functools import wraps


def log_event(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, str):
            self._history.append(result)
        return result
    return wrapper


_EMPTY_EVENTS = [
    ("You move cautiously through the area. Nothing stirs.", 0),
    ("The wind howls, but no enemies are near.", 0),
    ("You find a safe hollow and catch your breath. (+5 HP)", 5),
    ("Embers of an old campfire still glow. You rest a moment. (+10 HP)", 10),
    ("A shadow passes overhead — but disappears.", 0),
    ("Distant growling fades into silence.", 0),
    ("You discover a trickle of a healing spring. (+8 HP)", 8),
]

_SPECIAL_MESSAGES = {
    "merchant": "The merchant winks and flips you a gold coin.",
    "shrine":   "Warm light washes over you — wounds knit closed.",
    "treasure": "The chest groans open, revealing glittering gold.",
    "training": "You work through the training dummies until your muscles burn.",
}


class EventSystem:
    def __init__(self):
        self._history: list[str] = []

    @log_event
    def trigger_empty_event(self) -> str:
        text, _ = random.choice(_EMPTY_EVENTS)
        return text

    def heal_from_empty_event(self, event_text: str) -> int:
        for text, hp in _EMPTY_EVENTS:
            if text == event_text:
                return hp
        return 0

    @log_event
    def trigger_special_message(self, event: dict) -> str:
        return _SPECIAL_MESSAGES.get(event.get("type", ""), "Something unusual happens.")

    def get_history(self) -> list[str]:
        return self._history[-10:]
