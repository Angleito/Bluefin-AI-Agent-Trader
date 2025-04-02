# Nix Integration Guide for Bluefin AI Agent Trader

## Overview

This project uses Nix for reproducible, declarative dependency management and build system. The Nix configuration provides a consistent and reproducible environment across different development and deployment scenarios.

## Nix Flake Configuration

The project uses a Nix flake (`nix/flake.nix`) to define the build and development environment. Key features include:

### Inputs
- `nixpkgs`: Official Nix package repository
- `flake-utils`: Utility for creating cross-system flakes
- `poetry2nix`: Tool for integrating Poetry with Nix

### Outputs

#### Packages
- `bluefin-trader`: Main application package
- Builds the project using Poetry dependencies

#### Development Shell
- Provides a complete development environment
- Includes Python 3.11
- Installs development tools (pytest, mypy, black, etc.)

## Using Nix

### Development Workflow

#### Enter Development Shell
```bash
nix develop
```
This command sets up a complete development environment with all dependencies.

#### Build the Project
```bash
nix build .#bluefin-trader
```
Builds the entire project with all dependencies.

### Continuous Integration

The Nix configuration includes checks for:
- Code formatting (black)
- Import sorting (isort)
- Type checking (mypy)

### Reproducible Builds

Nix ensures that:
- Dependencies are exactly the same across different machines
- Build environment is consistent
- No "it works on my machine" problems

## Docker Integration

The `Dockerfile.nix` uses a multi-stage build:
1. Use Nix to resolve and install dependencies
2. Create a minimal runtime image
3. Copy only necessary artifacts

### Building Docker Image
```bash
nix build .#bluefin-trader-docker
```

## Best Practices

### Updating Dependencies
- Use `nix flake update` to update input versions
- Commit `flake.lock` to version control

### Adding New Dependencies
1. Update `pyproject.toml`
2. Rebuild Nix environment
3. Commit changes to `flake.nix` if needed

## Troubleshooting

### Common Issues
- Ensure Nix experimental features are enabled
- Check that you're using a compatible system
- Verify network connectivity for package downloads

### Debugging
- Use `nix develop -v` for verbose output
- Check `nix log` for build logs

## Security

Nix provides additional security by:
- Isolating builds
- Preventing unexpected system-wide changes
- Enabling precise dependency tracking

## Contributing

When making changes:
- Update `flake.nix` for new dependencies
- Ensure all checks pass
- Test in the Nix development shell