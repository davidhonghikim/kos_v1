"""
Kind Link Framework (KLF) Protocol Implementation

This module implements the KLF protocol for secure, efficient messaging
in the KOS ecosystem.
"""

from .message import KLFMessage, MessageType, MessageFlags
from .connection import KLFConnection, ConnectionState
from .router import KLFRouter, TopicRouter
from .encryption import KLFEncryption, EncryptionAlgorithm

__version__ = "1.0.0"
__all__ = [
    "KLFMessage",
    "MessageType", 
    "MessageFlags",
    "KLFConnection",
    "ConnectionState",
    "KLFRouter",
    "TopicRouter",
    "KLFEncryption",
    "EncryptionAlgorithm"
] 