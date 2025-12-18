"""Configuration loading for Polymarket bot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Bot configuration loaded from environment variables."""

    # Polymarket API settings
    HOST: str = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
    CHAIN_ID: int = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))

    # Authentication
    PRIVATE_KEY: str = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    FUNDER_ADDRESS: str = os.getenv("POLYMARKET_FUNDER_ADDRESS", "")

    # Bot settings
    MAX_BID_PRICE: float = float(os.getenv("MAX_BID_PRICE", "0.05"))
    ORDER_SIZE: float = float(os.getenv("ORDER_SIZE", "5.0"))
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        errors = []

        if not cls.PRIVATE_KEY:
            errors.append("POLYMARKET_PRIVATE_KEY is not set")
        elif not cls.PRIVATE_KEY.startswith("0x"):
            errors.append("POLYMARKET_PRIVATE_KEY must start with '0x'")

        if not cls.FUNDER_ADDRESS:
            errors.append("POLYMARKET_FUNDER_ADDRESS is not set")
        elif not cls.FUNDER_ADDRESS.startswith("0x"):
            errors.append("POLYMARKET_FUNDER_ADDRESS must start with '0x'")

        if cls.MAX_BID_PRICE <= 0:
            errors.append("MAX_BID_PRICE must be positive")

        if cls.ORDER_SIZE <= 0:
            errors.append("ORDER_SIZE must be positive")

        if errors:
            raise ValueError("Configuration errors:\n  - " + "\n  - ".join(errors))

    @classmethod
    def display(cls) -> None:
        """Display current configuration (with sensitive data masked)."""
        print("=== Configuration ===")
        print(f"  Host: {cls.HOST}")
        print(f"  Chain ID: {cls.CHAIN_ID}")
        print(f"  Private Key: {'*' * 10}...{cls.PRIVATE_KEY[-4:] if cls.PRIVATE_KEY else 'NOT SET'}")
        print(f"  Funder Address: {cls.FUNDER_ADDRESS or 'NOT SET'}")
        print(f"  Max Bid Price: ${cls.MAX_BID_PRICE}")
        print(f"  Order Size: {cls.ORDER_SIZE} shares")
        print(f"  Dry Run: {cls.DRY_RUN}")
        print("=====================")
