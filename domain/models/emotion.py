from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Tuple

class Emotion(Enum):
    FRISSON = "frisson"
    ADRENALINE = "adrenaline"
    EMERVEILLEMENT = "emerveillement"
    RIRE = "rire"
    ROMANTISME = "romantisme"
    MELANCOLIE = "melancolie"
    REFLEXION = "reflexion"
    NOSTALGIE = "nostalgie"


@dataclass(frozen=True)
class EmotionGenres:
    core: List[int]       # le film doit avoir AU MOINS UN de ces genres pour entrer dans le pool
    secondary: List[int]  # bonus de score, ne suffit pas à entrer dans le pool
    excluded: List[int]   # un seul de ces genres → film retiré du pool
    excluded_unless: List[int] = field(default_factory=list)  # ces genres annulent l'exclusion (ex. un film d'horreur reste un frisson même avec de l'action)

    def matches(self, genres: Set[int]) -> bool:
        has_core = bool(genres & set(self.core))
        is_excluded = bool(genres & set(self.excluded)) and not genres & set(self.excluded_unless)
        return has_core and not is_excluded

    def affinity(self, genres: Set[int]) -> Tuple[int, int]:
        # (score pondéré, nb de genres principaux en commun) — sert à départager pour le filet de sécurité
        n_core = len(genres & set(self.core))
        n_secondary = len(genres & set(self.secondary))
        return (2 * n_core + n_secondary, n_core)


# d'une émotion de ton (sinon Bambi / Le Roi Lion sortent dans "Rire").
EMOTION_GENRES: Dict[Emotion, EmotionGenres] = {
    # TMDB met "Thriller" sur presque tous les films d'action : on exclut Action/Aventure
    # (Mad Max, Jurassic World…) sauf si le film est aussi un film d'horreur (Alien, World War Z).
    Emotion.FRISSON: EmotionGenres(
        core=[27, 9648, 53],                 # Horreur, Mystère, Thriller
        secondary=[80, 878],                 # Crime, Science-Fiction
        excluded=[35, 10751, 16, 12, 28, 10749],  # Comédie, Familial, Animation, Aventure, Action, Romance
        excluded_unless=[27]),               # Horreur
    # Aventure en secondaire seulement : sinon les films familiaux (Minions) et contemplatifs entrent.
    Emotion.ADRENALINE: EmotionGenres(
        core=[28],                           # Action
        secondary=[12, 53, 878, 10752, 37],  # Aventure, Thriller, Science-Fiction, Guerre, Western
        excluded=[99, 10749, 16, 10751]),    # Documentaire, Romance, Animation, Familial
    Emotion.EMERVEILLEMENT: EmotionGenres(
        core=[14, 878],                      # Fantastique, Science-Fiction
        secondary=[12, 16, 10751],           # Aventure, Animation, Familial
        excluded=[27, 53]),                  # Horreur, Thriller
    Emotion.RIRE: EmotionGenres(
        core=[35],                           # Comédie
        secondary=[10751, 16],               # Familial, Animation
        excluded=[27, 10752, 53]),           # Horreur, Guerre, Thriller
    Emotion.ROMANTISME: EmotionGenres(
        core=[10749],                        # Romance
        secondary=[35, 10402, 18],           # Comédie, Musique, Drame
        excluded=[27, 10752]),               # Horreur, Guerre
    # Pas de Guerre/Histoire en secondaire : sinon Mélancolie devient "cinéma de guerre".
    Emotion.MELANCOLIE: EmotionGenres(
        core=[18],                           # Drame
        secondary=[10402, 10749],            # Musique, Romance
        excluded=[35, 28, 27, 10751, 53, 12]),  # Comédie, Action, Horreur, Familial, Thriller, Aventure
    Emotion.REFLEXION: EmotionGenres(
        core=[99, 36, 9648],                 # Documentaire, Histoire, Mystère
        secondary=[18, 878],                 # Drame, Science-Fiction
        excluded=[35, 28, 10751, 16, 27]),   # Comédie, Action, Familial, Animation, Horreur
    Emotion.NOSTALGIE: EmotionGenres(
        core=[10751, 37, 10402, 16],         # Familial, Western, Musique, Animation
        secondary=[12, 35, 36],              # Aventure, Comédie, Histoire
        excluded=[27, 53]),                  # Horreur, Thriller
}


def emotions_of(genres: Set[int]) -> List[Emotion]:
    # Émotions d'un film. Filet de sécurité : un film qui ne passe la règle d'aucune émotion
    # est rattaché à celle dont il partage le plus de genres → tout film avec un genre a une émotion.
    matched = [emotion for emotion, emotion_genres in EMOTION_GENRES.items() if emotion_genres.matches(genres)]
    if matched or not genres:
        return matched
    best = max(EMOTION_GENRES, key=lambda emotion: EMOTION_GENRES[emotion].affinity(genres))
    return [best] if EMOTION_GENRES[best].affinity(genres)[0] > 0 else []
