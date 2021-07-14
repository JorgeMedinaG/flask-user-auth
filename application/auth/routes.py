from flask import Blueprint
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity, 
    get_jwt
)
from .models import User, TokenBlocklist

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/auth/login', methods=['POST'])
def login():
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                            type=str,
                            required=True,
                            help="This field cannot be blank."
                            )
    parser.add_argument('password',
                            type=str,
                            required=True,
                            help="This field cannot be blank."
                            )
    try:
        data = parser.parse_args()
    except :
        return {"message" : "User information is needed"}, 400
    user = User.find_by_username(data['username'])
    if not user:
        return {"message" : "User does not exists."}, 400
    if user.check_password(data['password']):
        access_token = create_access_token(user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {
            'user'          : user.json(),
            'acces_token'   : access_token,
            'refresh_token' : refresh_token
        }, 200
    return {'message' : 'Invalid credentials.'}, 401

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    id = get_jwt_identity()
    new_access_token = create_access_token(id, fresh=False)
    return {'access_token' : new_access_token}, 200


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    try:
        TokenBlocklist.revoke_token(jti)
    except Exception as e:
        print(e)
        return {'message' : 'An error occurred while logging out.'}, 500
    return {'message' : 'Successfully logged out'}, 200