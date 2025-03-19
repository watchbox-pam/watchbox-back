from enum import Enum
from typing import List, Dict

class Emotion(Enum):
    FRISSON = "frisson"
    EXCITATION = "excitation"
    EMERVEILLEMENT = "emerveillement"
    RIRE = "rire"
    ROMANTISME = "romantisme"
    MELANCOLIE = "melancolie"
    REFLEXION = "reflexion"
    NOSTALGIE = "nostalgie"

EMOTION_GENRE_MAPPING: Dict[Emotion, List[int]] = {
    Emotion.FRISSON: [27, 53, 80, 9648, 878],  # Horreur, Thriller, Crime, Mystère, Science-Fiction
    Emotion.EXCITATION: [12, 28, 10752, 37, 878, 53],  # Aventure, Action, Guerre, Western, Science-Fiction, Thriller
    Emotion.EMERVEILLEMENT: [14, 878, 16, 12, 99],  # Fantastique, Science-Fiction, Animation, Aventure, Documentaire
    Emotion.RIRE: [35, 16, 10751, 10770],  # Comédie, Animation, Familial, Téléfilm
    Emotion.ROMANTISME: [10749, 18, 10402],  # Romance, Drame, Musique
    Emotion.MELANCOLIE: [18, 10752, 10402, 36],  # Drame, Guerre, Musique, Histoire
    Emotion.REFLEXION: [99, 18, 9648, 36, 878, 80],  # Documentaire, Drame, Mystère, Histoire, Science-Fiction, Crime
    Emotion.NOSTALGIE: [36, 10751, 37, 10402, 16, 10770]  # Histoire, Familial, Western, Musique, Animation, Téléfilm
}
