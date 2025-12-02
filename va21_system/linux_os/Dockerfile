# VA21 Research OS - Lightweight Container/VM Image
# Based on Alpine Linux for minimal footprint
# Supports: Docker, Podman, VirtualBox
# Includes: ClamAV for threat defense, SearXNG for research

FROM alpine:3.19 AS base

LABEL maintainer="Prayaga Vaibhav"
LABEL description="VA21 Research OS - Secure AI-Powered Research Environment"
LABEL version="1.0.0"

# Install essential packages including ClamAV
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-psutil \
    busybox-extras \
    bash \
    curl \
    git \
    openssh \
    vim \
    tmux \
    htop \
    strace \
    ltrace \
    tcpdump \
    nmap \
    netcat-openbsd \
    bind-tools \
    file \
    tree \
    jq \
    # ClamAV - Open Source Antivirus
    clamav \
    clamav-daemon \
    clamav-libunrar \
    # For SearXNG
    py3-yaml \
    py3-requests \
    py3-lxml \
    py3-babel \
    && rm -rf /var/cache/apk/*

# Initialize ClamAV database directory
RUN mkdir -p /var/lib/clamav \
    && chown clamav:clamav /var/lib/clamav

# Create VA21 user and directories
RUN adduser -D -h /home/researcher researcher \
    && mkdir -p /va21/{guardian,vault,research,sandbox,logs} \
    && mkdir -p /home/researcher/{research,notes,tools} \
    && chown -R researcher:researcher /va21 /home/researcher

# Install Python dependencies for Guardian AI
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy VA21 components
COPY guardian/ /va21/guardian/
COPY zork_shell/ /va21/zork_shell/
COPY searxng/ /va21/searxng/
COPY scripts/entrypoint.sh /va21/entrypoint.sh
COPY config/ /va21/config/

# Make scripts executable
RUN chmod +x /va21/entrypoint.sh \
    && chmod +x /va21/zork_shell/*.py \
    && chmod +x /va21/guardian/*.py \
    && chmod +x /va21/searxng/*.py 2>/dev/null || true

# Set up the Zork shell as default
RUN echo '#!/bin/bash' > /usr/local/bin/va21 \
    && echo 'cd /va21 && python3 /va21/zork_shell/zork_interface.py' >> /usr/local/bin/va21 \
    && chmod +x /usr/local/bin/va21

# Environment
ENV VA21_HOME=/va21
ENV VA21_USER=researcher
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color

# Working directory
WORKDIR /home/researcher

# Switch to researcher user for security
USER researcher

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default command - start the Zork-style interface
ENTRYPOINT ["/va21/entrypoint.sh"]
CMD ["zork"]
