from flask_jwt_extended import JWTManager
from .auth.models import User, TokenBlocklist

jwt = JWTManager()


@jwt.user_lookup_loader
def user_lookup_loader(jwt_header, jwt_payload):
    identity = jwt_payload['sub']
    return User.find_by_id(identity)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    if TokenBlocklist.check_revoked(jwt_payload['jti']):
        return True
    return False

