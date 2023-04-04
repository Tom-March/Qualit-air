from functools import wraps
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    abort,
    jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from werkzeug.exceptions import HTTPException  # will use this for errorhandling
from .forms import (
    ALLOWED_EXTENSIONS,
    RegisterForm,
    LoginForm,
    FilmForm,
    SeriesForm,
    PeopleForm,
    BlogForm,
    EditProfileForm,
    EditProfilePasswordForm,
)
from .models import Account, Blog, Media, Series, People, Reports, Plays_in, Directed_by
from .database import db
import datetime as dt
import os

htmlExceptionMessages = {"404": "The page you’re looking for doesn’t exist."}

# custom decorators
def user_active(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and not current_user.active:
            return abort(403, "Your account has been disabled.")
        return func(*args, **kwargs)

    return decorated_view


def admin_only(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            return abort(403, "You don't have authorization to view this page.")
        return func(*args, **kwargs)

    return decorated_view


def anon(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("flixlist.root"))
        return func(*args, **kwargs)

    return decorated_view


# code from http://flask.pocoo.org/snippets/62/
# wayback machine link: https://web.archive.org/web/20120517003641/http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form["next"]
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


# get picture in local file
def get_picture(type, id):
    current_folder = os.getcwd()
    list_pictures = os.listdir(current_folder + "\my_app\static\img\%s" % type)
    for file in list_pictures:
        filerpartitioned = file.rpartition(".")
        if filerpartitioned[0] == str(id):
            return file
    return None


flixlist_app = Blueprint("flixlist", __name__)


@flixlist_app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template(
        "error.html",
        status_code=e.code,
        status_name=e.name,
        description=e.description,
    )


# main page, displays user list
@flixlist_app.route("/")
@user_active
def root():
    media = Media.query.all()
    blogs = Blog.query.all()
    dict_pictures = {}
    for apieceofmedia in media:
        dict_pictures[apieceofmedia.id] = get_picture("media", apieceofmedia.id)
    return render_template(
        "list.html", medias=media, blogs=blogs, pictures=dict_pictures
    )


@flixlist_app.route("/search")
@user_active
def searchbar():
    all_media = Media.query.all()
    dict_pictures = {}
    for eachmedia in all_media:
        dict_pictures[eachmedia.id] = get_picture("media", eachmedia.id)
    return render_template("search.html", medias=all_media, pictures=dict_pictures)


@flixlist_app.route("/searchreview")
@user_active
def searchreview():
    all_blogs = Blog.query.all()
    all_users = Account.query.all()
    all_media = Media.query.all()
    info_review = {}
    for user in all_users:
        for blog in all_blogs:
            if user.id == blog.Account_email:
                info_user = [user.first_name, user.last_name, user.username, user.id]
                info_review[blog.id] = info_user
    for media in all_media:
        for blog in all_blogs:
            if media.id == blog.Media_id:
                info_review[blog.id].append(media.title)
    return render_template(
        "searchreview.html", blogs=all_blogs, info_review=info_review
    )


@flixlist_app.route("/searchpeople")
@user_active
def searchafriend():
    people = People.query.all()
    dict_pictures = {}
    for person in people:
        dict_pictures[person.id] = get_picture("people", person.id)
    return render_template("searchpeople.html", people=people, pictures=dict_pictures)


@flixlist_app.route("/searchuser")
@user_active
def searchuser():
    users = Account.query.all()
    dict_pictures = {}
    for eachUser in users:
        dict_pictures[eachUser.id] = get_picture("profile", eachUser.id)
    return render_template("searchusers.html", users=users, pictures=dict_pictures)


@flixlist_app.route("/media/<int:id>")
@user_active
def mediapage(id):
    media = Media.query.filter_by(id=id).first()
    if media is None:
        abort(404, htmlExceptionMessages["404"])
    file = get_picture("media", id)
    if current_user.is_authenticated:
        user_blog_id = Blog.query.filter_by(
            Media_id=id, Account_email=current_user.id
        ).first()
        if user_blog_id is not None:
            user_blog_id = user_blog_id.id
        else:
            user_blog_id = -1
    else:
        user_blog_id = -1
    reviews = Blog.query.filter_by(Media_id=id).all()
    series = Series.query.filter_by(id=id).first()
    directors = Directed_by.query.filter_by(Media_id=id).all()
    len_dir = len(directors)
    directors_people = []
    last_dir = 0
    if len_dir > 0:
        for director in directors:
            directors_people.append(
                People.query.filter_by(id=director.People_id).first()
            )
        last_dir = directors_people[len_dir - 1]
    actors = Plays_in.query.filter_by(Media_id=id).all()
    actors_people = []
    len_actors = len(actors)
    last_actor = 0
    if len_actors > 0:
        for actor in actors:
            actors_people.append(People.query.filter_by(id=actor.People_id).first())
        last_actor = actors_people[len_actors - 1]
    return render_template(
        "media.html",
        media=media,
        reviews=reviews,
        series=series,
        picture=file,
        id=id,
        last_dir=last_dir,
        last_actor=last_actor,
        len_dir=len_dir,
        len_actors=len_actors,
        directors_people=directors_people,
        actors_people=actors_people,
        user_blog_id=user_blog_id,
    )


@flixlist_app.route("/people/<int:id>")
@user_active
def peoplepage(id):
    person = People.query.filter_by(id=id).first()
    if person is None:
        abort(404, htmlExceptionMessages["404"])
    file = get_picture("people", id)
    medias_dir = []
    medias_plays = []
    directed = Directed_by.query.filter_by(People_id=id).all()
    if directed is not None:
        for media in directed:
            medias_dir.append(Media.query.filter_by(id=media.Media_id).first())
    plays = Plays_in.query.filter_by(People_id=id).all()
    if plays is not None:
        for media in plays:
            medias_plays.append(Media.query.filter_by(id=media.Media_id).first())
    return render_template(
        "people.html",
        people=person,
        media_dir=medias_dir,
        media_plays=medias_plays,
        picture=file,
        today=dt.date.today(),
    )


@flixlist_app.route("/media/<int:id>/reviews")
@user_active
def mediamessages(id):
    media = Media.query.filter_by(id=id).first()
    if media is None:
        abort(404, htmlExceptionMessages["404"])
    user_reviews = Blog.query.filter_by(Media_id=id).all()
    usernames = {}
    for user in user_reviews:
        dudesaccount = Account.query.filter_by(id=user.Account_email).first()
        if dudesaccount.username is not None:
            usernames[user.Account_email] = dudesaccount.username
        else:
            usernames[user.Account_email] = (
                dudesaccount.first_name + " " + dudesaccount.last_name
            )
    return render_template(
        "messages.html",
        type="media",
        media=media,
        user_reviews=user_reviews,
        usernames=usernames,
    )


@flixlist_app.route("/user/<username>")
@user_active
def anotheruserprofile(username):
    user = Account.query.filter_by(username=username).first()
    if user is None:
        user = Account.query.filter_by(id=username).first()
    if user is None:
        abort(404, htmlExceptionMessages["404"])
    file = get_picture("profile", user.id)
    statistics = [0, 0, 0, 0, 0]
    user_list = Blog.query.filter_by(Account_email=user.id).all()
    if user_list is not None and not len(user_list) == 0:
        total = len(user_list)
        for element in user_list:
            statistics[element.state] += 1
        for idx, eachStat in enumerate(statistics):
            statistics[idx] = (eachStat / total) * 100
    return render_template(
        "profile.html",
        picture=file,
        stats=statistics,
        actual_user=user,
        real_current_user=False,
        username=username,
    )


@flixlist_app.route("/user/<username>/posts")
@user_active
def usermessages(username):
    user = Account.query.filter_by(username=username).first()
    if user is None:
        user = Account.query.filter_by(id=username).first()
    if user is None:
        abort(404, htmlExceptionMessages["404"])
    user_posts = Blog.query.filter_by(Account_email=user.id).all()
    media_titles = {}
    for post in user_posts:
        media_titles[post.id] = Media.query.filter_by(id=post.Media_id).first()
    return render_template(
        "messages.html",
        type="user",
        user=user,
        user_posts=user_posts,
        media_titles=media_titles,
        username=username,
    )


@flixlist_app.route("/media/add", methods=["GET", "POST"])
@login_required
@user_active
def addmedia():
    filmForm = FilmForm()
    seriesForm = SeriesForm()
    if request.method == "GET":
        return render_template(
            "addmedia.html", filmForm=filmForm, seriesForm=seriesForm
        )
    requestForm = request.form
    formType = requestForm["currentForm"]
    if formType == "film":
        for attr in requestForm:
            if not attr == "currentForm" and not attr == "next":
                if attr in ["year", "duration"]:
                    try:
                        filmForm[attr].data = int(requestForm[attr])
                    except ValueError:
                        pass
                else:
                    filmForm[attr].data = requestForm[attr].strip()
        if not filmForm.validate_on_submit():
            return jsonify({"redirect": None, "form": filmForm.errors})
        new_media = Media(
            title=filmForm.title.data,
            description=filmForm.description.data,
            year=filmForm.year.data,
            duration=filmForm.duration.data,
            category=filmForm.cat.data,
        )
        db.session.add(new_media)
        db.session.commit()
        # Save the upload file into the server
        f = filmForm.upload.data
        if f is not None:
            extension = f.filename.split(".")[-1]
            name = "%d.%s" % (new_media.id, extension)
            f.save(os.path.join("./my_app/static/img/media", name))
        flash("Film added successfully.")
    elif formType == "series":
        for attr in requestForm:
            if not attr == "currentForm" and not attr == "next":
                if attr == "no_seasons" or attr == "no_episodes":
                    try:
                        seriesForm[attr].data = int(requestForm[attr])
                    except ValueError:
                        pass
                else:
                    seriesForm[attr].data = requestForm[attr].strip()
        if not seriesForm.validate_on_submit():
            return jsonify({"redirect": None, "form": seriesForm.errors})
        year = seriesForm.year.data.split("-")
        if len(year) == 1:
            year.append(None)
        else:
            if year[0] == year[1]:
                year[1] = None
        duration = seriesForm.duration.data.split("-")
        if len(duration) == 1:
            duration.append(None)
        elif duration[0] == duration[1]:
            duration[1] = None
        new_media = Media(
            title=seriesForm.title.data,
            description=seriesForm.description.data,
            year=year[0],
            duration=duration[0],
            category=seriesForm.cat.data,
        )
        db.session.add(new_media)
        db.session.commit()
        new_series = Series(
            id=new_media.id,
            duration2=duration[1],
            year_end=year[1],
            no_episodes=seriesForm.no_episodes.data,
            no_seasons=seriesForm.no_episodes.data,
        )
        db.session.add(new_series)
        db.session.commit()
        # Save the upload file into the server
        f = seriesForm.upload.data
        if f is not None:
            extension = f.filename.split(".")[-1]
            name = "%d.%s" % (new_media.id, extension)
            f.save(os.path.join("./my_app/static/img/media", name))
        flash("Series added successfully.")
    else:
        abort(418)
    return jsonify(
        {"redirect": url_for("flixlist.mediapage", id=new_media.id), "form": None}
    )


@flixlist_app.route("/people/add", methods=["GET", "POST"])
@login_required
@user_active
def addpeople():
    form = PeopleForm()
    if request.method == "GET":
        return render_template("addPeople.html", peopleForm=form)
    requestForm = request.form
    for attr in requestForm:
        if not attr == "next":
            form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})
    newpeople = People(
        first_name=form.firstName.data,
        last_name=form.lastName.data,
        bday=dt.datetime.strptime(form.bday.data, "%Y-%m-%d").date(),
    )
    db.session.add(newpeople)
    db.session.commit()
    # Save the upload file into the server
    f = form.upload.data
    if f is not None:
        extension = f.filename.split(".")[-1]
        name = "%d.%s" % (newpeople.id, extension)
        f.save(os.path.join("./my_app/static/img/people", name))
    flash("Person added successfully.")
    return jsonify(
        {"redirect": url_for("flixlist.peoplepage", id=newpeople.id), "form": None}
    )


