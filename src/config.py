import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()],
)


class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
    temperature: float = float(os.getenv("TEMPERATURE", "0"))
    port: int = int(os.getenv("PORT", "7860"))
    app_title: str = "Arihant Healthcare Support AI"
    app_description: str = (
        "Welcome! I am an intelligent multi-agent assistant designed to help you explore medical equipment, look up your orders, "
        "and find your purchase history. To access your account, please provide "
        "your Customer ID, email, or phone number."
    )


settings = Settings()
