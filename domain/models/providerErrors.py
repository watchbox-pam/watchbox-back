class InvalidProviderError(Exception):
    """Un ou plusieurs ids ne correspondent à aucune plateforme de streaming disponible en France."""

    def __init__(self, unknown_ids: list[int]):
        self.unknown_ids = unknown_ids
        super().__init__(f"Plateformes inconnues : {', '.join(str(i) for i in unknown_ids)}")


class ProviderCatalogUnavailableError(Exception):
    """La liste des plateformes (TMDB) est momentanément indisponible."""