@flixlist_app.route("/profile")
@login_required
@user_active
def userprofile():
    file = get_picture("profile", current_user.id)
    statistics = [0, 0, 0, 0, 0]
    user_list = Blog.query.filter_by(Account_email=current_user.id).all()
    if user_list is not None and not len(user_list) == 0:
        total = len(user_list)
        for element in user_list:
            statistics[element.state] += 1
        for idx, eachStat in enumerate(statistics):
            statistics[idx] = (eachStat / total) * 100
    return render_template(
        "profile.html",
        picture=file,
        stats=statistics,
        real_current_user=True,
        actual_user=current_user,
    )


@flixlist_app.route("/profile/edit", methods=["GET", "POST"])
@login_required
@user_active
def editprofile():
    editForm = EditProfileForm()
    if request.method == "GET":
        file = get_picture("profile", current_user.id)
        return render_template("profile_edit.html", form=editForm, picture=file)
    requestForm = request.form
    for attr in requestForm:
        editForm[attr].data = requestForm[attr].strip()
    if not editForm.validate_on_submit():
        return jsonify({"redirect": None, "form": editForm.errors})
    editForm_email_data = editForm.email.data.lower()
    if not current_user.id == editForm_email_data:
        # rename profile pic filename upon email change by the user
        for allowed_extension in ALLOWED_EXTENSIONS:
            old_filename = "%s.%s" % (current_user.id, allowed_extension)
            old_filepath = os.path.join("./my_app/static/img/profile", old_filename)
            new_filename = "%s.%s" % (editForm_email_data, allowed_extension)
            new_filepath = os.path.join("./my_app/static/img/profile", new_filename)
            if os.path.isfile(old_filepath):
                os.rename(old_filepath, new_filepath)
        current_user_blog = Blog.query.filter_by(Account_email=current_user.id).all()
        for message in current_user_blog:
            message.Account_email = editForm_email_data
            db.session.add(message)
        current_user_reports = Reports.query.filter_by(
            Account_email=current_user.id
        ).all()
        for report in current_user_reports:
            report.Account_email = editForm_email_data
            db.session.add(report)
    current_user.id = editForm_email_data
    if not editForm.username.data:
        current_user.username = None
    else:
        current_user.username = editForm.username.data
    current_user.last_name = editForm.lastName.data
    current_user.first_name = editForm.firstName.data
    current_user.bday = dt.datetime.strptime(editForm.bday.data, "%Y-%m-%d").date()
    db.session.commit()
    f = editForm.upload.data
    if f is not None:
        # remove previous profile picture
        for allowed_extension in ALLOWED_EXTENSIONS:
            filename = "%s.%s" % (current_user.id, allowed_extension)
            filepath = os.path.join("./my_app/static/img/profile", filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        # upload new one
        extension = f.filename.rpartition(".")[2]
        file_name = "%s.%s" % (current_user.id, extension)
        file_path = os.path.join("./my_app/static/img/profile", file_name)
        f.save(file_path)
    login_user(current_user, remember=True, force=True)
    flash("Profile updated successfully.")
    return jsonify({"redirect": url_for("flixlist.userprofile"), "form": None})


@flixlist_app.route("/profile/edit/password", methods=["GET", "POST"])
@login_required
@user_active
def editprofilepassword():
    editPasswordForm = EditProfilePasswordForm()
    if request.method == "GET":
        file = get_picture("profile", current_user.id)
        return render_template(
            "profile_edit_password.html", form=editPasswordForm, picture=file
        )
    requestForm = request.form
    for attr in requestForm:
        editPasswordForm[attr].data = requestForm[attr].strip()
    if not editPasswordForm.validate_on_submit():
        return jsonify({"redirect": None, "form": editPasswordForm.errors})
    if not current_user.check_password(editPasswordForm.current_passwd.data):
        return jsonify(
            {"redirect": None, "form": {"current_passwd": ["Wrong password."]}}
        )
    current_user.set_password(editPasswordForm.new_passwd.data)
    db.session.commit()
    flash("Password changed successfully.")
    return jsonify({"redirect": url_for("flixlist.userprofile"), "form": None})


@flixlist_app.route("/profile/posts")
@login_required
@user_active
def myposts():
    my_posts = Blog.query.filter_by(Account_email=current_user.id).all()
    my_blog = {}
    for eachPost in my_posts:
        corresponding_media = Media.query.filter_by(id=eachPost.Media_id).first()
        my_blog[eachPost.id] = corresponding_media
    return render_template(
        "messages.html",
        type="user",
        user=current_user,
        user_posts=my_posts,
        media_titles=my_blog,
    )


@flixlist_app.route("/admin", methods=["GET", "POST"])
@login_required
@user_active
@admin_only
def adminboard():
    users_admin = []
    users_normal = []
    users = Account.query.filter(Account.id != current_user.id).all()
    for user in users:
        if user.is_admin:
            users_admin.append(user)
        else:
            users_normal.append(user)
    dict_pictures = {}
    for user in users:
        dict_pictures[user.id] = get_picture("profile", user.id)
    return render_template(
        "admin.html",
        users_admin=users_admin,
        users_normal=users_normal,
        all_users=users,
        pictures=dict_pictures,
    )


@flixlist_app.route("/admin/reports")
@login_required
@user_active
@admin_only
def flags():
    all_flags_media = Reports.query.filter_by(People_id=None).all()
    all_flags_people = Reports.query.filter_by(Media_id=None).all()
    all_media = Media.query.all()
    all_peoples = People.query.all()
    media_title = {}
    media_ids = {}
    for media in all_media:
        for flag in all_flags_media:
            if media.id == flag.Media_id:
                media_title[flag.id] = media.title
                media_ids[flag.id] = media.id
    people_name = {}
    people_ids = {}
    for people in all_peoples:
        for flag in all_flags_people:
            if people.id == flag.People_id:
                people_name[flag.id] = people.first_name + " " + people.last_name
                people_ids[flag.id] = people.id
    return render_template(
        "flags.html",
        reports_media=all_flags_media,
        reports_people=all_flags_people,
        media_title=media_title,
        media_ids=media_ids,
        people_name=people_name,
        people_ids=people_ids,
    )


@flixlist_app.route("/admin/report/completed/<int:id>")
@login_required
@user_active
@admin_only
def completeflags(id):
    report = Reports.query.filter_by(id=id).first()
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for("flixlist.flags"))


