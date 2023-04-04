from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    DateField,
    EmailField,
    SelectField,
    IntegerField,
)
from wtforms.validators import (
    Optional,
    Length,
    InputRequired,
    ValidationError,
    Regexp,
    Email,
    NumberRange,
)
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from .models import Account
import string, datetime

# list of common image file types allowed for upload
ALLOWED_EXTENSIONS = [
    "apng",
    "avif",
    "gif",
    "jpg",
    "jpeg",
    "jfif",
    "pjpeg",
    "pjp",
    "png",
    "svg",
    "webp",
]


def passwdLowercase(form, field):
    for char in field.data:
        if char in string.ascii_lowercase:
            return
    raise ValidationError("Field must contain at least one lowercase character.")


def passwdUppercase(form, field):
    for char in field.data:
        if char in string.ascii_uppercase:
            return
    raise ValidationError("Field must contain at least one uppercase character.")


def passwdDigit(form, field):
    for char in field.data:
        if char in string.digits:
            return
    raise ValidationError("Field must contain at least one digit.")


def confirm_passwd_confirm(form, field):
    if form.__contains__("passwd") and field.data != form.passwd.data:
        raise ValidationError("Wrong password confirmation.")
    elif form.__contains__("new_passwd") and field.data != form.new_passwd.data:
        raise ValidationError("Wrong password confirmation.")


def check_bday(form, field):
    if (
        datetime.datetime.strptime(field.data, "%Y-%m-%d").date()
        > datetime.date.today()
    ):
        raise ValidationError("Wrong birthdate.")


def existing_username(form, field):
    user = Account.query.filter_by(username=field.data).first()
    if (
        user is not None
        and current_user.is_anonymous
        or user is not None
        and not current_user.id == user.id
    ):
        raise ValidationError(
            "This user already exist. Please use a different username."
        )


def verify_email_address(form, field):
    user = Account.query.filter_by(id=field.data).first()
    if (
        user is not None
        and current_user.is_anonymous
        or user is not None
        and not current_user.id == user.id
    ):
        raise ValidationError("This email address is already registered.")
    invalid_character = ["\\", "/", ":", "*", "?", "<", ">", "|", ' " ']
    for char in field.data:
        if char in invalid_character:
            raise ValidationError(
                'Unauthorized characters: \\, /, : , *, ?, <, >, |, ".'
            )


def passwordNoLeadingOrTrailingSpaces(form, field):
    if field.data.startswith(" ") or field.data.endswith(" "):
        raise ValidationError("Field cannot start or end with a whitespace character.")


username_validators = [
    Optional(),
    Length(min=2, max=20),
    Regexp(
        "^\w+$", message="Username must contain only letters, numbers or underscore."
    ),
    existing_username,
]
name_validators = [
    InputRequired(),
    Length(min=2, max=20),
    Regexp(
        "^\w+$", message="Username must contain only letters, numbers or underscore."
    ),
]
passwd_validators = [
    InputRequired(),
    Length(min=8),
    Length(max=128),  # two Length() functions to separate error messages
    passwdLowercase,
    passwdUppercase,
    passwdDigit,
    passwordNoLeadingOrTrailingSpaces,
]
email_validators = [InputRequired(), Email(), Length(max=1024), verify_email_address]
positive_int_validators = [InputRequired(), NumberRange(min=1)]


class EditProfilePasswordForm(FlaskForm):
    current_passwd = PasswordField(
        label="Current password", validators=[InputRequired()]
    )
    new_passwd = PasswordField(label="New password", validators=passwd_validators)
    new_passwd_confirm = PasswordField(
        label="Confirm new password", validators=[confirm_passwd_confirm]
    )
    submit = SubmitField(label="Change password")


class EditProfileForm(FlaskForm):
    email = EmailField(label="Email", validators=email_validators)
    username = StringField(label="Username (optional)", validators=username_validators)
    firstName = StringField(label="First Name", validators=name_validators)
    lastName = StringField(label="Last Name", validators=name_validators)
    bday = DateField(label="Birthdate", validators=[InputRequired(), check_bday])
    upload = FileField(
        label="Change profile picture",
        validators=[FileAllowed(ALLOWED_EXTENSIONS)],
    )
    submit = SubmitField(label="Save changes")


