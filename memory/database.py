"""SQLite database manager for JARVIS."""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Tuple, Any
from datetime import datetime

from core.config import Config
from core.logger import get_logger
from core.exceptions import DatabaseError

logger = get_logger("database")


class DatabaseManager:
    """SQLite database manager with thread safety."""

    def __init__(self) -> None:
        self.config = Config()
        self.db_path = self.config.database_path
        self._local = threading.local()
        self._lock = threading.Lock()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self._local.connection.row_factory = sqlite3.Row
            self._local.connection.execute("PRAGMA journal_mode=WAL")
            self._local.connection.execute("PRAGMA foreign_keys=ON")
        return self._local.connection

    @property
    def conn(self) -> sqlite3.Connection:
        return self._get_connection()

    def initialize(self) -> None:
        """Create all required tables."""
        logger.info(f"Initializing database at {self.db_path}")

        with self._lock:
            c = self.conn
            c.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    remind_at DATETIME NOT NULL,
                    recurring TEXT DEFAULT NULL,
                    completed INTEGER DEFAULT 0,
                    created DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT DEFAULT '',
                    success INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    command TEXT DEFAULT '',
                    detected_language TEXT DEFAULT '',
                    intent TEXT DEFAULT '',
                    tool TEXT DEFAULT '',
                    parameters TEXT DEFAULT '',
                    permission_level TEXT DEFAULT '',
                    confirmed INTEGER DEFAULT 0,
                    result TEXT DEFAULT '',
                    error TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS batch_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    source_path TEXT NOT NULL,
                    batch_size INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'pending',
                    total_files INTEGER DEFAULT 0,
                    processed INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    created DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS batch_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    error TEXT DEFAULT '',
                    processed_at DATETIME DEFAULT NULL,
                    FOREIGN KEY (job_id) REFERENCES batch_jobs(job_id)
                );

                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_memory_category ON memory(category);
                CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON reminders(remind_at);
                CREATE INDEX IF NOT EXISTS idx_batch_files_job ON batch_files(job_id);
            """)
            c.commit()
            logger.info("Database initialized successfully.")

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Execute a query with parameters."""
        with self._lock:
            try:
                cursor = self.conn.execute(query, params)
                self.conn.commit()
                return cursor
            except sqlite3.Error as e:
                logger.error(f"Database error: {e} | Query: {query}")
                raise DatabaseError(f"Database error: {e}")

    def fetchall(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a query and fetch all results."""
        with self._lock:
            try:
                cursor = self.conn.execute(query, params)
                return cursor.fetchall()
            except sqlite3.Error as e:
                logger.error(f"Database fetch error: {e}")
                raise DatabaseError(f"Database error: {e}")

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Execute a query and fetch one result."""
        with self._lock:
            try:
                cursor = self.conn.execute(query, params)
                return cursor.fetchone()
            except sqlite3.Error as e:
                logger.error(f"Database fetch error: {e}")
                raise DatabaseError(f"Database error: {e}")

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            try:
                self._local.connection.close()
                self._local.connection = None
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error closing database: {e}")
