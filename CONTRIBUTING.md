# Contributing to FinanceFlow

Thank you for your interest in contributing to FinanceFlow! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Potential implementation approach

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/financeflow.git
   cd financeflow
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   python manage.py test
   
   # Frontend tests (if implemented)
   cd frontend
   npm test
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your feature branch
   - Provide clear description of changes

## Code Style Guidelines

### Python (Backend)
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions and classes
- Maximum line length: 100 characters

```python
def calculate_budget_usage(user, category):
    """
    Calculate the percentage of budget used for a category.
    
    Args:
        user: User object
        category: Category object
    
    Returns:
        float: Percentage of budget used
    """
    # Implementation
```

### JavaScript (Frontend)
- Use ES6+ features
- Follow Airbnb style guide
- Use meaningful component and variable names
- Add JSDoc comments for complex functions

```javascript
/**
 * Format currency value with proper symbol and decimals
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount) => {
  // Implementation
};
```

## Development Setup

See [QUICKSTART.md](QUICKSTART.md) for complete setup instructions.

## Testing

### Backend Tests
```bash
cd backend
python manage.py test transactions
python manage.py test api
python manage.py test categorization
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Documentation

When adding new features:
- Update README.md if needed
- Update ARCHITECTURE.md for architectural changes
- Add/update API documentation
- Update setup guides if deployment changes

## Code Review Process

All contributions go through code review:
1. Automated tests must pass
2. Code style checks must pass
3. At least one maintainer approval required
4. Address review comments
5. Squash commits if requested

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Celebrate contributions of all sizes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue for questions
- Reach out to maintainers
- Join discussions in pull requests

Thank you for contributing to FinanceFlow! 🎉
