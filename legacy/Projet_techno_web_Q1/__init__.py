from .app import app
from .login_manager import login_manager
from .database import db
from .routes import flixlist_app
from .models import *
from datetime import date, timedelta, datetime

app.register_blueprint(flixlist_app)


with app.app_context():
    # db.drop_all()
    db.create_all()
    if Account.query.filter_by(id="admin").first() is None:
        admin = Account(
            id="admin",
            is_admin=True,
            last_name="Daddy",
            first_name="Big",
            bday=date.today() - timedelta(days=1),
        )
        admin.set_password("admin")
        db.session.add(admin)
    if Account.query.filter_by(id="jean-marie.duquet@flixmail.be").first() is None:
        user = Account(
            id="jean-marie.duquet@flixmail.be",
            last_name="Duquet",
            first_name="Jean-Marie",
            bday=date(1963, 7, 27),
        )
        user.set_password("Teknik2progra")
        db.session.add(user)
    if Account.query.filter_by(id="didier.deschamps@todo.app").first() is None:
        user = Account(
            id="didier.deschamps@todo.app",
            last_name="Deschamps",
            first_name="Didier",
            username="didierdu974",
            bday=date(1970, 5, 4),
        )
        user.set_password("Didiernumero1")
        db.session.add(user)
    if Media.query.filter_by(id=0).first() is None:
        film = Media(
            id=0,
            title="The Silence of the Lambs",
            year=1991,
            duration=118,
            category="psychological horror",
            description="A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims.",
        )
        db.session.add(film)
    if People.query.filter_by(id=0).first() is None:
        person = People(
            id=0,
            first_name="Jonathan",
            last_name="Demme",
            bday=date(1944, 2, 22),
        )
        db.session.add(person)
    if Directed_by.query.filter_by(Media_id=0, People_id=0).first() is None:
        director = Directed_by(Media_id=0, People_id=0)
        db.session.add(director)
    if People.query.filter_by(id=1).first() is None:
        person = People(
            id=1,
            first_name="Jodie",
            last_name="Foster",
            bday=date(1962, 11, 19),
        )
        db.session.add(person)
    if People.query.filter_by(id=2).first() is None:
        person = People(
            id=2,
            first_name="Anthony",
            last_name="Hopkins",
            bday=date(1937, 12, 31),
        )
        db.session.add(person)
    if Plays_in.query.filter_by(Media_id=0, People_id=1).first() is None:
        actress = Plays_in(Media_id=0, People_id=1)
        db.session.add(actress)
    if Plays_in.query.filter_by(Media_id=0, People_id=2).first() is None:
        actor = Plays_in(Media_id=0, People_id=2)
        db.session.add(actor)
    if Blog.query.filter_by(id=0).first() is None:
        review = Blog(
            id=0,
            rating=5,
            message="A must-watch classic.",
            state=0,
            Account_email="admin",
            Media_id=0,
            date=datetime.now(),
        )
        db.session.add(review)

    if Account.query.filter_by(id="cookies@chocolat.pepitte").first() is None:
        user = Account(
            id="cookies@chocolat.pepitte",
            last_name="Chocolat",
            first_name="Cookies",
            username="Cooky",
            bday=date(2009, 12, 8),
        )
        user.set_password("cookies")
        db.session.add(user)

    if Media.query.filter_by(id=1).first() is None:
        film2 = Media(
            id=1,
            title="Maléfique",
            year=2014,
            duration=1,
            category="Fantasy",
            description="Maleficent has an idyllic life in a forest kingdom....",
        )
        db.session.add(film2)
    if People.query.filter_by(id=3).first() is None:
        people = People(
            id=3,
            first_name="Angelina",
            last_name="Jolie",
            bday=date(1975, 6, 4),
        )
        db.session.add(people)
    if Plays_in.query.filter_by(Media_id=1, People_id=3).first() is None:
        Angfilm = Plays_in(
            Media_id=1,
            People_id=3,
        )
        db.session.add(Angfilm)
    if People.query.filter_by(id=4).first() is None:
        director = People(
            id=4,
            first_name="Robert",
            last_name="Stromberg",
            bday=date(1965, 1, 1),
        )
        db.session.add(director)
    if Directed_by.query.filter_by(Media_id=1, People_id=4).first() is None:
        direct_by = Directed_by(
            Media_id=1,
            People_id=4,
        )
        db.session.add(direct_by)

    if Blog.query.filter_by(id=1).first() is None:
        blog = Blog(
            id=1,
            rating=3,
            message="elle est jolie angelina jolie",
            Account_email="didier.deschamps@todo.app",
            Media_id=1,
            date=datetime.now(),
        )
        db.session.add(blog)
    if Media.query.filter_by(id=2).first() is None:
        film3 = Media(
            id=2,
            title="The Goonies",
            year=1985,
            duration=114,
            category="Adventure",
            description="A group of young misfits called The Goonies discover an ancient map and set out on an adventure to find a legendary pirate's long-lost treasure.",
        )
        db.session.add(film3)
    if Media.query.filter_by(id=3).first() is None:
        film4 = Media(
            id=3,
            title="Game of thrones",
            year=2011,
            duration=60,
            category="fantasy",
            description="ça se tape.",
        )
        db.session.add(film4)
        db.session.commit
        serie4 = Series(
            id=film4.id, duration2=80, year_end=2019, no_episodes=73, no_seasons=8
        )
        db.session.add(serie4)
        db.session.commit()
    if Plays_in.query.filter_by(Media_id=3, People_id=3).first() is None:
        Angfilm = Plays_in(
            Media_id=3,
            People_id=3,
        )
        db.session.add(Angfilm)
    if People.query.filter_by(id=5).first() is None:
        director = People(
            id=5,
            first_name="George R.R",
            last_name="Martin",
            bday=date(1948, 9, 20),
        )
        db.session.add(director)
    if Directed_by.query.filter_by(Media_id=3, People_id=5).first() is None:
        direct_by = Directed_by(
            Media_id=3,
            People_id=5,
        )
        db.session.add(direct_by)
    db.session.commit()
    if Directed_by.query.filter_by(Media_id=1, People_id=5).first() is None:
        direct_by = Directed_by(
            Media_id=1,
            People_id=5,
        )
        db.session.add(direct_by)
    db.session.commit()
