class InvalidExternalTokenError(Exception):
    """Le jeton Google / Apple est invalide, expiré, ou n'a pas été émis pour Watchbox."""


class ExternalAuthUnavailableError(Exception):
    """Impossible de vérifier le jeton : configuration manquante ou serveurs du fournisseur injoignables."""


class InvalidRegistrationTokenError(Exception):
    """Le jeton d'inscription temporaire est invalide ou a expiré."""


class AccountConflictError(Exception):
    """Le pseudo, l'adresse mail ou le compte externe est déjà utilisé."""
