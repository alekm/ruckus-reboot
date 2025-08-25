"""
Configuration module for Ruckus Access Point Reboot Tool
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class RuckusConfig:
    """Configuration class for Ruckus access point settings."""
    
    host: str
    username: str
    password: str
    port: int = 22
    timeout: int = 30
    reboot_timeout: int = 60
    
    @classmethod
    def from_env(cls) -> Optional['RuckusConfig']:
        """Create configuration from environment variables."""
        host = os.getenv('RUCKUS_HOST')
        username = os.getenv('RUCKUS_USERNAME')
        password = os.getenv('RUCKUS_PASSWORD')
        
        if not all([host, username, password]):
            return None
        
        return cls(
            host=host,
            username=username,
            password=password,
            port=int(os.getenv('RUCKUS_PORT', '22')),
            timeout=int(os.getenv('RUCKUS_TIMEOUT', '30')),
            reboot_timeout=int(os.getenv('RUCKUS_REBOOT_TIMEOUT', '60'))
        )


# Default configuration values
DEFAULT_CONFIG = {
    'ssh_timeout': 30,
    'command_timeout': 30,
    'reboot_timeout': 60,
    'max_retries': 3,
    'retry_delay': 5,
}

# Ruckus-specific command mappings
RUCKUS_COMMANDS = {
    'reboot': [
        'reboot',
        'shutdown -r now',
        'system reboot',
        'restart',
        'init 6'
    ],
    'system_info': {
        'hostname': 'hostname',
        'uptime': 'uptime',
        'version': 'cat /version 2>/dev/null || uname -a',
        'model': 'cat /proc/version 2>/dev/null || echo "Unknown"',
        'memory': 'free -h 2>/dev/null || echo "Memory info not available"',
        'interfaces': 'ifconfig 2>/dev/null || ip addr 2>/dev/null || echo "Interface info not available"'
    }
}
