import sys, os
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from app.config import Config
from app.utils.logger import get_logger
logger = get_logger("mesh-capital")

if __name__ == "__main__":
    try: Config.validate()
    except ValueError as e:
        logger.error(f"Config error: {e}"); sys.exit(1)
    from app import create_app
    app = create_app(Config)
    logger.info(f"Starting Mesh Capital on port {Config.PORT}")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG, use_reloader=False)
