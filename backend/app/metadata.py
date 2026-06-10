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
            "last_model": "llama3.2:1b",
            "history": [],
            "files_status": {} # Track status of each file: "processing", "ready", "error"
        }
        notebooks.append(new_notebook)
        self.save_all(notebooks)
        return new_notebook

    def update_file_status(self, notebook_id: str, filename: str, status: str):
        notebooks = self.load_all()
        for n in notebooks:
            if n["id"] == notebook_id:
                if "files_status" not in n: n["files_status"] = {}
                n["files_status"][filename] = status
                break
        self.save_all(notebooks)

    def get_files_status(self, notebook_id: str) -> Dict[str, str]:
        n = self.get_notebook(notebook_id)
        return n.get("files_status", {}) if n else {}

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

    def add_history_message(self, notebook_id: str, role: str, content: str, sources: List[str] = None):
        notebooks = self.load_all()
        for n in notebooks:
            if n["id"] == notebook_id:
                if "history" not in n: n["history"] = []
                n["history"].append({
                    "role": role,
                    "content": content,
                    "sources": sources or []
                })
                # Limit history size to 30 messages
                n["history"] = n["history"][-30:]
                break
        self.save_all(notebooks)

    def clear_history(self, notebook_id: str):
        notebooks = self.load_all()
        for n in notebooks:
            if n["id"] == notebook_id:
                n["history"] = []
                break
        self.save_all(notebooks)

metadata_manager = MetadataManager()
