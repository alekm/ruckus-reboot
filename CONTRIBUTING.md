# Contributing to Ruckus Reboot Tool

Thank you for your interest in contributing to the Ruckus Reboot Tool! This document provides guidelines for contributing to this project.

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate in all interactions.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker to report bugs
- Include detailed information about your environment (OS, Python version, etc.)
- Provide steps to reproduce the issue
- Include any error messages or logs

### Suggesting Enhancements

- Use the GitHub issue tracker to suggest new features
- Describe the enhancement and why it would be useful
- Consider the impact on existing functionality

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/alekm/ruckus-reboot.git
   cd ruckus-reboot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

## Testing

- Test your changes thoroughly
- Ensure compatibility with different Python versions
- Test with actual Ruckus access points when possible

## Documentation

- Update documentation for any new features
- Keep the README.md up to date
- Add docstrings for new functions and classes

## Security

- Never commit sensitive information (passwords, API keys, etc.)
- Follow security best practices
- Report security vulnerabilities privately

## License

By contributing to this project, you agree that your contributions will be licensed under the GNU General Public License v3.0.

## Questions?

If you have questions about contributing, please open an issue on GitHub.
