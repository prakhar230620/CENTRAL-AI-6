from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "ai_platform"
    ai_collection_name: str = "ai_registry"
    cache_max_size: int = 1000
    cache_ttl: int = 3600  # 1 hour
    nlp_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    ner_model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    tts_language: str = "en"
    temp_directory: str = "/tmp"
    log_level: str = "INFO"
    api_rate_limit: int = 100  # requests per minute
    max_input_length: int = 1000  # characters

    class Config:
        env_file = ".env"

settings = Settings()