@flixlist_app.route("/admin/action", methods=["GET", "POST"])
@login_required
@user_active
@admin_only
def adminaction():
    if request.method == "GET":
        return redirect(url_for("flixlist.adminboard"))
    action = request.form["action"]
    user_id = request.form["id"]
    user = Account.query.filter_by(id=user_id).first()
    if action == "block":
        user.active = not user.active
        db.session.commit()
        return jsonify({"is_active": user.active})
    elif action == "change_group":
        user.is_admin = not user.is_admin
        db.session.commit()
        return jsonify({"is_admin": user.is_admin})
    return


@flixlist_app.route("/signin", methods=["GET", "POST"])
@anon
def login():
    form = LoginForm()
    next = get_redirect_target()
    if next == url_for("flixlist.logout"):
        next = None
    if request.method == "GET":
        return render_template("login.html", form=form, next=next)
    requestForm = request.form
    for attr in requestForm:
        if not attr == "next":
            form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})
    user = Account.query.filter_by(id=form.email.data.lower()).first()
    if user is None or not user.check_password(form.passwd.data):
        # Incorrect username or password.
        error_login = {"error_login": ["Incorrect email or password."]}
        return jsonify({"redirect": None, "form": error_login})
    login_user(user, remember=True, force=True)
    flash("Logged in successfully.")
    return jsonify({"redirect": next, "form": None})


