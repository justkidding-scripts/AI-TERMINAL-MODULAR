# Contributing to AI-TERMINAL-MODULAR

Thank you for your interest in contributing! This guide will help you get started.

## Ways to Contribute

### Bug Reports
- **Search** existing issues first
- **Provide** detailed reproduction steps
- **Include** system information and logs
- **Add** labels: `bug`, `needs-triage`

### Feature Requests
- **Check** existing feature requests
- **Describe** the use case clearly
- **Provide** mockups or examples if applicable
- **Add** labels: `enhancement`, `feature-request`

### Code Contributions
- **Fork** the repository
- **Create** a feature branch
- **Follow** coding standards
- **Add** tests for new functionality
- **Update** documentation

### Documentation
- **Improve** existing docs
- **Add** missing documentation
- **Fix** typos and grammar
- **Update** examples

## Getting Started

### 1. Fork and Clone
```bash
git clone https/github.com/YOUR-USERNAME/AI-TERMINAL-MODULAR.git
cd AI-TERMINAL-MODULAR
```

### 2. Setup Development Environment
```bash
# Run setup
./setup.sh

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
./launch.sh --test
```

### 3. Create Branch
```bash
git checkout -b feature/amazing-feature
# or
git checkout -b bugfix/fix-important-bug
```

## Coding Standards

### Python Style
- **Follow** PEP 8
- **Use** type hints where possible
- **Add** docstrings for all functions/classes
- **Keep** line length under 88 characters
- **Use** meaningful variable names

### Code Quality
```bash
# Format code
black core/ modules/ tests/

# Check linting
flake8 core/ modules/ tests/

# Type checking
mypy core/ modules/

# Run tests
pytest tests/
```

### Commit Messages
Use conventional commits format:
```
feat: add new terminal interface
fix: resolve RAG indexing bug
docs: update installation guide
test: add RAG system tests
refactor: improve error handling
```

## Testing

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_rag_system.py

# With coverage
pytest --cov=core --cov=modules
```

### Writing Tests
- **Add tests** for all new functionality
- **Use** descriptive test names
- **Include** both positive and negative test cases
- **Mock** external dependencies
- **Test edge cases**

Example:
```python
def test_rag_add_document_success(self):
 """Test successful document addition to RAG system"""
 rag = RAGSkill()
 result = rag.handle("rag add_text test :: content")
 assert "Added" in result
 assert "test" in result
```

## ️ Architecture

### Project Structure
```
AI-TERMINAL-MODULAR/
├── core/ # Terminal implementations
├── modules/ # Modular components
├── tests/ # Test suite
├── config/ # Configuration templates
├── launchers/ # Launch scripts
└── docs/ # Documentation
```

### Key Components
- **Core Terminals**: Different interface implementations
- **RAG System**: Document indexing and retrieval
- **AI Integration**: Ollama client and fallback handling
- **Launchers**: Auto-detection and setup scripts

### Adding New Features
1. **Design** the feature interface
2. **Implement** core functionality
3. **Add** configuration options
4. **Write** comprehensive tests
5. **Update** documentation
6. **Add** launcher support

## Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
- [ ] No merge conflicts

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Documentation
- [ ] Documentation updated
- [ ] Examples added/updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
```

### Review Process
1. **Automated** checks run
2. **Maintainer** review
3. **Address** feedback
4. **Final approval**
5. **Merge** to main

## Recognition

Contributors are recognized in:
- **README** contributors section
- **Release notes**
- **GitHub** contributors page

## Getting Help

### Discussion Forums
- **GitHub Discussions**: General questions
- **Issues**: Bug reports and features
- **Discord**: Real-time chat (if available)

### Maintainer Contact
- **Issues**: Primary communication method
- **Email**: For security issues only

## First Contribution

### Good First Issues
Look for issues labeled:
- `good-first-issue`
- `help-wanted`
- `documentation`
- `beginner-friendly`

### Mentorship
- **Ask questions** in issues
- **Request guidance** from maintainers
- **Start small** with documentation or tests

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Standards
- **Be respectful** of differing viewpoints
- **Accept constructive criticism**
- **Focus on** what's best for the community
- **Show empathy** towards other contributors

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team.

---

## Thank You!

Every contribution, no matter how small, is valuable to the project. Thank you for helping make AI-TERMINAL-MODULAR better for everyone!

**Happy Coding!** 