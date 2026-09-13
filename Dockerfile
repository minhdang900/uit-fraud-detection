# syntax=docker/dockerfile:1
FROM python:3.11.9-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libgomp1 is required by xgboost and scikit-learn at runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgomp1 \
 && apt-get clean \
 && find /var/lib/apt/lists -type f -delete

# Non-root user (docker-patterns: never run as root)
RUN groupadd -g 1001 app && useradd -u 1001 -g app -m -s /bin/bash app

# Create the Jupyter config dir owned by app BEFORE any named volume mounts
# over it. A fresh named volume inherits the image path's ownership; without
# this it mounts root-owned and the non-root user cannot write there.
RUN mkdir -p /home/app/.jupyter && chown -R app:app /home/app

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER app
EXPOSE 8888

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=8 \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8888/api').read()" || exit 1

# NOTE: do not add --ServerApp.allow_origin=*. The browser reaches this
# same-origin, so it buys nothing, and it disables the CORS protection that
# stops a malicious page you visit from driving this kernel (arbitrary code
# execution). Loopback binding does not help: the request would come from
# your own browser.
CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--ServerApp.root_dir=/work"]
