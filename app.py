from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
username = os.environ["USER_NAME"]
password = os.environ["PASSWORD"]

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{username}:{password}@localhost:5432/dailytodos"
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# Schema for User Table
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    public_id = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    todos = db.relationship("Todo", backref="owner", lazy="dynamic")

    def __repr__(self):
        return f"User <{self.name}>"


# Schema for Todo Table
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    public_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Todo <{self.name}>"


# Route to greet
@app.get("/")
def greet():
    return jsonify({"message": "Welcome to Todo API"})


# Retrieve all users
@app.get("/users")
def get_users():
    result = [
        {"name": u.name, "email": u.email, "id": u.public_id, "is_admin": u.is_admin}
        for u in User.query.all()
    ]
    return jsonify(result)


# Retrieve or delete a user's data
@app.route("/user/<id>", methods=["GET", "DELETE"])
def get_delete_user(id):
    user = User.query.filter_by(public_id=id).first()
    if not user:
        return {"error": "User not found"}, 404

    # Retrieve a user's data
    if request.method == "GET":
        result = {"name": user.name, "email": user.email, "is_admin": user.is_admin}
        return result

    # Delete a user's data
    elif request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return {"message": "User successfully deleted"}, 200


# Create a new user or update an existing user's data
@app.route("/user", methods=["POST", "PUT"])
def create_user():
    data = request.get_json()

    # Create a new user
    if request.method == "POST":
        user = User.query.filter_by(email=data["email"]).first()
        if user:
            return {"error": f"User with email {data['email']} already exists"}, 400

        new_user = User(
            name=data["name"],
            email=data["email"],
            public_id=str(uuid.uuid4()),
            is_admin=data.get("is_admin", False),
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User successfully created"}), 201

    # Update an existing user's data partially or entirely
    elif request.method == "PUT":
        user = User.query.filter_by(public_id=data["id"]).first()
        if not user:
            return {"error": "User not found"}, 404

        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        user.is_admin = data.get("is_admin", user.is_admin)
        db.session.commit()
        return {"message": "User data successfully updated"}


if __name__ == "__main__":
    app.run(debug=True)
