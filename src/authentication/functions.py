import logging
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from administrativelevels.models import AdministrativeLevel
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from authentication.models import Facilitator
from no_sql_client import NoSQLClient
from dashboard.utils import get_administrative_levels_by_level_and_name
from cdd.constants import ADMINISTRATIVE_LEVEL_TYPE
import json

# from sys import platform
# from datetime import datetime
import pandas as pd


def conversion_file_csv_to_dict(file_csv, sheet="Sheet1") -> dict:
    read_file = pd.read_csv(file_csv, sheet)
    # datas = read_file.to_dict()

    return read_file


def conversion_file_xlsx_to_dict(file_xlsx, sheet="Sheet1") -> dict:
    read_file = pd.read_excel(file_xlsx, sheet)
    # datas = read_file.to_dict()

    return read_file


def save_agents_sc_csv_datas_to_db(agent_file, sheet="SC") -> str:
    """Function to save agents from csv/excel file to the database"""
    # load file
    role = "SC"
    datas = {}
    try:
        datas = pd.read_excel(agent_file, sheet)
    except pd.errors.ParserError as exc:
        datas = pd.read_csv(agent_file, sheet)
    except Exception as exc:
        # messages.info(request, _("An error has occurred..."))
        print("Error while loading the file")

    logger = logging.getLogger(__name__)
    # control variables
    num_rows = datas.shape[0]
    saved_count = 0
    update_count = 0
    nsc = NoSQLClient()
    administrative_levels_db = nsc.get_db("administrative_levels")

    for index, row in datas.iterrows():
        # Split into words
        nom_words = row["NOM"].split()
        if len(nom_words) >= 2:
            username = f"{nom_words[0]}_{nom_words[1]}"
        else:
            username = f"{nom_words[0]}"

        facilitator, created = Facilitator.objects.get_or_create(
            username=username,
            defaults={
                "active": True,
                "role": role,
            },
        )
        departement = get_administrative_levels_by_level_and_name(
            administrative_levels_db,
            ADMINISTRATIVE_LEVEL_TYPE.DÉPARTEMENT,
            row["DÉPARTEMENT"],
        )
        departement = departement[0][0]
        commune = get_administrative_levels_by_level_and_name(
            administrative_levels_db, ADMINISTRATIVE_LEVEL_TYPE.COMMUNE, row["COMMUNE"]
        )
        commune = commune[0][0]
        arr = get_administrative_levels_by_level_and_name(
            administrative_levels_db,
            ADMINISTRATIVE_LEVEL_TYPE.ARRONDISSEMENT,
            row["ARRONDISSEMENT"],
        )
        arr = arr[0][0]
        doc_properties = {
            "name": row["NOM"],
            "email": "",
            "phone": row["CONTACT"],
            "sex": "M." if row["SEXE"] == "Masculin" else "Mme",
            "role": role,
            "administrative_levels": [
                {"name": departement["name"], "id": departement["administrative_id"]},
                {"name": commune["name"], "id": commune["administrative_id"]},
                {"name": arr["name"], "id": arr["administrative_id"]},
            ],
            "type": "facilitator",
        }

        facilitator_database = nsc.get_db(facilitator.no_sql_db_name)
        # If creating agent , create it couchdb doc
        if created:
            nsc.create_document(facilitator_database, doc_properties)
            print(f"created {facilitator.username}")
            saved_count += 1
        # if updating, update couchdb doc
        else:
            # get agent doc
            query_result = facilitator_database.get_query_result(
                {"type": "facilitator"}
            )[:]
            existing_doc = facilitator_database[query_result[0]["_id"]]

            # Update administrative_levels if not already present
            for level in doc_properties["administrative_levels"]:
                level_name = level["name"]
                level_id = level["id"]

                # Check if both name and id are not already present
                if all(
                    level_name != existing_level["name"]
                    or level_id != existing_level["id"]
                    for existing_level in existing_doc["administrative_levels"]
                ):
                    existing_doc["administrative_levels"].append(level)

            nsc.update_doc(facilitator_database, existing_doc["_id"], existing_doc)
            print(f"updated {facilitator.username} with {arr['name']}")
            update_count += 1

    if saved_count + update_count == num_rows:
        message = "Success!"
    elif saved_count == 0:
        message = "No items have been saved!"
    else:
        message = "A problem has occurred! Some element(s) have not been saved!"

    return message
