from flask.cli import FlaskGroup
from app import app
from extensions import db
from werkzeug.security import generate_password_hash
from models import User
import click
import getpass
import datetime

cli = FlaskGroup(app)

@cli.command("create_admin")
@click.argument("email")
def create_admin(email):
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print("Passwords don't match")
        return
    try:
        created_on = datetime.datetime.now()
        user = User(
            email=email, 
            name="Администратор", 
            password=generate_password_hash(password, method='sha256'), 
            created_on=created_on, 
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        print(f"Admin user with email '{email}' created successfully!")
    except Exception as e:
        print(f"Couldn't create admin user: {e}")

if __name__ == "__main__":
    cli()
