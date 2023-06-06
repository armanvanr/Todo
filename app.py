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


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    public_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Todo <{self.name}>"


@app.get("/")
def greet():
    return jsonify({"message": "Welcome to Todo API"})


@app.get("/users")
def get_user():
    result = [
        {"name": u.name, "email": u.email, "id": u.public_id, "is_admin": u.is_admin}
        for u in User.query.all()
    ]
    return jsonify(result)


@app.post("/user")
def create_user():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        return {"error": f"User with email {data['email']} already exists"}, 400
    
    new_user = User(
        name=data["name"],
        email=data["email"],
        public_id=str(uuid.uuid4()),
        is_admin=data.get("is_admin", False)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User successfully created"}), 201


if __name__ == "__main__":
    app.run(debug=True)
