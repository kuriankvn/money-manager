"""Main entry point for the finance manager application."""
import sys
from app.storage.db import init_database
from app.utils.logging import setup_logging, get_logger


def main() -> None:
    """Main entry point."""
    setup_logging()
    logger = get_logger(__name__)
    
    if len(sys.argv) < 2:
        print("Usage: python -m app.main <command>")
        print("\nCommands:")
        print("  init-db    Initialize the database")
        print("  version    Show version information")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init-db":
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
    
    elif command == "version":
        print("Personal Finance Manager v0.1.0")
        print("Architecture: Domain-driven design")
        print("Domains: Accounts, Subscriptions, Investments")
    
    else:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

