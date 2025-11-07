import os
from functools import lru_cache
from typing import List, Optional


class Settings:
    def __init__(self):
        # Load environment variables
        self._load_env()
        
        # App
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.cors_allow_origins: List[str] = self._parse_cors_origins()

        # Data & Paths
        self.data_dir: str = "data"
        self.uploads_dir: str = "data/uploads"
        self.indexes_dir: str = "data/indexes"
        self.sqlite_url: str = "sqlite:///data/meta.db"

        # Embeddings
        self.embedding_model_name: str = "bge-large-en-v1.5"
        self.embedding_batch_size: int = 64
        self.embedding_cache_dir: Optional[str] = None

        # Vector store (FAISS HNSW)
        self.faiss_index_path: str = "data/indexes/bge-large-en.hnsw.faiss"
        self.faiss_hnsw_M: int = 32
        self.faiss_hnsw_ef_construction: int = 200
        self.faiss_ef_search: int = 128

        # Retrieval
        self.retrieval_top_k: int = 8

        # Context
        self.context_budget_tokens: int = 6000
        self.mmr_lambda: float = 0.7

        # Generator provider selection
        self.generator_provider: str = os.getenv("GENERATOR_PROVIDER", "gemini")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = "gpt-4o-mini"
        self.openai_temperature: float = 0.2
        self.openai_max_tokens: int = 1024

        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.gemini_model: str = "gemini-2.5-flash"

        # Orchestration
        self.enable_query_enhancer: bool = False
        self.enable_rerank: bool = True
        self.enable_compress: bool = True
        self.enable_select: bool = True
        self.max_iterations: int = 2
        self.schedule_continue_threshold: float = 0.55

        # Telemetry
        self.log_level: str = "INFO"
        
        # Ensure directories exist
        self._ensure_dirs()

    def _load_env(self):
        """Load environment variables from .env file if it exists"""
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment"""
        cors_env = os.getenv("CORS_ALLOW_ORIGINS", '["*"]')
        if cors_env.startswith('[') and cors_env.endswith(']'):
            # Remove brackets and quotes, split by comma
            origins = cors_env[1:-1].replace('"', '').split(',')
            return [origin.strip() for origin in origins if origin.strip()]
        return ["*"]

    def _ensure_dirs(self):
        """Ensure required directories exist"""
        for dir_path in [self.data_dir, self.uploads_dir, self.indexes_dir]:
            os.makedirs(dir_path, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


