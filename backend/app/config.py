from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    # MySQL
    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "cosmetics_ai"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    # JWT
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # LLM
    llm_api_key: str = ""
    llm_api_base: str = ""
    llm_model: str = "gpt-4"

    # RAGFlow
    ragflow_url: str = "http://192.168.1.100:9380"
    ragflow_api_key: str = ""

    # Dify
    dify_url: str = "https://api.dify.ai"
    dify_api_key: str = ""

    # Dify Workflow Keys
    dify_wf_regulation_search_key: str = ""
    dify_wf_doc_review_key: str = ""
    dify_wf_copy_review_key: str = ""
    dify_wf_copy_generate_key: str = ""
    dify_chat_app_key: str = ""

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "cosmetics-ai"
    minio_secure: bool = False

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    model_config = {"env_file": ".env"}


settings = Settings()
