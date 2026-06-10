import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

METADATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks_metadata.json")

class MetadataManager:
    def __init__(self):
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "w") as f:
                json.dump({"notebooks": []}, f)

    def load_all(self) -> List[Dict]:
        try:
            with open(METADATA_FILE, "r") as f:
                data = json.load(f)
                return data.get("notebooks", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_all(self, notebooks: List[Dict]):
        with open(METADATA_FILE, "w") as f:
            json.dump({"notebooks": notebooks}, f, indent=4)

    def create_notebook(self, name: str) -> Dict:
        notebooks = self.load_all()
        new_notebook = {
            "id": str(uuid.uuid4()),
            "name": name,
            "created_at": datetime.now().isoformat(),
            "last_model": "llama3.2:1b"
        }
        notebooks.append(new_notebook)
        self.save_all(notebooks)
        return new_notebook

    def delete_notebook(self, notebook_id: str) -> bool:
        notebooks = self.load_all()
        initial_count = len(notebooks)
        notebooks = [n for n in notebooks if n["id"] != notebook_id]
        if len(notebooks) < initial_count:
            self.save_all(notebooks)
            return True
        return False

    def get_notebook(self, notebook_id: str) -> Optional[Dict]:
        notebooks = self.load_all()
        for n in notebooks:
            if n["id"] == notebook_id:
                return n
        return None

    def update_model(self, notebook_id: str, model: str):
        notebooks = self.load_all()
        for n in notebooks:
            if n["id"] == notebook_id:
                n["last_model"] = model
                break
        self.save_all(notebooks)

metadata_manager = MetadataManager()
