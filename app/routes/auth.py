from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from email_validator import validate_email, EmailNotValidError
from .. import db
from ..models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    try:
        validate_email(email)
    except EmailNotValidError:
        return jsonify({"error": "Invalid email"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"is_admin": user.is_admin})
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.post("/auth/users")
@jwt_required()
def create_user():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    is_admin = bool(data.get("is_admin", False))

    try:
        validate_email(email)
    except EmailNotValidError:
        return jsonify({"error": "Invalid email"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User.register(email=email, password=password, is_admin=is_admin)
    return jsonify({"user": user.to_dict()}), 201
