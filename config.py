# Configuration settings for the agent system

import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "healthcare123")

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "openai" or "groq"
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")  # or "gpt-4"

# Agent Configuration
MAX_ITERATIONS = 10
TEMPERATURE = 0.0