@flixlist_app.route("/signup", methods=["GET", "POST"])
@anon
def register():
    form = RegisterForm()
    next = get_redirect_target()
    if next == url_for("flixlist.logout"):
        next = None
    if request.method == "GET":
        return render_template("register.html", form=form)
    requestForm = request.form
    for attr in requestForm:
        if not attr == "next":
            form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})
    if not form.username.data:
        form.username.data = None
    new_account = Account(
        id=form.email.data.lower(),
        username=form.username.data,
        last_name=form.lastName.data,
        first_name=form.firstName.data,
        bday=dt.datetime.strptime(form.bday.data, "%Y-%m-%d").date(),
    )
    new_account.set_password(form.passwd.data)
    db.session.add(new_account)
    db.session.commit()
    # Save the upload file into the server
    f = form.upload.data
    if f is not None:
        extension = f.filename.split(".")[-1]
        name = "%s.%s" % (form.email.data.lower(), extension)
        f.save(os.path.join("./my_app/static/img/profile", name))
    login_user(new_account, remember=True, force=True)
    flash("Logged in successfully.")
    return jsonify({"redirect": next, "form": None})


@flixlist_app.route("/signout")
@login_required
def logout():
    logout_user()
    next = get_redirect_target()
    return redirect(next)


@flixlist_app.route("/blog/add/<int:mediaId>", methods=["GET", "POST"])
@login_required
@user_active
def addblog(mediaId):
    form = BlogForm()
    if request.method == "GET":
        get_blog = Blog.query.filter_by(
            Account_email=current_user.id, Media_id=mediaId
        ).first()
        if get_blog is not None:
            return redirect(url_for("flixlist.modifyblog", id=get_blog.id))
        return render_template("addblog.html", BlogForm=form, mediaId=mediaId)
    requestForm = request.form
    for attr in requestForm:
        if not attr == "next":
            if attr in ["rating", "state"]:
                try:
                    form[attr].data = int(requestForm[attr])
                except ValueError:
                    pass
            else:
                form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})
    newblog = Blog(
        rating=form.rating.data,
        message=form.message.data,
        state=form.state.data,
        Media_id=mediaId,
        Account_email=current_user.id,
        date=dt.datetime.now(),
    )
    db.session.add(newblog)
    db.session.commit()
    return jsonify(
        {"redirect": url_for("flixlist.mediamessages", id=mediaId), "form": None}
    )


