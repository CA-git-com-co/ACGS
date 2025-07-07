# ACGS Docker Compose Makefile
# Constitutional Hash: cdd01ef066bc6cf2

.PHONY: help dev prod test monitoring mcp clean

help: ## Show this help message
	@echo "ACGS Docker Compose Commands:"
	@echo "Constitutional Hash: cdd01ef066bc6cf2"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment with hot reload
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.development.override.yml up

dev-detached: ## Start development environment in background
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.development.override.yml up -d

prod: ## Start production environment
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.production.override.yml up

prod-detached: ## Start production environment in background
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.production.override.yml up -d

test: ## Start testing environment
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.testing.override.yml up

monitoring: ## Start with monitoring stack
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.monitoring.yml up -d

mcp: ## Start MCP services for multi-agent coordination
	docker-compose -f compose-stacks/docker-compose.mcp.yml up -d

dev-full: ## Start development with monitoring
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.development.override.yml \
	              -f docker-compose.monitoring.yml up -d

prod-full: ## Start production with monitoring
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.production.override.yml \
	              -f docker-compose.monitoring.yml up -d

logs: ## View logs for all services
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml logs -f

status: ## Show status of all services
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml ps

clean: ## Stop and remove all containers, networks, and volumes
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml \
	              -f docker-compose.monitoring.yml down -v --remove-orphans
	docker-compose -f compose-stacks/docker-compose.mcp.yml down -v --remove-orphans

reset: ## Complete reset - stop, clean, and rebuild
	make clean
	docker system prune -f
	docker-compose -f docker-compose.base.yml \
	              -f docker-compose.services.yml build --no-cache

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -f http://localhost:8001/health && echo "✓ Constitutional AI"
	@curl -f http://localhost:8002/health && echo "✓ Integrity Service"
	@curl -f http://localhost:8010/health && echo "✓ API Gateway"
	@curl -f http://localhost:8008/health && echo "✓ Governance Synthesis"
