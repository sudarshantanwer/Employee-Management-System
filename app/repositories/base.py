"""Shared repository utilities."""

from typing import Any

from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(id_str: str) -> ObjectId:
    """Convert string to ObjectId, raising ValueError on invalid input."""
    try:
        return ObjectId(id_str)
    except InvalidId as exc:
        raise ValueError(f"Invalid ID format: {id_str}") from exc


def serialize_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert MongoDB document _id to string."""
    if document is None:
        return None
    doc = dict(document)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def serialize_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Serialize a list of MongoDB documents."""
    return [serialize_document(doc) for doc in documents]  # type: ignore[misc]