@flixlist_app.route("/list/add/<int:mediaId>", methods=["POST"])
@login_required
@user_active
def addlist(mediaId):
    new_blog = Blog(
        Account_email=current_user.id,
        Media_id=mediaId,
        message="",
        date=dt.datetime.now(),
    )
    db.session.add(new_blog)
    db.session.commit()
    return redirect(url_for("flixlist.root"))


@flixlist_app.route("/list/check_add", methods=["POST"])
@user_active
def get_blog_current():
    if current_user.is_authenticated:
        user_blog_list = Blog.query.filter_by(Account_email=current_user.id).all()
    else:
        user_blog_list = []
    user_idblog_list = []
    for blog in user_blog_list:
        user_idblog_list.append(blog.Media_id)
    media_query = Media.query.all()
    mediaIdList = []
    for eachMedia in media_query:
        mediaIdList.append(eachMedia.id)
    return jsonify({"id_media_user": user_idblog_list, "media_query": mediaIdList})


@flixlist_app.route("/blog/modify/<int:id>", methods=["GET", "POST"])
@login_required
@user_active
def modifyblog(id):
    blog = Blog.query.filter_by(id=id).first()
    if blog is None:
        abort(404, htmlExceptionMessages["404"])
    form = BlogForm()
    if request.method == "GET":
        return render_template(
            "modifyblog.html",
            BlogForm=form,
            id=id,
            rating=blog.rating,
            message=blog.message,
            state=blog.state,
        )
    requestForm = request.form
    for attr in requestForm:
        if not attr == "next":
            if attr in ["rating", "state"]:
                try:
                    form[attr].data = int(requestForm[attr])
                except ValueError:
                    pass
            else:
                form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})
    blog.rating = form.rating.data
    blog.message = form.message.data
    blog.state = form.state.data
    db.session.commit()
    return jsonify({"redirect": url_for("flixlist.root"), "form": None})


