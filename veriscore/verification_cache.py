import sqlite3
import hashlib
import re
from pathlib import Path


def normalize_claim(claim: str) -> str:
    claim = claim.strip().lower()
    claim = re.sub(r"\s+", " ", claim)
    claim = claim.rstrip(".,;:!?")
    return claim


def hash_claim(normalized_claim: str) -> str:
    return hashlib.sha256(normalized_claim.encode("utf-8")).hexdigest()


class VerificationCache:
    def __init__(self, db_path="verification_cache.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS verification_cache (
            claim_hash TEXT,
            normalized_claim TEXT,
            model_name TEXT,
            verdict TEXT,
            PRIMARY KEY (claim_hash, model_name)
        );
        """)
        self.conn.commit()

    def get(self, claim: str, model_name: str):
        normalized = normalize_claim(claim)
        claim_hash = hash_claim(normalized)

        cursor = self.conn.execute("""
            SELECT verdict FROM verification_cache
            WHERE claim_hash = ? AND model_name = ?
        """, (claim_hash, model_name))

        row = cursor.fetchone()
        return row[0] if row else None

    def add(self, claim: str, model_name: str, verdict: str):
        normalized = normalize_claim(claim)
        claim_hash = hash_claim(normalized)

        self.conn.execute("""
            INSERT OR REPLACE INTO verification_cache
            (claim_hash, normalized_claim, model_name, verdict)
            VALUES (?, ?, ?, ?)
        """, (claim_hash, normalized, model_name, verdict))

        self.conn.commit()