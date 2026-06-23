"""Celery background tasks for email and audit processing."""

from loguru import logger

from app.core.celery_app import celery_app


@celery_app.task(name="send_welcome_email", bind=True, max_retries=3)
def send_welcome_email(self, email: str, full_name: str) -> dict[str, str]:
    """Simulate sending a welcome email to a newly registered user."""
    try:
        logger.info(
            "[EMAIL SIMULATION] Welcome email sent to {} ({})",
            email,
            full_name,
        )
        return {"status": "sent", "email": email, "type": "welcome"}
    except Exception as exc:
        logger.error("Failed to send welcome email: {}", exc)
        raise self.retry(exc=exc, countdown=60) from exc


@celery_app.task(name="send_password_reset_email", bind=True, max_retries=3)
def send_password_reset_email(self, email: str, reset_token: str) -> dict[str, str]:
    """Simulate sending a password reset email."""
    try:
        logger.info(
            "[EMAIL SIMULATION] Password reset email sent to {} (token: {}...)",
            email,
            reset_token[:8],
        )
        return {"status": "sent", "email": email, "type": "password_reset"}
    except Exception as exc:
        logger.error("Failed to send password reset email: {}", exc)
        raise self.retry(exc=exc, countdown=60) from exc


@celery_app.task(name="process_audit_log", bind=True, max_retries=3)
def process_audit_log(
    self,
    user_id: str,
    action: str,
    resource: str,
    resource_id: str,
) -> dict[str, str]:
    """Process audit log entry in the background."""
    try:
        logger.info(
            "[AUDIT PROCESSING] user={} action={} resource={} resource_id={}",
            user_id,
            action,
            resource,
            resource_id,
        )
        return {
            "status": "processed",
            "user_id": user_id,
            "action": action,
        }
    except Exception as exc:
        logger.error("Failed to process audit log: {}", exc)
        raise self.retry(exc=exc, countdown=30) from exc
