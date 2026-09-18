import sqlite3
import json
from typing import List, Optional
from pathlib import Path
from config.settings import settings
from core.models import JobRecord, CanonicalDossier, CalibrationSession, SalaryInfo, JobRequirements

class DatabaseManager:
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 職缺表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                company_name TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                location TEXT,
                posted_at TEXT NOT NULL,
                salary_json TEXT,
                raw_jd TEXT,
                requirements_json TEXT,
                fit_score REAL DEFAULT 0.0,
                is_processed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs (posted_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_processed ON jobs (is_processed)")

            # 2. 使用者權威檔案表 (Canonical Dossier)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_dossier (
                user_id TEXT PRIMARY KEY,
                dossier_json TEXT NOT NULL,
                last_calibrated_at TEXT NOT NULL
            )
            """)

            # 3. 訪談會話表 (Calibration Sessions)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS calibration_sessions (
                session_id TEXT PRIMARY KEY,
                session_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """)
            
            conn.commit()

    # ================= 職缺操作 =================

    def job_exists(self, job_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,))
            return cursor.fetchone() is not None

    def save_job(self, job: JobRecord) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO jobs (
                id, source, company_name, title, url, location,
                posted_at, salary_json, raw_jd, requirements_json,
                fit_score, is_processed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.source,
                job.company_name,
                job.title,
                job.url,
                job.location,
                job.posted_at,
                job.salary.model_dump_json(),
                job.raw_jd,
                job.requirements.model_dump_json() if job.requirements else None,
                job.fit_score,
                1 if job.is_processed else 0,
                job.created_at
            ))
            conn.commit()
            return True

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_job(row)

    def get_all_jobs(self, limit: int = 100) -> List[JobRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY posted_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_job(r) for r in rows]

    def get_unprocessed_jobs(self, limit: int = 50) -> List[JobRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE is_processed = 0 ORDER BY posted_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_job(r) for r in rows]

    def _row_to_job(self, row: sqlite3.Row) -> JobRecord:
        salary_data = json.loads(row["salary_json"]) if row["salary_json"] else {}
        req_data = json.loads(row["requirements_json"]) if row["requirements_json"] else None
        
        return JobRecord(
            id=row["id"],
            source=row["source"],
            company_name=row["company_name"],
            title=row["title"],
            url=row["url"],
            location=row["location"] or "台灣",
            posted_at=row["posted_at"],
            salary=SalaryInfo(**salary_data),
            raw_jd=row["raw_jd"] or "",
            requirements=JobRequirements(**req_data) if req_data else None,
            fit_score=row["fit_score"],
            is_processed=bool(row["is_processed"]),
            created_at=row["created_at"]
        )

    # ================= 使用者權威檔案操作 =================

    def save_dossier(self, dossier: CanonicalDossier):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO user_dossier (user_id, dossier_json, last_calibrated_at)
            VALUES (?, ?, ?)
            """, (
                dossier.user_id,
                dossier.model_dump_json(),
                dossier.last_calibrated_at
            ))
            conn.commit()

    def get_dossier(self, user_id: str = "default_user") -> Optional[CanonicalDossier]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dossier_json FROM user_dossier WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return CanonicalDossier(**json.loads(row["dossier_json"]))

    # ================= 訪談會話操作 =================

    def save_calibration_session(self, session: CalibrationSession):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO calibration_sessions (session_id, session_json, updated_at)
            VALUES (?, ?, datetime('now'))
            """, (
                session.session_id,
                session.model_dump_json()
            ))
            conn.commit()

    def get_calibration_session(self, session_id: str) -> Optional[CalibrationSession]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session_json FROM calibration_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return CalibrationSession(**json.loads(row["session_json"]))

db = DatabaseManager()
