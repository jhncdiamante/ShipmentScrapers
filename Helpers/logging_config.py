import logging


def setup_logger(name=None):
    # Clear all existing handlers (reset logger)
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Setup basic configuration
    logging.basicConfig(
        filename="Application.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s\n",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="w",  # overwrite file on each run
    )

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    return logging.getLogger(name) if name else logging.getLogger()
