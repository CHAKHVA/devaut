# app/core/security.py

import logging  # Keep logging here for security-related events
import uuid
from datetime import datetime, timezone
from typing import Optional

# Import application settings
from app.core.config import settings
from jose import ExpiredSignatureError, JWTClaimsError, JWTError, jwt

logger = logging.getLogger(__name__)

# --- Password hashing/verification functions are REMOVED ---
# These responsibilities are handled by Supabase Auth service.

# --- FastAPI-specific token creation is REMOVED ---
# Access tokens are issued by Supabase Auth service.


def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verifies a JWT token allegedly issued by Supabase Auth.

    Checks the signature, expiration, issuer, and audience claims
    against the values configured in application settings.

    Args:
        token: The JWT token string received from the client.

    Returns:
        The decoded payload dictionary if the token is valid in all aspects,
        otherwise returns None. Logs warnings/errors on failure.
    """
    try:
        # Decode the token, simultaneously verifying signature, expiration,
        # issuer, and audience based on provided options.
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],  # Supabase typically uses HS256
            audience=settings.SUPABASE_AUDIENCE,  # Verify the intended audience
            issuer=settings.SUPABASE_ISSUER_URL,  # Verify who issued the token
        )

        # Although decode checks 'exp', an explicit check can be clearer
        # and handles potential clock skew issues if needed (though usually not necessary).
        # exp_timestamp = payload.get('exp')
        # if not exp_timestamp or datetime.now(timezone.utc) >= datetime.fromtimestamp(exp_timestamp, timezone.utc):
        #     logger.warning("Token verification failed: Token has expired (explicit check).")
        #     return None

        # If decode succeeds without exceptions, the token is considered valid
        return payload

    except ExpiredSignatureError:
        # Specific exception for expired tokens
        logger.warning(
            "Token verification failed: Token has expired (ExpiredSignatureError)."
        )
        return None
    except JWTClaimsError as e:
        # Specific exception for invalid claims (e.g., wrong audience or issuer)
        logger.warning(f"Token verification failed: Invalid claims: {e}")
        return None
    except JWTError as e:
        # Catches other JWT errors like invalid signature, malformed token, etc.
        logger.warning(f"Token verification failed: General JWTError: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors during the process
        logger.error(
            f"An unexpected error occurred during token verification: {e}",
            exc_info=True,
        )
        return None


def extract_supabase_user_id(payload: dict) -> Optional[uuid.UUID]:
    """
    Safely extracts the Supabase User ID (usually the 'sub' claim)
    from a decoded JWT payload and converts it to a UUID object.

    Args:
        payload: The dictionary representing the decoded JWT payload.

    Returns:
        The User ID as a UUID object if found and valid, otherwise None.
    """
    subject = payload.get("sub")
    if not subject:
        logger.error("Supabase User ID ('sub' claim) not found in token payload.")
        return None
    try:
        # Convert the subject string to a UUID object
        user_id = uuid.UUID(subject)
        return user_id
    except ValueError:
        # Handle cases where the 'sub' claim is not a valid UUID format
        logger.error(
            f"Invalid UUID format for Supabase User ID ('sub' claim): {subject}"
        )
        return None


def extract_user_email(payload: dict) -> Optional[str]:
    """
    Safely extracts the email claim from a decoded JWT payload.

    Args:
        payload: The dictionary representing the decoded JWT payload.

    Returns:
        The email string if found, otherwise None.
    """
    email = payload.get("email")
    if not email:
        logger.warning("Email claim not found in token payload.")
        return None
    return str(email)  # Ensure it's a string
