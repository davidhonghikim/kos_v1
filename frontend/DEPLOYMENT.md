# KOS v1 Frontend - Automated Deployment Guide

## 🚀 Quick Start (Zero User Interaction)

### Windows Deployment
```bash
# Navigate to frontend directory
cd frontend

# Run automated installer
install.bat
```

### Linux/macOS Deployment
```bash
# Navigate to frontend directory
cd frontend

# Make installer executable
chmod +x install.sh

# Run automated installer
./install.sh
```

## 📋 Prerequisites

### Required Software
- **Node.js 18+** (with npm included)
  - Download from: https://nodejs.org/
  - **Important**: Check "Add to PATH" during installation

### System Requirements
- **Linux**: Ubuntu 20.04+, CentOS 8+, or equivalent
- **macOS**: macOS 10.15+ (Catalina)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Windows**: Windows 10/11 (64-bit)

## 🔧 Automated Installation Process

The installer performs these steps automatically:

1. **Environment Check**
   - Verifies Node.js installation
   - Confirms npm availability
   - Handles PATH issues automatically

2. **Clean Installation**
   - Removes existing `node_modules`
   - Clears `package-lock.json`
   - Ensures fresh dependency installation

3. **Dependency Installation**
   - Installs all required packages
   - Uses `--legacy-peer-deps` for compatibility
   - Skips optional dependencies for faster install

4. **Security Audit**
   - Runs npm security audit
   - Automatically fixes vulnerabilities
   - Reports any remaining issues

5. **Build Verification**
   - Tests the build process
   - Ensures TypeScript compilation works
   - Verifies Vite bundling

## 🛡️ Security Features

### Automatic Vulnerability Fixes
- **esbuild vulnerability**: Automatically upgraded to Vite 7.0.4
- **Dependency scanning**: Continuous security monitoring
- **Force fixes**: Resolves breaking changes automatically

### Security Best Practices
- Uses `--no-audit` during install to prevent hanging
- Runs security audit after installation
- Applies fixes with `--force` when necessary

## 🔄 Reproducible Deployments

### Locked Dependencies
The `package.json` uses exact version ranges to ensure:
- Consistent installations across environments
- No unexpected breaking changes
- Reproducible builds

### Clean State Guarantee
Each installation:
- Removes all previous artifacts
- Starts with a clean slate
- Prevents dependency conflicts

## 🚨 Troubleshooting

### Common Issues

#### "npm is not recognized"
**Solution**: Reinstall Node.js with "Add to PATH" option checked

#### "Permission denied" (Linux/macOS)
**Solution**: Run with sudo or fix directory permissions
```bash
sudo ./install.sh
```

#### "Build failed"
**Solution**: Check Node.js version (requires 18+)
```bash
node --version
```

### Manual Fallback
If automated installation fails:
```bash
# Clean manually
rm -rf node_modules package-lock.json

# Install with specific flags
npm install --no-optional --no-audit --legacy-peer-deps

# Fix security issues
npm audit fix --force

# Test build
npm run build
```

## 📊 Installation Verification

After successful installation, verify with:
```bash
# Check if everything works
npm run dev    # Development server
npm run build  # Production build
npm run preview # Preview build
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy Frontend
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && chmod +x install.sh && ./install.sh
```

### Docker Integration
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install --no-optional --no-audit --legacy-peer-deps
COPY frontend/ .
RUN npm run build
```

## 📈 Performance Optimization

### Installation Speed
- Uses `--no-optional` to skip optional dependencies
- Uses `--no-audit` to prevent hanging during install
- Uses `--legacy-peer-deps` for compatibility

### Build Optimization
- TypeScript compilation optimized
- Vite bundling with tree-shaking
- Production-ready builds

## 🔍 Monitoring & Logs

### Installation Logs
- All steps are logged to console
- Error messages are clearly displayed
- Progress indicators for long operations

### Build Logs
- TypeScript compilation errors
- Vite bundling warnings
- Security audit results

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify Node.js version and PATH settings
3. Run the manual fallback commands
4. Check the console output for specific error messages

---

**Note**: This automated installation system ensures zero user interaction and reproducible deployments across all environments. 