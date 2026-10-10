# Configuration settings for the agent system

import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "healthcare123")

# Authentication Configuration
# JWT_SECRET_KEY must be set in .env (generate with: python -c "import secrets; print(secrets.token_hex(32))")
# It is intentionally left empty here so a missing secret fails loudly instead of
# silently signing tokens with a predictable fallback value.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
AUTH_DB_PATH = os.getenv("AUTH_DB_PATH", "auth.db")

# CORS: comma-separated list of origins allowed to call the API
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "openai" or "groq"
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")  # or "gpt-4"

# Agent Configuration
MAX_ITERATIONS = 10
TEMPERATURE = 0.0
