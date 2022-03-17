import re
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import requests
import json
from .models import Books, Members
from . import db

URL = "https://frappe.io/api/method/frappe-library/?page="
api = Blueprint('api', __name__)

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

@api.get('/get_books')
def get_books():
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1

    if request.args.get('title') != '' and request.args.get('authors') != '':
        bookByTitle = requests.get(URL+f"{page}&title={request.args.get('title')}").json()['message']
        bookByAuthors = requests.get(URL+f"{page}&authors={request.args.get('authors')}").json()['message']
        books = intersection(bookByTitle, bookByAuthors)
    elif request.args.get('title') != '':
        books = requests.get(URL+f"{page}&title={request.args.get('title')}").json()['message']
    elif request.args.get('authors') != '':
        books = requests.get(URL+f"{page}&authors={request.args.get('authors')}").json()['message']
    else:
        books = requests.get(URL+f"{page}").json()['message']

    return jsonify(books), 200

@api.get('/member/<int:id>')
def get(id):
    if "logged_in" in session:
        user = Members.query.get(id)
        if user is None:
            return jsonify(error="User not found"), 400
        else:
            return jsonify(user=user.serialize), 200
    else:
        return jsonify(error="Please Login to Use API"), 401

# @api.get('/users')
# def get_users():
#     users = Members.query.all()
#     return jsonify(users=[user.serialize for user in users]), 200

# @api.get('/users/<id>')
# def get_user(id):
#     if not id.isnumeric():
#         return jsonify(message = "User ID should by numeric"), 404
#     user = Members.query.filter(Members.id == id).one_or_none()
#     if user is None:
#         return jsonify(message = "User Not Found", user = f"none"), 404
#     user = Members.query.get(id)
#     return jsonify(message = "User Found",user = id, details=user.serialize), 200

# @api.get('/books')
# def books():
#     books = [book.id for book in Books.query.with_entities(Books.id)]
#     ok = books.sort()
#     print(type(ok))
#     return jsonify( books = len(books), bookIDs = books), 200

# @api.get('/books/<id>')
# def book():
#     if not id.isnumeric():
#         return jsonify(message = "Book ID should by numeric"), 404
#     user = Members.query.filter(Members.id == id).one_or_none()
#     if user is None:
#         return jsonify(message = "User Not Found", user = f"none"), 404
#     user = Members.query.get(id)
#     return jsonify(message = "User Found",user = id, details=user.serialize), 200



