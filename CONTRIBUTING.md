# Contributing to RLM Fraud Detection

First off, thank you for considering contributing to this project! 🎉

## Code of Conduct

This project and everyone participating in it is governed by respect, professionalism, and collaboration.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Include detailed steps to reproduce
- Provide system information (Python version, OS, etc.)
- Include relevant code snippets or error messages

### Suggesting Enhancements

- Open an issue with the `enhancement` label
- Clearly describe the feature and its benefits
- Provide examples of how it would be used

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run tests: `pytest tests/`
6. Update documentation if needed
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/rlm-fraud-detection.git
cd rlm-fraud-detection

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Run tests
pytest tests/

# Run linter
black app/
flake8 app/
```

## Style Guide

- Follow PEP 8 for Python code
- Use `black` for code formatting
- Write docstrings for all public functions
- Add type hints where appropriate
- Keep functions focused and small

## Testing

- Write tests for new features
- Maintain or improve code coverage
- Test with Python 3.11+

## Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update CHANGELOG.md

## Questions?

Feel free to open an issue for any questions about contributing.

## Attribution

All contributors will be recognized in the project's README.

---

**Author**: Abivarma (abivarmasabari@gmail.com)
**Repository**: https://github.com/Abivarma/rlm-fraud-detection
**Contact**: [GitHub](https://github.com/Abivarma) | [Medium](https://medium.com/@abivarmasabari) | [LinkedIn](https://www.linkedin.com/in/abivarma)
