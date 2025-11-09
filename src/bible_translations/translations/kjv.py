from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class KJV(BibleGatewayTranslation):
    """
    King James Version backed by BibleGateway scraping.

    Inherits all retrieval methods from BibleGatewayTranslation so that the
    scraping logic is shared across translations.
    """
    name = "King James Version"
    abbreviation = "KJV"
    copyright = "Public Domain"
