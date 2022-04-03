from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import requests
from .models import Books, Members, Issued
import json
from . import db
import datetime

URL = "https://frappe.io/api/method/frappe-library/?page="
books = Blueprint('books', __name__)

@books.route('/')
def index():
    if "logged_in" in session:
        books = Books.query.all()
        return render_template('books/index.html', books= books)
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@books.route('/book/<int:id>')
def book(id):
    if "logged_in" in session:
        book = Books.query.filter_by(book_id=id).first()
        if not book:
            return render_template('books/book.html', book=book)
        members= Members.query.with_entities(Members.id).all()
        issued = Issued.query.filter_by(book_id=book.id, status=True).all()
        for issue in issued:
            issue.update
        return render_template('books/book.html', book=book, members = members, issues=issued)
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@books.route('/import', methods=['GET'])
def dashboard():
    if "logged_in" in session:
        return render_template("books/import.html")
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@books.route('/browse', methods=['GET'])
def browse():
    return render_template("books/browse.html")

# API stuff #
@books.delete('/delete-book')
def delete():
    if "logged_in" in session:
        params = json.loads(request.data)
        id = int(params['id'])
        Books.query.filter_by(id=id).delete()
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({"status": "Failure - Not Logged in"}), 401

@books.delete('/delete-books')
def deleteAll():
    if "logged_in" in session:
        params = json.loads(request.data)
        ids = params['ids']
        Books.query.filter(Books.id.in_(ids)).delete()
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({"status": "Failure - Not Logged in"}), 401

@books.post('/add-books')
def add():
    if "logged_in" in session:
        params = json.loads(request.data)

        url = ''

        if 'title' in params:
            url = url + '&title=' + params['title']
        
        if 'author' in params:
            url = url + '&authors=' + params['author']
    
        if 'publisher' in params:
            url = url + '&publisher=' + params['publisher']
        
        quantity = int(params['quantity'])
        perbook = int(params['perbook'])
        if quantity <= 0 or perbook <=0 :
            return jsonify({'success': False}), 400

        page = 1
        while quantity > 0:
            response = requests.get(URL + str(page) + url).json()['message']
            if len(response) == 0:
                break
            for book in response:
                if quantity == 0:
                    break
                if len(Books.query.filter_by(book_id=book['bookID']).all()) == 0:
                    new = Books(book, perbook)
                    db.session.add(new)
                    quantity -= 1
            page += 1
        db.session.commit()
    
        return jsonify({'added': int(params['quantity']) - quantity})
    else:
        return jsonify({"status": "Failure - Not Logged in"}), 401