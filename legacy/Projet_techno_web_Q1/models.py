from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from .database import db


class Account(UserMixin, db.Model):
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(20), unique=True)
    passwd_hash = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    bday = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean(), default=False, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    blogs = db.relationship("Blog", backref="written by", lazy="dynamic")
    reports = db.relationship("Reports", backref="reported by", lazy="dynamic")

    def isBirthday(self):
        if self.bday.replace(year=date.today().year) == date.today():
            return True
        return False

    def set_password(self, passwd):
        self.passwd_hash = generate_password_hash(passwd)

    def check_password(self, passwd):
        return check_password_hash(self.passwd_hash, passwd)

    def __repr__(self):
        return f"Email: {self.id}\nUsername: {self.username}\n\
            Last Name: {self.last_name}\nFirst Name: {self.first_name}\n\
                Birthday: {self.bday}\n\
                    Is admin? {self.is_admin}\nIs active? {self.active}\n"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column(db.Integer)
    message = db.Column(db.String(500))
    date = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Integer, default=4, nullable=False)
    Account_email = db.Column(db.Integer, db.ForeignKey("account.id"))
    Media_id = db.Column(db.Integer, db.ForeignKey("media.id"))
    __table_args__ = (db.UniqueConstraint(Account_email, Media_id, name="IDBLOG"),)
    reports = db.relationship("Reports", backref="reports blog", lazy="dynamic")

    def __repr__(self):
        return f"ID: {self.id}\nDate: {self.date}\n\
            Media ID: {self.Media_id}\nRating: {self.rating}\n\
            Message: {self.message}\nby {self.Account_email}\n"


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    blogs = db.relationship("Blog", backref="about", lazy="dynamic")
    reports = db.relationship("Reports", backref="reports media", lazy="dynamic")
    series = db.relationship("Series", backref="series", lazy="dynamic")
    plays_in = db.relationship("Plays_in", backref="people plays in", lazy="dynamic")
    directed_by = db.relationship(
        "Directed_by", backref="person directs", lazy="dynamic"
    )

    def __repr__(self):
        series = Series.query.filter_by(id=self.id).first()
        if series is None:
            return f"Film ID: {self.id}\nTitle: {self.title}\nYear: {self.year}\n\
                Duration: {self.duration}\nCategory: {self.category}\n"
        if series.year_end is None:
            s = f"Series ID: {self.id}\nTitle: {self.title}\nYear: {self.year}\n"
        else:
            s = f"Series ID: {self.id}\nTitle: {self.title}\n\
                Year range: {self.year}-{series.year_end}\n"
        if series.duration2 is None:
            s = s + f"Duration: {self.duration}\nCategory: {self.category}\n"
        else:
            s = (
                s
                + f"Duration : {self.duration}-{series.duration2}\n\
                    Category: {self.category}\n"
            )
        return s


class Series(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("media.id"), primary_key=True)
    duration2 = db.Column(db.Integer)
    year_end = db.Column(db.Integer)
    no_episodes = db.Column(db.Integer, nullable=False)
    no_seasons = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        media = Media.query.filter_by(id=self.id).first()
        if self.year_end is None:
            s = f"Series ID: {self.id}\nTitle: {media.title}\nYear: {media.year}\n"
        else:
            s = f"Series ID: {self.id}\nTitle: {media.id}\n\
                Year range: {media.year}-{self.year_end}\n"
        if self.duration2 is None:
            s = s + f"Duration: {media.duration}\nCategory: {media.category}\n"
        else:
            s = (
                s
                + f"Duration: {media.duration}-{self.duration2}\n\
                Category: {media.category}\n"
            )
        return s


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    bday = db.Column(db.Date, nullable=False)
    plays_in = db.relationship("Plays_in", backref="plays in media", lazy="dynamic")
    directed_by = db.relationship(
        "Directed_by", backref="media directed by", lazy="dynamic"
    )

    def __repr__(self):
        return f"People ID: {self.id}\nLast Name: {self.last_name}\n\
            First Name: {self.first_name}\nBirthday: {self.bday}\n"


class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(300), nullable=True)
    Account_email = db.Column(
        db.String(50), db.ForeignKey("account.id"), nullable=False
    )
    Media_id = db.Column(db.Integer, db.ForeignKey("media.id"))
    People_id = db.Column(db.Integer, db.ForeignKey("blog.id"))

    def __repr__(self):
        if self.Blog_id is None and self.Media_id is None:
            return f"ERROR: Constraint exact-1 not respected (both NULL).\n"
        if self.Blog_id is None:
            return f"Report ID: {self.id}\nMessage: {self.message}\
                by {self.Account_email}\nMedia ID: {self.Media_id}"
        if self.Media_id is None:
            return f"Report ID: {self.id}\nMessage: {self.message}\
                by {self.Account_email}\nBlog ID: {self.Blog_id}"
        return f"ERROR: Constraint exact-1 not respected (both NOT NULL).\n"


class Plays_in(db.Model):
    Media_id = db.Column(db.Integer, db.ForeignKey("media.id"), primary_key=True)
    People_id = db.Column(db.Integer, db.ForeignKey("people.id"), primary_key=True)


class Directed_by(db.Model):
    Media_id = db.Column(db.Integer, db.ForeignKey("media.id"), primary_key=True)
    People_id = db.Column(db.Integer, db.ForeignKey("people.id"), primary_key=True)
