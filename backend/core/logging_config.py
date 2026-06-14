import logging
import sys

def setup_logging():
    # Setup structured formatting for CLI output
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-24s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Minimize noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

# Run setup
setup_logging()
logger = logging.getLogger("app")
