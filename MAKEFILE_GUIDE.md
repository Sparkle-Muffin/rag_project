# 🚀 RAG Project Makefile & Helper Script Guide

This guide explains how to use the new automation tools that will significantly improve your RAG project development workflow.

## 📋 What's New

Your project now includes:
- **`Makefile`** - Comprehensive automation for all project tasks
- **`rag.sh`** - User-friendly shell script wrapper
- **Automated workflows** - From setup to deployment

## 🎯 Key Benefits

1. **🚀 Faster Development** - One command instead of multiple manual steps
2. **🔄 Consistent Workflows** - Standardized processes for team members
3. **🐳 Docker Management** - Easy container lifecycle management
4. **🧪 Automated Testing** - Integrated testing and quality checks
5. **📊 Status Monitoring** - Quick project health checks
6. **💾 Backup & Recovery** - Automated project backups

## 🚀 Quick Start

### First-Time Setup
```bash
# Complete project setup (environment + Docker)
./rag.sh setup

# Activate environment
conda activate myenv

# Process documents
./rag.sh pipeline

# Launch application
./rag.sh app
```

### Daily Development
```bash
# Start services
./rag.sh start

# Check status
./rag.sh status

# Run tests
./rag.sh test

# Stop services
./rag.sh stop
```

## 📚 Detailed Command Reference

### 🐳 Docker Management

| Command | Description | Use Case |
|---------|-------------|----------|
| `./rag.sh start` | Start all containers | Daily development |
| `./rag.sh stop` | Stop all containers | End of work session |
| `./rag.sh restart` | Restart containers | After configuration changes |
| `./rag.sh logs` | View container logs | Debug issues |
| `./rag.sh status` | Check service health | Monitor system |

### 🔄 Pipeline & Processing

| Command | Description | Use Case |
|---------|-------------|----------|
| `./rag.sh pipeline` | Run document processing | After document updates |
| `./rag.sh test` | Run system tests | Before deployment |
| `./rag.sh app` | Launch Streamlit app | User testing |

### 🧹 Maintenance

| Command | Description | Use Case |
|---------|-------------|----------|
| `./rag.sh clean` | Remove generated files | Free up disk space |
| `./rag.sh backup` | Create project backup | Before major changes |
| `./rag.sh install-bielik` | Install Bielik model | Model setup |

### 🛠️ Development

| Command | Description | Use Case |
|---------|-------------|----------|
| `./rag.sh dev` | Run full dev workflow | Code quality check |
| `make format` | Format code | Before commits |
| `make lint` | Check code quality | Code review |

## 🔧 Advanced Makefile Usage

For power users, the Makefile provides additional commands:

```bash
# Show all available commands
make help

# Check environment status
make check-env

# Development workflow
make dev

# Production deployment check
make deploy-check

# Watch mode (auto-run tests on changes)
make watch
```

## 📊 Project Status Monitoring

Use `./rag.sh status` to get a comprehensive overview:

```bash
./rag.sh status
```

This will show:
- ✅ Conda environment status
- 🐳 Docker container status
- 📁 Generated files presence
- 🔧 Service health

## 🚨 Troubleshooting

### Common Issues

#### 1. Conda Environment Not Active
```bash
# Error: Please activate the 'myenv' conda environment first
conda activate myenv
```

#### 2. Docker Not Running
```bash
# Error: Docker is not running
sudo systemctl start docker  # Linux
# or start Docker Desktop on Windows/Mac
```

#### 3. Port Conflicts
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :6333  # Qdrant
sudo netstat -tulpn | grep :11434 # Ollama
```

#### 4. Container Issues
```bash
# View logs
./rag.sh logs

# Restart services
./rag.sh restart

# Clean and restart
make docker-clean
./rag.sh setup
```

## 🔄 Development Workflow

### 1. Morning Routine
```bash
./rag.sh start      # Start services
./rag.sh status     # Check everything is running
./rag.sh pipeline   # If documents changed
```

### 2. Development Session
```bash
# Make code changes...
make format         # Format code
make lint          # Check quality
./rag.sh test      # Run tests
```

### 3. End of Day
```bash
./rag.sh stop      # Stop services
./rag.sh backup    # Optional: create backup
```

## 📈 Performance Tips

1. **Use `make watch`** for automatic testing during development
2. **Run `./rag.sh clean`** periodically to free disk space
3. **Use `make deploy-check`** before production deployment
4. **Monitor with `./rag.sh status`** regularly

## 🔒 Security Considerations

- The Makefile and script don't handle sensitive data
- Docker containers run with default security settings
- Consider adding `.env` files for configuration if needed
- Review Docker container permissions for production use

## 🚀 Production Deployment

Before deploying to production:

```bash
# Run deployment checks
make deploy-check

# Verify all services are healthy
./rag.sh status

# Run full test suite
./rag.sh test

# Create backup
./rag.sh backup
```

## 📝 Customization

### Environment Variables
Edit the Makefile to customize:
- Container names
- Port numbers
- Environment names
- File paths

### Adding New Commands
1. Add target to Makefile
2. Add corresponding case to `rag.sh`
3. Update this documentation

## 🤝 Team Collaboration

### Onboarding New Developers
1. Clone repository
2. Run `./rag.sh setup`
3. Follow this guide
4. Use `./rag.sh help` for quick reference

### Standardized Workflows
- All team members use the same commands
- Consistent environment setup
- Standardized testing procedures
- Unified deployment process

## 📚 Additional Resources

- **Makefile Documentation**: `make help`
- **Script Help**: `./rag.sh help`
- **Project README**: `README.md`
- **Test Results**: `TEST_REPORT.md`

## 🎉 What You've Gained

With these new tools, your RAG project now has:

✅ **Professional-grade automation**  
✅ **Consistent development workflows**  
✅ **Easy service management**  
✅ **Automated quality checks**  
✅ **Comprehensive monitoring**  
✅ **Team collaboration tools**  
✅ **Production-ready processes**  

Your development experience is now significantly more efficient and professional! 🚀 