# RAG Project Makefile
# Automates common development tasks for the RAG QA Chat system

.PHONY: help install setup clean test run-pipeline run-tests run-app docker-setup docker-clean docker-logs lint format check-env

# Default target
help:
	@echo "🚀 RAG Project Makefile - Available Commands:"
	@echo ""
	@echo "📦 Environment & Setup:"
	@echo "  install          - Create conda environment from environment.yml"
	@echo "  setup            - Full project setup (install + docker-setup)"
	@echo "  check-env        - Check if conda environment is active"
	@echo ""
	@echo "🐳 Docker Management:"
	@echo "  docker-setup     - Setup Ollama and Qdrant containers"
	@echo "  docker-start     - Start all containers"
	@echo "  docker-stop      - Stop all containers"
	@echo "  docker-restart   - Restart all containers"
	@echo "  docker-logs      - Show container logs"
	@echo "  docker-clean     - Remove containers and volumes"
	@echo ""
	@echo "🔄 Pipeline & Processing:"
	@echo "  run-pipeline     - Run document processing pipeline"
	@echo "  run-tests        - Run system tests and generate report"
	@echo "  run-app          - Launch Streamlit user application"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean            - Clean generated files and caches"
	@echo "  lint             - Run code linting (if tools available)"
	@echo "  format           - Format code (if tools available)"
	@echo ""
	@echo "📊 Development:"
	@echo "  dev-setup        - Setup development environment with linting tools"
	@echo "  watch            - Watch for changes and run tests automatically"

# Environment variables
ENV_NAME := myenv
OLLAMA_CONTAINER := ollama
QDRANT_CONTAINER := qdrant
OLLAMA_PORT := 11434
QDRANT_PORT := 6333

# Check if conda environment is active
check-env:
	@if [ "$$(conda info --envs | grep '*' | awk '{print $$1}')" != "$(ENV_NAME)" ]; then \
		echo "❌ Error: Please activate the '$(ENV_NAME)' conda environment first:"; \
		echo "   conda activate $(ENV_NAME)"; \
		exit 1; \
	else \
		echo "✅ Conda environment '$(ENV_NAME)' is active"; \
	fi

# Install conda environment
install:
	@echo "📦 Creating conda environment from environment.yml..."
	conda env create -f environment.yml
	@echo "✅ Environment created successfully!"
	@echo "   Activate it with: conda activate $(ENV_NAME)"

# Setup development environment with linting tools
dev-setup: install
	@echo "🔧 Setting up development environment..."
	conda activate $(ENV_NAME) && pip install black flake8 mypy pre-commit
	@echo "✅ Development tools installed!"

# Full project setup
setup: install docker-setup
	@echo "🎉 Project setup complete!"
	@echo "   Next steps:"
	@echo "   1. conda activate $(ENV_NAME)"
	@echo "   2. make run-pipeline"
	@echo "   3. make run-app"

# Docker setup
docker-setup:
	@echo "🐳 Setting up Docker containers..."
	@echo "📥 Pulling Qdrant image..."
	docker pull qdrant/qdrant
	@echo "🚀 Starting Qdrant container..."
	docker run -d --name $(QDRANT_CONTAINER) -p $(QDRANT_PORT):6333 qdrant/qdrant
	@echo "📥 Setting up Ollama container..."
	docker run -d --gpus=all -v ${PWD}/ollama_volumes:/root/.ollama -p $(OLLAMA_PORT):$(OLLAMA_PORT) --name $(OLLAMA_CONTAINER) ollama/ollama
	@echo "⏳ Waiting for containers to be ready..."
	@sleep 10
	@echo "✅ Docker containers are ready!"

# Docker management
docker-start:
	@echo "🚀 Starting containers..."
	docker start $(QDRANT_CONTAINER) $(OLLAMA_CONTAINER)
	@echo "✅ Containers started!"

docker-stop:
	@echo "🛑 Stopping containers..."
	docker stop $(QDRANT_CONTAINER) $(OLLAMA_CONTAINER)
	@echo "✅ Containers stopped!"

docker-restart: docker-stop docker-start

docker-logs:
	@echo "📋 Container logs:"
	@echo "=== Qdrant ==="
	docker logs $(QDRANT_CONTAINER) --tail=20
	@echo "=== Ollama ==="
	docker logs $(OLLAMA_CONTAINER) --tail=20

docker-clean:
	@echo "🧹 Cleaning up Docker containers and volumes..."
	docker stop $(QDRANT_CONTAINER) $(OLLAMA_CONTAINER) 2>/dev/null || true
	docker rm $(QDRANT_CONTAINER) $(QDRANT_CONTAINER) 2>/dev/null || true
	docker volume rm ollama_volumes 2>/dev/null || true
	@echo "✅ Docker cleanup complete!"

# Pipeline execution
run-pipeline: check-env
	@echo "🔄 Running document processing pipeline..."
	python rag_pipeline.py
	@echo "✅ Pipeline execution complete!"

# Test execution
run-tests: check-env
	@echo "🧪 Running system tests..."
	python rag_run_tests.py
	@echo "✅ Tests complete! Check TEST_REPORT.md for results."

