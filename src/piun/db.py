"""Wrapper around db operations"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_DEFAULT_PATH = Path("~/.cache/piun/image.db")


class PiunDatabase:
    """Class to handle database interactions"""

    db = None
    layer_table_name = "layer"
    hash_field_name = "hash"
    hash_type_field_name = "hash_type"
    image_field_name = "image"

    def __init__(self, database_path=DB_DEFAULT_PATH):
        """Initialize db"""
        if not isinstance(database_path, Path):
            raise ValueError("Incorrect path type!")
        realpath = database_path.expanduser()
        realpath.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.db = sqlite3.connect(realpath.as_posix())
        self.create_layer_table()

    def __del__(self):
        if self.db:
            self.db.commit()
            self.db.close()

    def create_table(self, table_name, *params):
        """Create the table if it does not already exist"""
        table = self.db.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        if not table.fetchone():
            self.db.execute(f"CREATE TABLE {table_name}({', '.join(params)})")

    def create_layer_table(self):
        """Create the layer table with the hash, hash_type, and image fields"""
        self.create_table(
            self.layer_table_name,
            self.hash_type_field_name,
            self.hash_field_name,
            self.image_field_name,
        )

    def hash_in_table(self, hash_type, hash_value, image_name):
        """Check the table for a given hash and return if we have an entry"""
        hash_row = self.db.execute(
            f"""SELECT * FROM {self.layer_table_name}
                WHERE {self.hash_type_field_name}='{hash_type}'
                AND {self.hash_field_name}='{hash_value}'
                AND {self.image_field_name}='{image_name}'"""
        )
        if hash_row.fetchone():
            return True
        return False

    def add_hash(self, hash_type, hash_value, image_name):
        """Add a hash row to the table"""
        self.db.execute(
            f"""INSERT INTO {self.layer_table_name} VALUES
            ('{hash_type}', '{hash_value}', '{image_name}')"""
        )
        self.db.commit()

    def add_unique_hash(self, hash_type, hash_value, image_name):
        """Add a unique hash to the table, return false if it was not unique"""
        if self.hash_in_table(hash_type, hash_value, image_name):
            return False
        self.add_hash(hash_type, hash_value, image_name)
        return True

    def clear_old_hashes(self, image_name):
        """Remove the old hashes associated with the given image"""
        self.db.execute(
            f"""DELETE FROM {self.layer_table_name}
            WHERE {self.image_field_name}='{image_name}'"""
        )