class RegisterForm(FlaskForm):
    email = EmailField(label="Email", validators=email_validators)
    passwd = PasswordField(label="Password", validators=passwd_validators)
    passwd_confirm = PasswordField(
        label="Confirm password", validators=[confirm_passwd_confirm]
    )
    username = StringField(label="Username (optional)", validators=username_validators)
    firstName = StringField(label="First Name", validators=name_validators)
    lastName = StringField(label="Last Name", validators=name_validators)
    bday = DateField(label="Birthdate", validators=[InputRequired(), check_bday])
    upload = FileField(
        label="Profile picture (optional)",
        validators=[FileAllowed(ALLOWED_EXTENSIONS)],
    )
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[InputRequired()])
    passwd = PasswordField(label="Password", validators=[InputRequired()])
    submit = SubmitField(label="Log-in")


class FilmForm(FlaskForm):
    title = StringField(label="Title", validators=[InputRequired()])
    description = StringField(label="Description (optional)", validators=[Optional()])
    year = IntegerField(label="Year", validators=positive_int_validators)
    duration = IntegerField(label="Duration", validators=positive_int_validators)
    cat = StringField(label="Category", validators=[InputRequired()])
    upload = FileField(
        label="Image (optional)",
        validators=[FileAllowed(ALLOWED_EXTENSIONS)],
    )
    submit = SubmitField(label="Submit to our database")


class SeriesForm(FlaskForm):
    title = StringField(label="Title", validators=[InputRequired()])
    description = StringField(label="Description (optional)", validators=[Optional()])
    year = StringField(label="Year range", validators=[InputRequired()])
    duration = StringField(label="Duration", validators=[InputRequired()])
    cat = StringField(label="Category", validators=[InputRequired()])
    no_seasons = IntegerField(
        label="Number of seasons", validators=positive_int_validators
    )
    no_episodes = IntegerField(
        label="Number of episodes", validators=positive_int_validators
    )
    upload = FileField(
        label="Image (optional)",
        validators=[FileAllowed(ALLOWED_EXTENSIONS)],
    )
    submit = SubmitField(label="Submit to our database")

    def validate_year(self, field):
        splitedField = field.data.split("-")
        if len(splitedField) > 2:
            raise ValidationError('Format must be "xxxx-xxxx"')
        try:
            for element in splitedField:
                int(element)
        except ValueError:
            raise ValidationError("Input must be numbers")
        if len(splitedField) == 2:
            if splitedField[0] > splitedField[1]:
                raise ValidationError("Wrong year range")

    def validate_duration(self, field):
        splitedField = field.data.split("-")
        if len(splitedField) > 2:
            raise ValidationError('Format must be "xx-xx" in minutes')
        try:
            for element in splitedField:
                int(element)
        except ValueError:
            raise ValidationError("Input must be numbers")
        if len(splitedField) == 2:
            if splitedField[0] > splitedField[1]:
                raise ValidationError("Wrong duration range")


class PeopleForm(FlaskForm):
    firstName = StringField(label="First Name", validators=name_validators)
    lastName = StringField(label="Last Name", validators=name_validators)
    bday = DateField(label="Birthdate", validators=[InputRequired()])
    upload = FileField(
        label="Image (optional)",
        validators=[FileAllowed(ALLOWED_EXTENSIONS)],
    )
    submit = SubmitField(label="Submit to our database")

    def validate_bday(self, field):
        if (
            datetime.datetime.strptime(field.data, "%Y-%m-%d").date()
            > datetime.date.today()
        ):
            raise ValidationError("Wrong birthdate.")


class BlogForm(FlaskForm):
    rating = IntegerField(
        label="Rating (Optional)", validators=[Optional(), NumberRange(min=0, max=5)]
    )
    message = StringField(label="Message (Optional)")
    state = IntegerField(label="Status", validators=[InputRequired()])
    submit = SubmitField(label="Submit to our database")