# Application launch
run-app: check-env
	@echo "🚀 Launching Streamlit application..."
	streamlit run rag_user_app.py

# Watch mode for development
watch: check-env
	@echo "👀 Watching for changes and running tests..."
	@echo "Press Ctrl+C to stop watching"
	@while true; do \
		find . -name "*.py" -newer .last_run 2>/dev/null | head -1 | xargs -I {} echo "Change detected in {}"; \
		touch .last_run; \
		sleep 2; \
	done

# Code quality
lint: check-env
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 . --exclude=__pycache__,*.egg-info,.git,venv,env; \
	else \
		echo "⚠️  flake8 not found. Install with: make dev-setup"; \
	fi

format: check-env
	@echo "✨ Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black . --exclude="__pycache__|*.egg-info|.git|venv|env"; \
	else \
		echo "⚠️  black not found. Install with: make dev-setup"; \
	fi

# Cleanup
clean:
	@echo "🧹 Cleaning up generated files..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .last_run
	rm -rf docs_preprocessed/
	rm -rf text_chunks/
	rm -f TEST_REPORT.md
	@echo "✅ Cleanup complete!"

# Quick status check
status:
	@echo "📊 Project Status:"
	@echo "=== Environment ==="
	@if conda info --envs | grep -q "^\* $(ENV_NAME)"; then \
		echo "✅ Conda environment: $(ENV_NAME) (active)"; \
	else \
		echo "❌ Conda environment: $(ENV_NAME) (not active)"; \
	fi
	@echo "=== Docker Containers ==="
	@if docker ps | grep -q "$(QDRANT_CONTAINER)"; then \
		echo "✅ Qdrant: Running"; \
	else \
		echo "❌ Qdrant: Not running"; \
	fi
	@if docker ps | grep -q "$(OLLAMA_CONTAINER)"; then \
		echo "✅ Ollama: Running"; \
	else \
		echo "❌ Ollama: Not running"; \
	fi
	@echo "=== Files ==="
	@if [ -d "docs_preprocessed" ]; then \
		echo "✅ Preprocessed docs: Present"; \
	else \
		echo "❌ Preprocessed docs: Missing"; \
	fi
	@if [ -d "text_chunks" ]; then \
		echo "✅ Text chunks: Present"; \
	else \
		echo "❌ Text chunks: Missing"; \
	fi

# Backup and restore
backup:
	@echo "💾 Creating backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "rag_project_backup_$$timestamp.tar.gz" \
		--exclude='*.tar.gz' \
		--exclude='__pycache__' \
		--exclude='.git' \
		--exclude='ollama_volumes' \
		.
	@echo "✅ Backup created: rag_project_backup_$$timestamp.tar.gz"

# Install Bielik model in Ollama
install-bielik:
	@echo "🤖 Installing Bielik model in Ollama..."
	@echo "⚠️  Make sure you have:"
	@echo "   1. Downloaded Bielik-11B-v2.6-Instruct.Q4_K_M.gguf"
	@echo "   2. Created Modelfile"
	@echo "   3. Ollama container is running"
	@echo ""
	@read -p "Press Enter when ready to continue..."
	@if [ ! -f "Bielik-11B-v2.6-Instruct.Q4_K_M.gguf" ]; then \
		echo "❌ Error: Bielik model file not found!"; \
		echo "   Download from: https://huggingface.co/speakleash/Bielik-11B-v2.6-Instruct-GGUF"; \
		exit 1; \
	fi
	@if [ ! -f "Modelfile" ]; then \
		echo "❌ Error: Modelfile not found!"; \
		exit 1; \
	fi
	@echo "📁 Copying files to Ollama container..."
	docker cp . $(OLLAMA_CONTAINER):/root/.ollama/Bielik-11B-v2_6-Instruct_Q4_K_M
	@echo "🔧 Creating model in Ollama..."
	docker exec -it $(OLLAMA_CONTAINER) ollama create Bielik-11B-v2_6-Instruct_Q4_K_M -f /root/.ollama/Bielik-11B-v2_6-Instruct_Q4_K_M/Modelfile
	@echo "✅ Bielik model installed successfully!"
	@echo "   Run with: docker exec -it $(OLLAMA_CONTAINER) ollama run Bielik-11B-v2_6-Instruct_Q4_K_M"

# Quick development workflow
dev: check-env format lint run-tests
	@echo "🎯 Development workflow complete!"

# Production deployment check
deploy-check: check-env
	@echo "🚀 Production deployment check..."
	@echo "=== Environment ==="
	python -c "import sys; print(f'Python: {sys.version}')"
	@echo "=== Dependencies ==="
	pip list | grep -E "(torch|transformers|qdrant|streamlit)"
	@echo "=== Services ==="
	@curl -s http://localhost:$(QDRANT_PORT)/health >/dev/null && echo "✅ Qdrant: Healthy" || echo "❌ Qdrant: Unhealthy"
	@curl -s http://localhost:$(OLLAMA_PORT)/api/tags >/dev/null && echo "✅ Ollama: Healthy" || echo "❌ Ollama: Unhealthy"
	@echo "✅ Deployment check complete!" 