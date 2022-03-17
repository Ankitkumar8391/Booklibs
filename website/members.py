from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import requests
from .models import *
import json
from . import db
import datetime


member = Blueprint('members', __name__)

def issue(member, book):
    Book = Books.query.get(book)
    Member = Members.query.get(member)

    if Book is None:
            return 400, "Book not found"
    elif Book.quantity - Book.issued <= 0:
            return 400, "Book not available"


    if Member is None:
        return 400, "Member not found"
    elif (Member.credit-INIT_RENT) < -500:
        return 400, "Member has insufficient credit"
    
    issued = Issued.query.filter_by(member_id=member, book_id=book, status=True).first()
    
    if issued:
        return 400, 'Book Already Issued'
    else:
        issued = Issued(member, book)
        Member.credit = Member.credit - INIT_RENT
        Member.books.append(issued)
        Book.issued = Book.issued + 1
        db.session.commit()
        return 200, Issued.query.get(issued.id).serialize

def bookReturn(id):
    issued = Issued.query.get(id)
    if issued is None:
        return 400, "Wrong Issue ID"
    else:
        issued.status = False
        issued.update
        issued.returned = datetime.datetime.now()
        book = Books.query.get(issued.book_id)
        book.issued -= 1
        member = Members.query.get(issued.member_id)
        member.credit -= (issued.rent - INIT_RENT)
        db.session.commit()
        return 200, issued.serialize

@member.route('/')
def index():
    if "logged_in" in session:
        return render_template('members/index.html', users=Members.query.all())
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@member.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if "logged_in" in session: 
        if request.method == 'GET':
            transactions=Issued.query.all()
            for t in transactions:
                t.update
            return render_template('members/transactions.html', transactions=transactions)
        else:
            params = json.loads(request.data)
            status = params['status']
            if status:
                member_id = params['member_id']
                book_id = params['book_id']
                code, msg = issue(member_id, book_id)
            else:
                id = params['id']
                code, msg = bookReturn(id)
        
            return jsonify(msg=msg, code=code), 200
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@member.route('/member/<int:id>')
def details(id):
    if "logged_in" in session:
        user = Members.query.get(id)
        for issue in user.books:
            issue.update
        return render_template('members/member.html', user=user)
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@member.route('/payments', methods=['GET', 'POST'])
def payments():
    if "logged_in" in session:
        if request.method == "GET":
            return render_template('members/payments.html', payments=Payment.query.all())
        else:
            params = json.loads(request.data)
            amount = int(params['amount'])
            member_id = params['id']
            member = Members.query.get(member_id)
            if not member or amount < 100:
                return jsonify(msg="Payment UnSuccessful", code=404), 404
            member.payments.append(Payment(member_id, amount))
            db.session.commit()
            return jsonify(msg="Payment Successful", payment=member.payments[-1].serialize, code=200), 200
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))

@member.route('/add', methods=['GET', 'POST'])
def newUser():
    if "logged_in" in session:
        if request.method == 'POST':
            params = json.loads(request.data)
            new = {
            'name':params['name'],
            'email':params['email'],
            'credit':0
            }    
            try:
                new_member = Members(new)
                db.session.add(new_member)
                db.session.commit()
                member = Members.query.get(new_member.id)
                member.payments.append(Payment(new_member.id, int(params['credit'])))
                db.session.commit()
                return jsonify(user=member.serialize, result=200), 200
            except:
                return jsonify(result="User Email '{}' already Exists".format(new['email'])), 200
        else:
            return render_template('members/newuser.html')
    else:
        return redirect(url_for('views.index', error="Please login to view this page."))