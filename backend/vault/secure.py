"""
Secure Vault Implementation

Encrypted storage system for sensitive data in the Amauta system.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from backend.config import settings

logger = logging.getLogger(__name__)


class VaultManager:
    """Secure vault manager for encrypted data storage"""

    def __init__(self):
        self.vault_path = settings.VAULT_PATH
        self.key_file = os.path.join(self.vault_path, "vault.key")
        self.data_file = os.path.join(self.vault_path, "vault.data")
        self._ensure_vault_directory()
        self._load_or_create_key()

    def _ensure_vault_directory(self):
        """Ensure vault directory exists"""
        os.makedirs(self.vault_path, exist_ok=True)
        logger.info(f"Vault directory ensured: {self.vault_path}")

    def _load_or_create_key(self):
        """Load existing key or create new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                self.key = f.read()
            logger.info("Loaded existing vault key")
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
            logger.info("Generated new vault key")

        self.cipher = Fernet(self.key)

    def store(self, key: str, value: Any) -> bool:
        """Store encrypted data in vault"""
        try:
            # Load existing data
            data = self._load_data()

            # Encrypt value
            value_str = json.dumps(value)
            encrypted_value = self.cipher.encrypt(value_str.encode())

            # Store encrypted data
            data[key] = base64.b64encode(encrypted_value).decode()

            # Save data
            self._save_data(data)

            logger.info(f"Stored encrypted data for key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to store data in vault: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve decrypted data from vault"""
        try:
            # Load data
            data = self._load_data()

            if key not in data:
                logger.warning(f"Key not found in vault: {key}")
                return None

            # Decrypt value
            encrypted_value = base64.b64decode(data[key])
            decrypted_value = self.cipher.decrypt(encrypted_value)

            # Parse JSON
            value = json.loads(decrypted_value.decode())

            logger.info(f"Retrieved decrypted data for key: {key}")
            return value

        except Exception as e:
            logger.error(f"Failed to retrieve data from vault: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete data from vault"""
        try:
            data = self._load_data()

            if key in data:
                del data[key]
                self._save_data(data)
                logger.info(f"Deleted data for key: {key}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete data from vault: {e}")
            return False

    def list_keys(self) -> list:
        """List all keys in vault"""
        try:
            data = self._load_data()
            return list(data.keys())
        except Exception as e:
            logger.error(f"Failed to list vault keys: {e}")
            return []

    def clear(self) -> bool:
        """Clear all data from vault"""
        try:
            self._save_data({})
            logger.info("Cleared all vault data")
            return True
        except Exception as e:
            logger.error(f"Failed to clear vault: {e}")
            return False

    def _load_data(self) -> Dict[str, str]:
        """Load vault data from file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        return {}

    def _save_data(self, data: Dict[str, str]):
        """Save vault data to file"""
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def health_check(self) -> Dict[str, Any]:
        """Health check for vault"""
        try:
            keys = self.list_keys()
            return {
                "status": "healthy",
                "total_keys": len(keys),
                "vault_path": self.vault_path,
                "key_exists": os.path.exists(self.key_file),
                "data_exists": os.path.exists(self.data_file),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global vault instance
vault_manager = VaultManager()
