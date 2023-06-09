from extended_choices import Choices

ADMINISTRATIVE_LEVEL_TYPE = Choices(
    ("DÉPARTEMENT", "département", "Département"),
    ("COMMUNE", "commune", "Commune"),
    ("ARRONDISSEMENT", "arrondissement", "Arrondissement"),
    ("VILLAGE", "village", "Village"),
)
