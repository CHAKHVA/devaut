# Git Branching Workflow

This document outlines the basic Git branching workflow for this project.

## Branch Structure

- `main`: The main branch containing production-ready code
- `feature/*`: Feature branches for new development work

## Workflow Guidelines

1. **Main Branch**
   - The `main` branch should always contain production-ready code
   - Never commit directly to `main`
   - All changes must come through feature branches and pull requests

2. **Feature Branches**
   - Create a new feature branch for each feature/task
   - Branch naming convention: `feature/descriptive-name`
   - Example: `feature/user-authentication`, `feature/dashboard-layout`

## Development Process

1. **Starting New Work**

   ```bash
   # Ensure you're on main and it's up to date
   git checkout main
   git pull origin main

   # Create and switch to new feature branch
   git checkout -b feature/your-feature-name
   ```

2. **During Development**
   - Make regular commits with clear messages
   - Keep your feature branch up to date with main

   ```bash
   # Update your feature branch with main
   git checkout main
   git pull origin main
   git checkout feature/your-feature-name
   git merge main
   ```

3. **Completing Work**
   - Push your feature branch

   ```bash
   git push origin feature/your-feature-name
   ```

   - Create a pull request to merge into `main`
   - After review and approval, merge the pull request
   - Delete the feature branch after successful merge

## Best Practices

- Keep feature branches focused and small
- Update feature branches regularly with main
- Write clear commit messages
- Test your changes before creating pull requests
- Review your own code before submitting pull requests
