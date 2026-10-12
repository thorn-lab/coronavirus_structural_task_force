#!/usr/bin/env bash
set -Eeuo pipefail

# Build validation containers.
#
# Haruspex: ARM64 with TensorFlow compatibility shim.
# AUSPEX:   AMD64 because its DIALS dependencies did not solve on ARM64.
#
# AUSPEX optimization:
# Remove the Micromamba package cache in the same Docker layer in which
# the environment is created, reducing the final image where possible.
#
# Usage:
#   ./setup-validation-docker.sh
#   ./setup-validation-docker.sh /path/to/tools
#
# Optional environment variables:
#   HARUSPEX_PLATFORM=linux/arm64
#   AUSPEX_PLATFORM=linux/amd64
#   HARUSPEX_REF=master
#   AUSPEX_REF=main

TOOLS_DIR="${1:-.validation-tools}"
HARUSPEX_PLATFORM="${HARUSPEX_PLATFORM:-linux/arm64}"
AUSPEX_PLATFORM="${AUSPEX_PLATFORM:-linux/amd64}"

HARUSPEX_REPO="https://github.com/thorn-lab/haruspex.git"
AUSPEX_REPO="https://github.com/YunyunGao/AUSPEX.git"

HARUSPEX_REF="${HARUSPEX_REF:-master}"
AUSPEX_REF="${AUSPEX_REF:-main}"

die() {
    echo "ERROR: $*" >&2
    exit 1
}

command -v git >/dev/null 2>&1 || die "Git is required."
command -v docker >/dev/null 2>&1 || die "Docker is required."
docker info >/dev/null 2>&1 || die "Start Docker Desktop and retry."

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" ||
    die "Run this script from inside the repository."

mkdir -p "$TOOLS_DIR"
TOOLS_DIR="$(cd "$TOOLS_DIR" && pwd)"

clone_if_missing() {
    local repo="$1"
    local dir="$2"
    local ref="$3"

    if [[ -d "$dir/.git" ]]; then
        echo "Reusing checkout: $dir ($(git -C "$dir" rev-parse --short HEAD))"
        return
    fi

    [[ ! -e "$dir" ]] ||
        die "$dir exists but is not a Git checkout; leaving it untouched."

    # --branch accepts branch or tag names (not commit SHAs).
    git clone --depth 1 --branch "$ref" "$repo" "$dir"
}

echo "=== Preparing repositories ==="

HARUSPEX_DIR="$TOOLS_DIR/haruspex"
AUSPEX_DIR="$TOOLS_DIR/auspex"

clone_if_missing "$HARUSPEX_REPO" "$HARUSPEX_DIR" "$HARUSPEX_REF"
clone_if_missing "$AUSPEX_REPO" "$AUSPEX_DIR" "$AUSPEX_REF"

# ------------------------------------------------------------
# Haruspex
# ------------------------------------------------------------

echo
echo "=== Preparing Haruspex ($HARUSPEX_PLATFORM) ==="

HARUSPEX_DOCKERFILE="$REPO_ROOT/docker/Dockerfile.arm64"
HARUSPEX_SHIM="$REPO_ROOT/docker/haruspex_compat.py"

[[ -f "$HARUSPEX_DOCKERFILE" ]] ||
    die "Missing tracked file: $HARUSPEX_DOCKERFILE"
[[ -f "$HARUSPEX_SHIM" ]] ||
    die "Missing tracked file: $HARUSPEX_SHIM"

mkdir -p "$HARUSPEX_DIR/docker"
cp "$HARUSPEX_DOCKERFILE" "$HARUSPEX_DIR/docker/Dockerfile.arm64"
cp "$HARUSPEX_SHIM" "$HARUSPEX_DIR/docker/haruspex_compat.py"

docker build \
    --platform "$HARUSPEX_PLATFORM" \
    -f "$HARUSPEX_DIR/docker/Dockerfile.arm64" \
    -t haruspex:arm64 \
    "$HARUSPEX_DIR"

echo "Checking Haruspex CLI..."
docker run --rm --platform "$HARUSPEX_PLATFORM" \
    haruspex:arm64 --help

# ------------------------------------------------------------
# AUSPEX
# ------------------------------------------------------------

echo
echo "=== Preparing AUSPEX ($AUSPEX_PLATFORM) ==="

[[ -f "$AUSPEX_DIR/environment.yml" ]] ||
    die "AUSPEX environment.yml not found."

[[ -f "$AUSPEX_DIR/setup.py" || -f "$AUSPEX_DIR/pyproject.toml" ]] ||
    die "AUSPEX package metadata not found."

[[ -d "$AUSPEX_DIR/auspex" ]] ||
    die "AUSPEX Python package directory not found."

# Keep the generated Dockerfile outside the AUSPEX checkout.
AUSPEX_DOCKERFILE="$TOOLS_DIR/Dockerfile.auspex.validation"

cat > "$AUSPEX_DOCKERFILE" <<'DOCKERFILE'
FROM mambaorg/micromamba:1.5.10

WORKDIR /opt/auspex

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml

# Create the environment and clean the package cache in the same layer.
# Removing the cache prevents its files from being retained in an earlier
# image layer. Hard-linked files may limit the actual storage savings.
RUN micromamba create -y -n auspex -f /tmp/environment.yml \
    && micromamba clean --all --yes \
    && rm -rf /opt/conda/pkgs/*

COPY --chown=$MAMBA_USER:$MAMBA_USER . /opt/auspex

RUN micromamba run -n auspex python -m pip install --no-deps . \
    && test -x /opt/conda/envs/auspex/bin/auspex

ENTRYPOINT ["/opt/conda/envs/auspex/bin/auspex"]
DOCKERFILE

# BuildKit uses the Dockerfile-specific ignore file beside the Dockerfile.
# Exclude Git metadata and Python bytecode from the build context.
printf '.git\n__pycache__\n*.pyc\n' > "$AUSPEX_DOCKERFILE.dockerignore"

docker build \
    --platform "$AUSPEX_PLATFORM" \
    -f "$AUSPEX_DOCKERFILE" \
    -t auspex:amd64 \
    "$AUSPEX_DIR"

echo "Checking AUSPEX CLI..."
docker run --rm --platform "$AUSPEX_PLATFORM" \
    auspex:amd64 --help

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

echo
echo "Both images built and basic CLI checks passed."
echo "Haruspex image: haruspex:arm64 ($HARUSPEX_PLATFORM)"
echo "AUSPEX image:   auspex:amd64 ($AUSPEX_PLATFORM)"
echo "Note: CLI checks do not validate scientific inference."

echo
echo "=== Built image sizes ==="
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}' |
    awk 'NR == 1 || ($1 == "haruspex" && $2 == "arm64") || ($1 == "auspex" && $2 == "amd64")'