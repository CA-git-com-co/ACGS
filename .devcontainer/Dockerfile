# Use the official Microsoft VS Code dev containers base image
FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    curl \
    wget \
    git \
    vim \
    nano \
    # Python development
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Node.js (will be updated by features)
    nodejs \
    npm \
    # Database clients
    postgresql-client \
    redis-tools \
    # System utilities
    htop \
    tree \
    jq \
    unzip \
    # Docker utilities
    docker.io \
    docker-compose \
    # Additional development tools
    tmux \
    zsh \
    fish \
    # Cleanup
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install UV (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install Rust (will be updated by features)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Install Solana CLI
RUN sh -c "$(curl -sSfL https://release.solana.com/v1.18.4/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:$PATH"

# Install Anchor CLI
RUN cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
RUN avm install latest && avm use latest

# Create workspace directory
WORKDIR /workspace

# Set up Python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install common Python packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
    # Development tools
    black \
    flake8 \
    mypy \
    isort \
    pytest \
    pytest-asyncio \
    pytest-cov \
    # Web frameworks
    fastapi \
    uvicorn \
    # Database
    sqlalchemy \
    alembic \
    asyncpg \
    redis \
    # AI/ML
    torch \
    transformers \
    accelerate \
    # Utilities
    pydantic \
    python-dotenv \
    httpx \
    aiofiles

# Install global Node.js packages
RUN npm install -g \
    typescript \
    ts-node \
    @types/node \
    eslint \
    prettier \
    nodemon \
    pm2

# Configure Git (will be overridden by user settings)
RUN git config --global init.defaultBranch main
RUN git config --global pull.rebase false

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to non-root user
USER $USERNAME

# Set up user environment
RUN echo 'export PATH="/opt/venv/bin:$PATH"' >> ~/.bashrc
RUN echo 'export PYTHONPATH="/workspace/services/shared:/workspace:$PYTHONPATH"' >> ~/.bashrc

# Install user-specific tools
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN echo 'source ~/.cargo/env' >> ~/.bashrc

# Set working directory
WORKDIR /workspace

# Default command
CMD ["sleep", "infinity"]
