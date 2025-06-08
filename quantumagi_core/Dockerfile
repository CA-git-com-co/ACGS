# Use Ubuntu 20.04 as it has the required libssl1.1
FROM ubuntu:20.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install base dependencies and system libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    libudev-dev \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 3. Install the specific Solana CLI version that matches the old dependencies
RUN sh -c "$(curl -sSfL https://release.solana.com/v1.10.29/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:${PATH}"

# 4. Install the corresponding older Anchor version
RUN cargo install --git https://github.com/project-serum/anchor --tag v0.25.0 anchor-cli --locked

# 5. Set up the workspace
WORKDIR /app
COPY . .

# 6. Clean up old lock file and target dir, then build
CMD rm -f Cargo.lock && anchor clean && anchor build