@flixlist_app.route("/blog/delete/<int:id>", methods=["GET", "POST"])
@login_required
@user_active
def deleteblog(id):
    blog = Blog.query.filter_by(id=id).first()
    if blog is not None:
        db.session.delete(blog)
        db.session.commit()
    return redirect(url_for("flixlist.root"))


@flixlist_app.route("/media/report/<int:id>", methods=["GET", "POST"])
@login_required
@user_active
def reportmedia(id):
    if request.method == "GET":
        return redirect(url_for("flixlist.mediapage", id=id))
    newreport = Reports(
        Account_email=current_user.id,
        Media_id=int(id),
        message=request.form["message"],
    )
    db.session.add(newreport)
    db.session.commit()
    return jsonify({"sucess": True})


@flixlist_app.route("/media/delete/<int:id>", methods=["POST"])
@login_required
@user_active
@admin_only
def deletemedia(id):
    media = Media.query.filter_by(id=id).first()
    blogs = Blog.query.filter_by(Media_id=id).all()
    reports = Reports.query.filter_by(Media_id=id).all()
    play_in = Plays_in.query.filter_by(Media_id=id).all()
    directed_by = Directed_by.query.filter_by(Media_id=id).all()
    series = Series.query.filter_by(id=id).first()
    for blog in blogs:
        db.session.delete(blog)
    for report in reports:
        db.session.delete(report)
    for actor in play_in:
        db.session.delete(actor)
    for director in directed_by:
        db.session.delete(director)
    if series is not None:
        db.session.delete(series)
    db.session.delete(media)
    db.session.commit()
    return jsonify({"redirect": url_for("flixlist.root")})


