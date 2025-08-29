# 🚀 RAG Project - Quick Reference Card

## ⚡ Most Used Commands

```bash
# 🆕 NEW: Use these for faster development!
./rag.sh setup      # Complete project setup
./rag.sh start      # Start all services
./rag.sh stop       # Stop all services
./rag.sh status     # Check project health
./rag.sh pipeline   # Process documents
./rag.sh app        # Launch Streamlit app
./rag.sh test       # Run tests
./rag.sh clean      # Clean up files
```

## 🔄 Daily Workflow

### Morning
```bash
./rag.sh start      # Start services
./rag.sh status     # Verify everything is running
```

### Development
```bash
./rag.sh pipeline   # If documents changed
./rag.sh test       # Before committing
./rag.sh app        # To test changes
```

### Evening
```bash
./rag.sh stop       # Stop services
./rag.sh backup     # Optional: create backup
```

## 🐳 Docker Management

```bash
./rag.sh start      # Start containers
./rag.sh stop       # Stop containers
./rag.sh restart    # Restart containers
./rag.sh logs       # View logs
./rag.sh status     # Check container health
```

## 🛠️ Development Tools

```bash
make format         # Format code
make lint          # Check code quality
make dev           # Full dev workflow
make watch         # Auto-test on changes
```

## 📊 Status Check

```bash
./rag.sh status     # Quick health check
make deploy-check   # Production readiness
```

## 🆘 Help & Documentation

```bash
./rag.sh help      # Show this help
make help          # Show all Makefile commands
```

## 📚 Full Documentation

- **Complete Guide**: `MAKEFILE_GUIDE.md`
- **Project README**: `README.md`
- **Test Results**: `TEST_REPORT.md`

---

💡 **Pro Tip**: Use `./rag.sh` for daily tasks, `make` for advanced operations! 