import json
import os
from typing import Dict, List, Any, Optional

class JSONDatabase:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            # Default to 'data' folder in the same directory as this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir
            
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.files = {
            "users": "users.json",
            "curriculum_years": "curriculum_years.json",
            "semesters": "semesters.json",
            "subjects": "subjects.json",
            "course_outcomes": "course_outcomes.json",
            "pyqs": "pyqs.json",
            "important_questions": "important_questions.json",
            "roadmap_steps": "roadmap_steps.json",
            "author_subjects": "author_subjects.json",
            "notes": "notes.json",
            "doubt_sessions": "doubt_sessions.json",
            "reference_videos": "reference_videos.json"
        }
        
        self._initialize_files()

    def _initialize_files(self):
        for table, filename in self.files.items():
            path = os.path.join(self.data_dir, filename)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump([], f)

    def _get_path(self, table: str) -> str:
        return os.path.join(self.data_dir, self.files[table])

    def read(self, table: str) -> List[Dict[str, Any]]:
        path = self._get_path(table)
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def write(self, table: str, data: List[Dict[str, Any]]):
        path = self._get_path(table)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        return self.read(table)

    def get_by_id(self, table: str, id_value: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
        data = self.read(table)
        for item in data:
            if item.get(id_field) == id_value:
                return item
        return None

    def add(self, table: str, item: Dict[str, Any]) -> Dict[str, Any]:
        data = self.read(table)
        
        # Simple ID generation if not provided
        if "id" not in item:
            if not data:
                item["id"] = 1
            else:
                item["id"] = max(i.get("id", 0) for i in data) + 1
        
        data.append(item)
        self.write(table, data)
        return item

    def update(self, table: str, id_value: Any, updates: Dict[str, Any], id_field: str = "id") -> Optional[Dict[str, Any]]:
        data = self.read(table)
        for i, item in enumerate(data):
            if item.get(id_field) == id_value:
                data[i].update(updates)
                self.write(table, data)
                return data[i]
        return None

    def delete(self, table: str, id_value: Any, id_field: str = "id") -> bool:
        data = self.read(table)
        initial_len = len(data)
        data = [item for item in data if str(item.get(id_field)) != str(id_value)]
        if len(data) < initial_len:
            self.write(table, data)
            return True
        return False

    def query(self, table: str):
        """Mock SQLAlchemy query interface for easier migration if possible"""
        return JSONQuery(self, table)

class JSONQuery:
    def __init__(self, db: JSONDatabase, table: str):
        self.db = db
        self.table = table
        self.data = db.read(table)

    def filter(self, **kwargs):
        filtered_data = []
        for item in self.data:
            match = True
            for key, value in kwargs.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered_data.append(item)
        self.data = filtered_data
        return self

    def first(self):
        return self.data[0] if self.data else None

    def all(self):
        return self.data

db = JSONDatabase()
