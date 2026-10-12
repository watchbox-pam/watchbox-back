class AdminError(Exception):
    """Erreur métier de l'administration, traduite en code HTTP par le router."""


class AdminNotFoundError(AdminError):
    """La ressource demandée n'existe pas (404)."""


class AdminConflictError(AdminError):
    """La ressource existe déjà ou entre en conflit (409)."""


class AdminValidationError(AdminError):
    """Les données envoyées sont invalides (400)."""


class AdminConfigurationError(AdminError):
    """Une configuration serveur est manquante (500)."""
