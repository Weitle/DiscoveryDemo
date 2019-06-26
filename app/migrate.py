from flask_migrate import Migrate
from app.db import db

migrate = Migrate(db=db)