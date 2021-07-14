from flask_restful import  Resource, reqparse

from .models import User

class UserResource(Resource):

    def get(self, id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('username', 
            type=str,
            required=False
        )
        data = parser.parse_args()
        if id:
            try:
                user = User.find_by_id(id)
            except:
                return {"message" : "An error occurred while retrieving the user"}, 500
            
        elif data['username']:
            try:
                user = User.find_by_username(data['username'])
            except:
                return {"message" : "An error occurred while retrieving the user"}, 500
        else:
            return {"message" : "You must specify a user ID or a username."}, 400
        
        if user:
            return {'user' : user.json()}
        else:
            return {'message' : "User not found"}, 404


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', 
            help='Please specify a username.',
            required=True,
            type=str
        )
        parser.add_argument('password', 
            help='A password must be specified.', 
            required=True, 
            type=str
        )
        parser.add_argument('name', 
            required=False, 
            type=str
        )
        parser.add_argument('role',
            help='Role must be specified.',
            required=True,
            type=str
        )

        data = parser.parse_args()
        if User.find_by_username(data['username']): return {"message" : "An user with username {} already exists.".format(data['username'])}
        try:
            new_user = User.create_user(**data)
        except Exception as e:
            print(e)
            return {"message" : "An error ocurred while creating the user."}, 500
        return {"user" : new_user.json()}, 201


    def put(self, id=None):
        if not id: return {"message" : "Must specify the user id to update /user/<id>"}, 400
        
        try:
            user = User.find_by_id(id)
        except:
            return {"message" : "An error occurred while retrieving the user"}, 500
        
        if not user: return {"message" : "User does not exists."}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('password', type=str)
        data = parser.parse_args()

        for key, value in data.items():
            if key == 'name':
                user.name = value
                user.save_to_db()
            elif key == 'password':
                user.set_password(value)
                user.save_to_db()
        return {"message" : "User updated successfully.", "user" : user.json()}


    def delete(self, id=None):
        if not id: return {"message" : "Must specify the user id to delete /user/<id>"}, 400
       
        user = User.find_by_id(id)
        if user:
            user.delete_from_db()
            return {"message" : "User deleted successfully."}
        return {"message" : "User didn't exist."}