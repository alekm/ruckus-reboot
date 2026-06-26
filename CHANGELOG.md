# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--factory-reset` flag: runs the Ruckus `set factory` command then reboots, so APs
  come up at factory defaults — intended for bulk or targeted vSZ → RUCKUS One (R1)
  migrations. Works in single-device and batch modes, is guarded by a double
  confirmation (skippable with `--no-confirm`), and is mutually exclusive with
  `--no-reboot`. Pairs with `--info` to capture pre-reset version/uptime.

### Fixed
- Reboot success detection: the AP replies `OK` and then closes the SSH session,
  so a dropped connection is now treated as success instead of a failure. Also
  drains the trailing CLI prompt after `set factory` so it no longer bleeds into
  the following reboot command.

## [1.0.0] - 2025-08-25

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

### Security
- No password logging
- Secure credential handling
- SSH key verification support
- Proper connection cleanup
