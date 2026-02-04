# # [see](https://chatgpt.com/s/t_68d3023d89ec8191895eda0e0c3bee62)

# from pydantic import Field, SecretStr
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     # --- core ---
#     env: str = Field("dev", description="Environment name: dev|test|prod")

#     # --- database (shared or per-context) ---
#     db_url: str = Field(..., alias="DATABASE_URL")
#     chat_db_url: str | None = None  # if None, fall back to db_url
#     knowledge_db_url: str | None = None  # same

#     # --- external services ---
#     openai_api_key: SecretStr | None = Field(default=None, alias="OPENAI_API_KEY")

#     # --- feature flags / tuning ---
#     enable_rag: bool = False

#     model_config = SettingsConfigDict(
#         env_file=".env",  # load .env in dev
#         env_file_encoding="utf-8",
#         extra="ignore",  # ignore unknown envs
#         populate_by_name=True,  # allow using field names as env keys
#     )

#     # Computed fallbacks
#     @property
#     def chat_db(self) -> str:
#         return self.chat_db_url or self.db_url

#     @property
#     def knowledge_db(self) -> str:
#         return self.knowledge_db_url or self.db_url
