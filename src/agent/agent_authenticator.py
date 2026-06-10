import hashlib
import uuid
import secrets

class AgentAuthenticator:
    """Manages secrets and cryptographic signatures for agent communication."""

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a secure random secret key for a new agent.
        Uses secrets module for cryptographic randomness.
        """
        return secrets.token_hex(32)

    @staticmethod
    def sign_message(message: str, secret_key: str) -> str:
        """
        Create a SHA-256 signature for the given message and secret key.
        The formula is SHA256(message + secret_key).
        """
        data = message + secret_key
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_message(message: str, secret_key: str, signature: str) -> bool:
        """
        Verify that the provided signature matches the message and secret key.
        """
        expected_signature = AgentAuthenticator.sign_message(message, secret_key)
        return secrets.compare_digest(expected_signature, signature)
