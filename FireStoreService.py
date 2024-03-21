from google.cloud import firestore
from datetime import datetime
from typing import Union

TIMESTAMP = "last_timestamp"
class FireStoreService:
    def __init__(self, project_id, database="github-commit-data", collection_name="latest_commit", document_id="F2NvrBYcwL0Yxe2UmN65") -> None:
        self.db = firestore.Client(project=project_id,database=database)
        self.collection_name = collection_name
        self.document_id = document_id
    
    def fetch_last_timestamp(self) -> Union[datetime, None]:
        doc_ref = self.db.collection(self.collection_name).document(self.document_id)       

        try:
            doc = doc_ref.get()
            if doc.exists:
                commit_timestamp = doc.to_dict().get(TIMESTAMP)
                print(f"last timestamp from database {commit_timestamp} \n {type(commit_timestamp)}")
                return commit_timestamp
            else:
                 # Instantiate timestamp here
                print("no timestamp in database. Instantiate a new one...")
                # TODO: check if this time object work since it needs to be iso8601 format
                current_time = datetime.now()
                self.db.update_last_timestamp(current_time)
                return current_time
        except Exception as e:
            print(f"An error occured: {e}")
            return None

    def update_last_timestamp(self, new_timestamp: datetime):
        """Updates the last timestamp in Datastore."""
        doc_ref = self.db.collection(self.collection_name).document(self.document_id)
        try:
            doc_ref.update({TIMESTAMP: new_timestamp})
            print(f"Last timestamp updated to {new_timestamp}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # for database class
    def convert_timestamp_from_zulu_to_UTC_format(self, zulu_iso_string:str) -> datetime:
        iso_string = zulu_iso_string.replace('Z', '+00:00')
        return datetime.fromisoformat(iso_string)
