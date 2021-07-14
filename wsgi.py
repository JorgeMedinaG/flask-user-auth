"""Application entry point."""
from application import create_app
from config import *
from dotenv import load_dotenv

load_dotenv()

if os.environ.get('FLASK_ENV') == 'development':
    app = create_app(DevelopmentConfig)
    print("Loading with development config")
else:
    app = create_app(ProductionConfig)
    print("Loading with production setup")

if __name__ == "__main__":
    app.run(host='0.0.0.0')