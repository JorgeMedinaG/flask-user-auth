from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()

def create_app(config):
	from .jwt_config import jwt
	
	app = Flask(__name__)
	api = Api(app)
	admin = Admin(app,name='User Manager')
	app.config.from_object(config)

	db.init_app(app)
	jwt.init_app(app)

	from .auth.resource import UserResource
	api.add_resource(UserResource, '/user', '/user/<int:id>')
	
	from .auth import routes
	app.register_blueprint(routes.auth_bp)

	from .auth.models import User, Role, Permission, TokenBlocklist
	admin.add_view(ModelView(User, db.session))
	admin.add_view(ModelView(Role, db.session))
	admin.add_view(ModelView(Permission, db.session))
	admin.add_view(ModelView(TokenBlocklist, db.session))

	with app.app_context():
		db.create_all()
		
	return app