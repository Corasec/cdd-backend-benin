# This library is meant to be a wrapper to connect
# To the cdd app couch db database. This depends on the
# no_sql_client.py library
import time
from no_sql_client import NoSQLClient
from cdd.constants import ADMINISTRATIVE_LEVEL_TYPE


def iterate_administrative_level(adm_list, type):
    for administrative_level in adm_list.filter(type=type):
        print(administrative_level.name)


class CddClient:
    def __init__(self):
        self.nsc = NoSQLClient()
        self.adm_db = self.nsc.get_db("administrative_levels")

    def iterate_administrative_level(self, adm_list, type):
        for administrative_level in adm_list.filter(type=type):
            print("CREATING", administrative_level.name)
            self.create_administrative_level(administrative_level)
            print("DONE", administrative_level.name)

    def create_administrative_level(self, adm_obj):
        # TODO: You need to manage the parent id from couch.
        # TODO 2: You need to manage the administrative_id.
        parent = ""
        if adm_obj.parent:
            parent = str(adm_obj.parent.id)
        data = {
            "administrative_id": str(adm_obj.id),
            "name": adm_obj.name,
            "administrative_level": adm_obj.type,
            "type": "administrative_level",
            "parent_id": parent,
            "latitude": float(adm_obj.latitude),
            "longitude": float(adm_obj.longitude),
        }
        self.nsc.create_document(self.adm_db, data)
        new = self.adm_db.get_query_result(
            {
                "type": "administrative_level",
                "administrative_id": str(adm_obj.id),
            }
        )
        final = None
        for obj in new:
            final = obj
        return final["_id"]

    def sync_administrative_levels(self, administrative_levels) -> bool:
        # Sync DÉPARTEMENT
        self.iterate_administrative_level(
            administrative_levels, ADMINISTRATIVE_LEVEL_TYPE.DÉPARTEMENT
        )
        # Sync COMMUNE
        self.iterate_administrative_level(
            administrative_levels, ADMINISTRATIVE_LEVEL_TYPE.COMMUNE
        )
        # Sync ARRONDISSEMENT
        self.iterate_administrative_level(
            administrative_levels, ADMINISTRATIVE_LEVEL_TYPE.ARRONDISSEMENT
        )
        # Sync VILLAGE
        self.iterate_administrative_level(
            administrative_levels, ADMINISTRATIVE_LEVEL_TYPE.VILLAGE
        )

        return True

    def update_administrative_level(self, obj) -> bool:
        administrative_level = self.adm_db[obj.no_sql_db_id]
        print(administrative_level)
        parent = ""
        if obj.parent:
            parent = str(obj.parent.id)
        data = {
            "name": obj.name,
            "administrative_level": obj.type,
            "parent_id": parent,
            "latitude": float(obj.latitude),
            "longitude": float(obj.longitude),
        }
        for k, v in data.items():
            if v:
                administrative_level[k] = v
        administrative_level.save()
        return True
