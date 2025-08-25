# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of Ruckus Reboot Tool
- SSH connection to Ruckus access points using pexpect
- Single device reboot functionality
- Batch processing from CSV files
- Support for Ruckus CLI prompt detection
- Automatic credential prompting
- Progress tracking and status reporting
- Verbose and quiet output modes
- System information gathering
- Comprehensive error handling
- Beautiful CLI interface with Rich library
- Test connectivity script
- Configuration management
- Environment variable support

### Features
- **Single Device Mode**: Reboot individual access points
- **Batch Processing**: Process multiple devices from CSV file
- **Ruckus CLI Support**: Optimized for Ruckus access point CLI
- **Secure Authentication**: Password prompting and SSH key handling
- **Progress Tracking**: Visual progress indicators for batch operations
- **Result Reporting**: Detailed success/failure reporting
- **Flexible Output**: Verbose and simple output modes

### Technical Details
- Python 3.7+ compatibility
- Cross-platform support (Linux, macOS, Windows)
- GPL-3.0 licensed
- Comprehensive documentation
- Professional packaging with setup.py

### Security
- No password logging
- Secure credential handling
- SSH key verification support
- Proper connection cleanup

## [Unreleased]

### Planned Features
- Support for additional Ruckus models
- Configuration file support
- Scheduled reboot functionality
- Logging to file
- Email notifications
- Web interface
- Docker containerization
