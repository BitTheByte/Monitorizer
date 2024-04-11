FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED=1

# Install openresty
RUN apt-get update && apt-get install -y --no-install-recommends gnupg curl ca-certificates && \
    curl https://openresty.org/package/pubkey.gpg -o pubkey.gpg && apt-key add pubkey.gpg && rm -rf pubkey.gpg && \
    echo "deb http://openresty.org/package/debian bullseye openresty" | tee /etc/apt/sources.list.d/openresty.list && \
    apt-get update && \
    apt-get -y --no-install-recommends install openresty

# Add docker binary
COPY --from=docker:latest /usr/local/bin/docker  /usr/local/bin/

# Add main entrypoint with tini
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

# Fake package to enable dependency caching
RUN mkdir -p /opt/src/monitorizer && touch /opt/src/monitorizer/__init__.py
COPY README.md /opt/src/README.md
COPY pyproject.toml /opt/src/pyproject.toml
RUN pip3 --default-timeout=1000 install /opt/src

# Real codebase
COPY monitorizer /opt/src/monitorizer
RUN pip3 install /opt/src/ --break-system-package && rm -rf /opt/src

COPY conf/nginx.conf /etc/openresty/nginx.conf

COPY *-entrypoint.sh /
RUN chmod +x /*-entrypoint.sh

ENTRYPOINT ["/usr/bin/tini", "-g", "--"]