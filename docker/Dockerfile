FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client git sshpass curl ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create ansible user and SSH key directory
RUN groupadd -r ansible && useradd -r -g ansible -m ansible \
    && mkdir -p /home/ansible/.ssh && chown ansible:ansible /home/ansible/.ssh \
    && chmod 0700 /home/ansible/.ssh

# Copy SSH private keys
COPY ./ssh-keys/ansible_ed25519 /home/ansible/.ssh/id_ed25519
COPY ./ssh-keys/azure_id_rsa /home/ansible/.ssh/id_rsa
COPY ./ssh-keys/chasty2_ed25519 /home/ansible/.ssh/chasty2_id_ed25519

# Set SSH key permissions
RUN chown ansible:ansible /home/ansible/.ssh/id_ed25519 \
    && chmod 600 /home/ansible/.ssh/id_ed25519 \
    && chown ansible:ansible /home/ansible/.ssh/id_rsa \
    && chmod 600 /home/ansible/.ssh/id_rsa \
    && chown ansible:ansible /home/ansible/.ssh/chasty2_id_ed25519 \
    && chmod 600 /home/ansible/.ssh/chasty2_id_ed25519

# Switch to ansible user
USER ansible

# Install Pulumi CLI
RUN curl -fsSL https://get.pulumi.com | sh

# Set PATH for pulumi and local bin
ENV PATH="/home/ansible/.pulumi/bin:/home/ansible/.local/bin:$PATH"

# Copy dependency files and install Python deps
COPY --chown=ansible:ansible pyproject.toml uv.lock /app/
WORKDIR /app
RUN uv sync --frozen

# Set uv project environment so uv run works from any workdir
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Ansible environment variables
ENV ANSIBLE_HOST_KEY_CHECKING=false
ENV ANSIBLE_GATHERING=smart
ENV ANSIBLE_RETRY_FILES_ENABLED=false
ENV ANSIBLE_PYTHON_INTERPRETER=auto_silent

# Upgrade podman collection (fix: nfs bind mount idempotency)
RUN uv run ansible-galaxy collection install --upgrade containers.podman

# Set entrypoint
COPY --chown=ansible:ansible ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]
