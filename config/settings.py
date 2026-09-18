import os
from pathlib import Path
from dotenv import load_dotenv

# 基礎專案路徑
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# 載入 .env
load_dotenv(BASE_DIR / ".env")

# 系統設定物件
class Settings:
    PROJECT_NAME: str = "SkillRadar"
    DATABASE_PATH: Path = DATA_DIR / "skill_radar.db"
    COMPANIES_YAML_PATH: Path = CONFIG_DIR / "companies.yaml"
    
    # 溫和爬蟲防 DDoS 參數
    CRAWLER_MIN_DELAY: float = float(os.getenv("CRAWLER_MIN_DELAY", "2.5"))
    CRAWLER_MAX_DELAY: float = float(os.getenv("CRAWLER_MAX_DELAY", "4.5"))
    CRAWLER_USER_AGENT: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    
    # 技能校準重訪談週期（預設 7 天）
    REINTERVIEW_INTERVAL_DAYS: int = int(os.getenv("REINTERVIEW_INTERVAL_DAYS", "7"))
    
    # Gemini 模型配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

settings = Settings()
