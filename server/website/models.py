from . import db
from sqlalchemy.sql import func, select
import datetime
INIT_RENT = 100
DAILY_RENT = 25
class Books(db.Model):
    __tablename__ = 'books'
    id       = db.Column(db.Integer, primary_key=True)
    isbn     = db.Column(db.String, nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    issued   = db.Column(db.Integer, nullable=False, default=0)
    title    = db.Column(db.String(100), nullable=False)
    author   = db.Column(db.String(100), nullable=False)
    book_id  = db.Column(db.Integer, nullable=False)
    added    = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now(), nullable=False)

    def __init__(self, book, quantity):
        self.isbn = book['isbn']
        self.quantity = quantity
        self.title = book['title']
        self.author = book['authors']
        self.book_id = book['bookID']

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id'     : self.id,
           'title'   : self.title,
           'isbn'  : self.isbn,
           'unique id': self.book_id,
           'quantity':self.quantity,
           'added': self.added.date()
       }

class Members(db.Model):
    __tablename__ = 'members'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(100), nullable=False, unique=True)
    credit   = db.Column(db.Integer, nullable=False)
    payments = db.relationship('Payment',backref='Members', lazy='dynamic')
    books    = db.relationship('Issued',backref='Members', lazy='dynamic')
    created  = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now(), nullable=False)


    def __init__(self, member):
        self.name = member['name']
        self.email = member['email']
        self.credit = member['credit']

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id'         : self.id,
           'name'       : self.name,
           'email'      : self.email,
           'credit'     : self.credit
       }

class Issued(db.Model):
    __tablename__ = 'issued'
    id       = db.Column(db.Integer, primary_key=True)
    member_id  = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    book_id  = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issued = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now(), nullable=False)
    returned = db.Column(db.DateTime(timezone=True))
    updated = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now() )
    status = db.Column(db.Boolean, nullable=False, default=True)
    rent  = db.Column(db.Integer, default=INIT_RENT, nullable=False)

    def __init__(self, member, book):
        self.member_id = member
        self.book_id = book

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id'         : self.id,
           'member'       : self.member_id,
           'book'  : self.book_id,
           'status': self.status,
           'issued' : self.issued, 
           'rent': self.rent
       }

    @property
    def update(self):
        if self.status:
            now = datetime.datetime.now() 
            if self.updated.date() != now.date():
                self.rent += (now.date() - self.issued.date()).days * DAILY_RENT
                self.updated = now
                db.session.commit()
class Payment(db.Model):
    __tablename__ = 'payment'
    id       = db.Column(db.Integer, primary_key=True)
    member_id  = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now(), nullable=False)

    def __init__(self, id, amount):
        self.amount = amount
        member = Members.query.filter_by(id=id).first()
        member.credit = member.credit + amount
        db.session.commit()

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id'         : self.id,
           'member_id'       : self.member_id,
           'amount' : self.amount, 
           'date': self.date
       }
