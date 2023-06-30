from extended_choices import Choices

ADMINISTRATIVE_LEVEL_TYPE = Choices(
    ("DÉPARTEMENT", "département", "Département"),
    ("COMMUNE", "commune", "Commune"),
    ("ARRONDISSEMENT", "arrondissement", "Arrondissement"),
    ("VILLAGE", "village", "Village"),
)

AGENT_ROLE = Choices(
    ("ACSDCC", "AC-SDCC", "Assistant coordonnateur spécialiste du dcc"),
    ("FGB", "FGB", "Formateur en gestion à la base"),
    ("SC", "SC", "Superviseur communal"),
    ("FT", "FT", "Facilitateur technique"),
    ("FC", "FC", "Facilitateur communautaire"),
)