@flixlist_app.route("/people/delete/<int:id>", methods=["POST"])
@login_required
@user_active
@admin_only
def deletepeople(id):
    person = People.query.filter_by(id=id).first()
    play_in = Plays_in.query.filter_by(People_id=id).all()
    directed_by = Directed_by.query.filter_by(People_id=id).all()
    reports = Reports.query.filter_by(People_id=id).all()
    for actor in play_in:
        db.session.delete(actor)
    for director in directed_by:
        db.session.delete(director)
    for flag in reports:
        db.session.delete(flag)
    db.session.delete(person)
    db.session.commit()
    return jsonify({"redirect": url_for("flixlist.root")})


@flixlist_app.route("/media/edit/<int:id>", methods=["GET", "POST"])
@login_required
@user_active
def editmedia(id):
    media = Media.query.filter_by(id=id).first()
    series = Series.query.filter_by(id=id).first()
    if series:
        form = SeriesForm()
        isfilm = False
        info = {
            "title": media.title,
            "description": media.description,
            "duration": media.duration,
            "category": media.category,
            "year": media.year,
            "no_episodes": series.no_episodes,
            "no_seasons": series.no_seasons,
            "year_end": series.year_end,
            "duration2": series.duration2,
            "img": get_picture("media", id),
        }
    else:
        form = FilmForm()
        isfilm = True
        info = {
            "title": media.title,
            "description": media.description,
            "duration": media.duration,
            "category": media.category,
            "year": media.year,
            "img": get_picture("media", id),
        }
    if request.method == "GET":
        file = get_picture("media", id)
        return render_template(
            "modifmedia.html",
            form=form,
            isfilm=isfilm,
            info=info,
            media_id=id,
            picture=file,
        )
    requestForm = request.form
    for attr in requestForm:
        if not series:
            if attr in ["year", "duration"]:
                try:
                    form[attr].data = int(requestForm[attr])
                except ValueError:
                    pass
            else:
                form[attr].data = requestForm[attr].strip()
        else:
            if attr == "no_episodes" or attr == "no_seasons":
                try:
                    form[attr].data = int(requestForm[attr])
                except ValueError:
                    pass
            else:
                form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})
    if series:
        year = form.year.data.split("-")
        if len(year) == 1:
            year.append(None)
        else:
            if year[0] == year[1]:
                year[1] = None
        duration = form.duration.data.split("-")
        if len(duration) == 1:
            duration.append(None)
        elif duration[0] == duration[1]:
            duration[1] = None
        # edit in series
        series.no_episodes = form.no_episodes.data
        series.no_seasons = form.no_seasons.data
        series.duration2 = duration[1]
        series.year_end = year[1]
        # edit in media
        media.title = form.title.data
        media.description = form.description.data
        media.year = year[0]
        media.category = form.cat.data
        media.duration = duration[0]
    else:
        media.title = form.title.data
        media.description = form.description.data
        media.year = form.year.data
        media.category = form.cat.data
        media.duration = form.duration.data
    f = form.upload.data
    if f is not None:
        # remove previous profile picture
        for allowed_extension in ALLOWED_EXTENSIONS:
            filename = "%s.%s" % (media.id, allowed_extension)
            filepath = os.path.join("./my_app/static/img/media", filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        # upload new one
        extension = f.filename.rpartition(".")[2]
        file_name = "%s.%s" % (media.id, extension)
        file_path = os.path.join("./my_app/static/img/media", file_name)
        f.save(file_path)
    db.session.commit()
    return jsonify(
        {"redirect": url_for("flixlist.mediapage", id=id), "form": form.errors}
    )


@flixlist_app.route("/people/edit/<int:id>", methods=["GET", "POST"])
@login_required
@user_active
def editpeople(id):
    form = PeopleForm()
    person = People.query.filter_by(id=id).first()
    info = {
        "firstname": person.first_name,
        "lastname": person.last_name,
        "bday": person.bday,
    }
    if request.method == "GET":
        file = get_picture("people", id)
        return render_template(
            "editpeople.html", peopleForm=form, info=info, people_id=id, picture=file
        )
    requestForm = request.form
    for attr in requestForm:
        if not attr == "next":
            form[attr].data = requestForm[attr].strip()
    if not form.validate_on_submit():
        return jsonify({"redirect": None, "form": form.errors})

    person.first_name = form.firstName.data
    person.last_name = form.lastName.data
    person.bday = dt.datetime.strptime(form.bday.data, "%Y-%m-%d").date()
    f = form.upload.data
    if f is not None:
        # remove previous profile picture
        for allowed_extension in ALLOWED_EXTENSIONS:
            filename = "%s.%s" % (id, allowed_extension)
            filepath = os.path.join("./my_app/static/img/people", filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        # upload new one
        extension = f.filename.rpartition(".")[2]
        file_name = "%s.%s" % (id, extension)
        file_path = os.path.join("./my_app/static/img/people", file_name)
        f.save(file_path)
    db.session.commit()
    return jsonify(
        {"redirect": url_for("flixlist.peoplepage", id=id), "form": form.errors}
    )


@flixlist_app.route("/people/report/<int:id>", methods=["GET", "POST"])
@login_required
@user_active
def reportpeople(id):
    if request.method == "GET":
        return redirect(url_for("flixlist.peoplepage", id=id))
    newreport = Reports(
        Account_email=current_user.id,
        People_id=int(id),
        message=request.form["message"],
    )
    db.session.add(newreport)
    db.session.commit()
    return jsonify({"sucess": True})


@flixlist_app.route("/people/<int:id>/directed", methods=["GET", "POST"])
@login_required
@user_active
def peopledirected(id):
    person = People.query.filter_by(id=id).first()
    if person is None:
        abort(404, htmlExceptionMessages["404"])
    if request.method == "GET":
        all_media = Media.query.all()
        dict_pictures = {}
        for eachmedia in all_media:
            dict_pictures[eachmedia.id] = get_picture("media", eachmedia.id)
        return render_template(
            "people_directed_search.html",
            medias=all_media,
            pictures=dict_pictures,
            person=person,
        )
    person_directed_these = Directed_by.query.filter_by(People_id=person.id).all()
    person_directed_these_media_id = []
    for directed_by in person_directed_these:
        person_directed_these_media_id.append(directed_by.Media_id)
    media_query = Media.query.all()
    mediaIdList = []
    for eachMedia in media_query:
        mediaIdList.append(eachMedia.id)
    return jsonify(
        {
            "person_directs": person_directed_these_media_id,
            "media_query": mediaIdList,
        }
    )


@flixlist_app.route("/people/<int:id>/playedin", methods=["GET", "POST"])
@login_required
@user_active
def peopleplayedin(id):
    person = People.query.filter_by(id=id).first()
    if person is None:
        abort(404, htmlExceptionMessages["404"])
    if request.method == "GET":
        all_media = Media.query.all()
        dict_pictures = {}
        for eachmedia in all_media:
            dict_pictures[eachmedia.id] = get_picture("media", eachmedia.id)
        return render_template(
            "people_playedin_search.html",
            medias=all_media,
            pictures=dict_pictures,
            person=person,
        )
    person_played_in_these = Plays_in.query.filter_by(People_id=person.id).all()
    person_played_in_these_media_id = []
    for played_in in person_played_in_these:
        person_played_in_these_media_id.append(played_in.Media_id)
    media_query = Media.query.all()
    mediaIdList = []
    for eachMedia in media_query:
        mediaIdList.append(eachMedia.id)
    return jsonify(
        {
            "person_plays_in": person_played_in_these_media_id,
            "media_query": mediaIdList,
        }
    )


@flixlist_app.route("/people/<int:id>/direct/toggle", methods=["POST"])
@login_required
@user_active
def peopletoggledirect(id):
    request_data = request.get_data()
    if request_data is None:
        abort(418)
    decoded_request = request_data.decode("utf-8")
    mediaId = decoded_request
    director_query = Directed_by.query.filter_by(Media_id=mediaId, People_id=id).first()
    if director_query is None:
        new_director = Directed_by(
            Media_id=mediaId,
            People_id=id,
        )
        db.session.add(new_director)
    else:
        db.session.delete(director_query)
    db.session.commit()
    return jsonify({"success": True})


@flixlist_app.route("/people/<int:id>/play/toggle", methods=["POST"])
@login_required
@user_active
def peopletoggleplay(id):
    request_data = request.get_data()
    if request_data is None:
        abort(418)
    decoded_request = request_data.decode("utf-8")
    mediaId = decoded_request
    actor_query = Plays_in.query.filter_by(Media_id=mediaId, People_id=id).first()
    if actor_query is None:
        new_actor = Plays_in(
            Media_id=mediaId,
            People_id=id,
        )
        db.session.add(new_actor)
    else:
        db.session.delete(actor_query)
    db.session.commit()
    return jsonify({"success": True})
