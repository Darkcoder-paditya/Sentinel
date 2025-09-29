from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models.mail import Mail
from ..models.user import User

mail_bp = Blueprint("mail", __name__)


@mail_bp.post("/mail/send")
@jwt_required()
def send_mail():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    recipient_email = (data.get("to") or "").strip().lower()
    subject = data.get("subject") or ""
    body = data.get("body") or ""

    recipient = User.query.filter_by(email=recipient_email).first()
    if recipient is None:
        return jsonify({"error": "Recipient not found"}), 404

    msg = Mail(sender_id=user_id, recipient_id=recipient.id, subject=subject, body=body)
    db.session.add(msg)
    db.session.commit()
    return jsonify({"mail": msg.to_dict()}), 201


@mail_bp.get("/mail/inbox")
@jwt_required()
def inbox():
    user_id = int(get_jwt_identity())
    rows = Mail.query.filter_by(recipient_id=user_id).order_by(Mail.created_at.desc()).limit(100).all()
    return jsonify({"items": [r.to_dict() for r in rows]}), 200


@mail_bp.get("/mail/sent")
@jwt_required()
def sent():
    user_id = int(get_jwt_identity())
    rows = Mail.query.filter_by(sender_id=user_id).order_by(Mail.created_at.desc()).limit(100).all()
    return jsonify({"items": [r.to_dict() for r in rows]}), 200
