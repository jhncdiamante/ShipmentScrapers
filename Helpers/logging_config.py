import logging

def setup_logger(name=None):
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            filename='Application.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S',
            filemode='a'
        )

        # Optional: Add console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
    return logging.getLogger(name) if name else logging.getLogger()