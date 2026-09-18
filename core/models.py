from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== 職缺相關模型 ====================

class SkillItem(BaseModel):
    name: str
    category: str = "General"  # Language, Framework, Database, DevOps, Architecture, etc.
    weight: float = 1.0

class JobRequirements(BaseModel):
    actual_seniority: str = "Mid"  # Junior, Mid, Senior, Lead
    seniority_reason: str = ""
    software_domain: str = "Backend / Cloud"  # Web, Firmware, EDA, AI, etc.
    must_have: List[SkillItem] = []
    nice_to_have: List[SkillItem] = []
    core_capabilities: List[str] = []

class SalaryInfo(BaseModel):
    raw_text: str = ""
    is_negotiable: bool = False
    min_annual: Optional[float] = None
    max_annual: Optional[float] = None
    estimated_annual: Optional[float] = None  # 當為面議時，由 LLM 推估之基準年薪
    estimation_basis: Optional[str] = None

class JobRecord(BaseModel):
    id: str  # e.g., "104_98765432"
    source: str  # "104", "cakeresume", "ats"
    company_name: str
    title: str
    url: str
    location: str = "台灣"
    posted_at: str  # ISO string or YYYY-MM-DD
    salary: SalaryInfo = Field(default_factory=SalaryInfo)
    raw_jd: str = ""
    requirements: Optional[JobRequirements] = None
    fit_score: float = 0.0  # 0~100 個人契合度
    is_processed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

# ==================== 使用者數位檔案與校準模型 ====================

class CalibratedSkill(BaseModel):
    name: str
    category: str = "General"
    level: str = "Competent"  # Proficient, Competent, Developing, Conceptual
    verified_depth: str = ""
    interview_ready: bool = True
    evidence_notes: str = ""

class CanonicalDossier(BaseModel):
    user_id: str = "default_user"
    effective_years_of_experience: float = 0.0
    core_domain: str = "Software Engineering"
    calibrated_skills: List[CalibratedSkill] = []
    learning_boundary_skills: List[str] = []
    target_roles: List[str] = ["軟體工程師"]
    last_calibrated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    raw_resume_summary: str = ""

class CalibrationQuestion(BaseModel):
    q_id: str
    target_skill: str
    question_text: str
    user_answer: Optional[str] = None
    is_follow_up: bool = False
    evaluation_result: Optional[str] = None

class CalibrationSession(BaseModel):
    session_id: str
    status: str = "in_progress"  # in_progress, completed
    questions: List[CalibrationQuestion] = []
    current_q_index: int = 0
    dossier: Optional[CanonicalDossier] = None

# ==================== 技能 ROI 決策模型 ====================

class LearningMilestone(BaseModel):
    phase: str
    hours: float
    description: str = ""

class SkillROI(BaseModel):
    skill_name: str
    category: str = "General"
    incremental_jobs_count: int = 0  # ΔN
    salary_premium_annual: float = 0.0  # ΔSalary (TWD)
    estimated_learning_hours: float = 0.0  # H(S, U)
    hourly_roi_score: float = 0.0
    quadrant: str = "Quick Wins"  # Quick Wins, High-Leverage Strategic, Deep Investment, Low ROI
    rationale: str = ""
    milestones: List[LearningMilestone] = []
