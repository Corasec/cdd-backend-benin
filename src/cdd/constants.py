from extended_choices import Choices

ADMINISTRATIVE_LEVEL_TYPE = Choices(
    ("DÉPARTEMENT", "département", "Département"),
    ("COMMUNE", "commune", "Commune"),
    ("ARRONDISSEMENT", "arrondissement", "Arrondissement"),
    ("VILLAGE", "village", "Village"),
)

PROJECT_STRUCTURE = {"phase": "phase", "activity": "étape", "task": "tâche"}

AGENT_ROLE = Choices(
    ("ACSDCC", "AC-SDCC", "Assistant coordonnateur spécialiste du dcc"),
    ("FGB", "FGB", "Formateur en gestion à la base"),
    ("SC", "SC", "Superviseur communal"),
    ("FT", "FT", "Facilitateur technique"),
    ("FC", "FC", "Facilitateur communautaire"),
)
AGENT_ROLE_CH = (
    ("", ""),
    ("SC", "SC"),
    ("FC", "FC"),
    ("FGB", "FGB"),
    ("FT", "FT"),
    ("AC-SDCC", "AC-SDCC"),
)
FC_COVERAGE = ["village"]
SC_FT_COVERAGE = ["arrondissement"]

# set to 1 hour
AGENT_TASKS_COMPLETION_TIMEOUT = 3600
