from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models.vault import VaultItem
from ..utils.crypto import encrypt_to_b64, decrypt_from_b64

vault_bp = Blueprint("vault", __name__)


@vault_bp.post("/vault")
@jwt_required()
def create_item():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    username = data.get("username")
    password = data.get("password") or ""
    notes = data.get("notes") or None

    item = VaultItem(
        owner_id=user_id,
        name=name,
        username=username,
        password_encrypted=encrypt_to_b64(password),
        notes_encrypted=encrypt_to_b64(notes) if notes else None,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"item": item.to_dict()}), 201


@vault_bp.get("/vault")
@jwt_required()
def list_items():
    user_id = int(get_jwt_identity())
    items = VaultItem.query.filter_by(owner_id=user_id).order_by(VaultItem.updated_at.desc()).all()
    return jsonify({"items": [i.to_dict() for i in items]}), 200


@vault_bp.get("/vault/<int:item_id>")
@jwt_required()
def get_item(item_id: int):
    user_id = int(get_jwt_identity())
    item = VaultItem.query.filter_by(id=item_id, owner_id=user_id).first()
    if item is None:
        return jsonify({"error": "Not found"}), 404
    detail = item.to_dict() | {
        "password": decrypt_from_b64(item.password_encrypted),
        "notes": decrypt_from_b64(item.notes_encrypted) if item.notes_encrypted else None,
    }
    return jsonify({"item": detail}), 200


@vault_bp.put("/vault/<int:item_id>")
@jwt_required()
def update_item(item_id: int):
    user_id = int(get_jwt_identity())
    item = VaultItem.query.filter_by(id=item_id, owner_id=user_id).first()
    if item is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        item.name = (data.get("name") or "").strip()
    if "username" in data:
        item.username = data.get("username")
    if "password" in data and data.get("password") is not None:
        item.password_encrypted = encrypt_to_b64(data.get("password") or "")
    if "notes" in data:
        notes_val = data.get("notes")
        item.notes_encrypted = encrypt_to_b64(notes_val) if notes_val else None

    db.session.commit()
    return jsonify({"item": item.to_dict()}), 200


@vault_bp.delete("/vault/<int:item_id>")
@jwt_required()
def delete_item(item_id: int):
    user_id = int(get_jwt_identity())
    item = VaultItem.query.filter_by(id=item_id, owner_id=user_id).first()
    if item is None:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "deleted"}), 200
