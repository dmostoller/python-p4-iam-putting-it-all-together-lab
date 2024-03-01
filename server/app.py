#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            form_json = request.get_json()
            new_user = User(
                username=form_json['username'],
                password_hash=form_json['password'],
                image_url=form_json['image_url'],
                bio=form_json['bio']
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id 
            response = make_response(new_user.to_dict(rules = ('-_password_hash', )), 201)
        except IntegrityError:
            response = make_response({'errors': ['validation errors']}, 422)
        
        return response

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(rules = ('-_password_hash', )), 200
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter(User.username == username).first()
        if user:
            session['user_id'] = user.id
            return user.to_dict(rules = ('-_password_hash', )), 200
        return {'error': 'Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session['user_id'] == None:
            return {'error': 'Unauthorized'}, 401
        session['user_id'] = None
        return {}, 204
        

class RecipeIndex(Resource):
    def get(self):
        if not session['user_id']:
            return {'error': 'Unauthorized'}, 401
        recipes = [recipe.to_dict(rules = ('-user_id', '-id')) for recipe in Recipe.query.all()]
        return make_response(jsonify(recipes), 200) 
    
    def post(self):
        if not session['user_id']:
            return {'error': 'Unauthorized'}, 401
        try:
            form_json = request.get_json()
            new_recipe = Recipe(
                title=form_json['title'],
                instructions=form_json['instructions'],
                minutes_to_complete=form_json['minutes_to_complete'],
                user_id=session.get('user_id')
            )
            db.session.add(new_recipe)
            db.session.commit()
            response = make_response(new_recipe.to_dict(), 201)
        except ValueError:
            response = make_response({"errors" : ["validation erros"]}, 422)
        
        return response
    
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)