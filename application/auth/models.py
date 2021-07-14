import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from application import db


user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True), 
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100))
    encrypted_password = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.datetime.now())
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    role = db.relationship('Role', secondary=user_role)

    def __repr__(self):
        return '<User {}-{}>'.format(self.id,self.username)

    def set_password(self, password):
        self.encrypted_password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.encrypted_password, password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            'id'         : self.id,
            'username'   : self.username,
            'name'       : self.name,
            'last_login' : str(self.last_login),
            'role'       : self.role[0].json()
        }

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def create_user(cls, **data ):
        user = cls(
            username=data['username'],
            name=data['name'] if data['name'] else "",
            encrypted_password="",
        )
        role_s = Role.query.filter_by(name=data['role']).first()
        user.role.append(role_s)
        user.set_password(data['password'])
        user.save_to_db()
        return user


role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True), 
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    permission = db.relationship('Permission', secondary=role_permission)

    def __repr__(self):
        return '< {} >'.format(self.name)

    def json(self):
        return {
            "role_name"  : self.name,
            "permission" : [permission.permission_name for permission in self.permission]
        }

class Permission(db.Model):

    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '< {} >'.format(self.permission_name)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)

    @classmethod
    def check_revoked(cls, jti):
        if cls.query.filter_by(jti=jti).first() :
            return True
        return False

    @classmethod
    def revoke_token(cls, jti):
        token = cls(jti=jti)
        db.session.add(token)
        db.session.commit()