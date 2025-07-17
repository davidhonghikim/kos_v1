#!/bin/bash
# KOS v1 - Dynamic Docker Image Puller (Ordered)
# This script reads your generated .env file to pull the correct images
# for all your enabled services, in user-specified order.

ENV_FILE=".env"
FAILED_LOG="logs/failed_images.log"

if [ ! -f "$ENV_FILE" ]; then
  echo "[ERROR] The main .env file was not found at: $ENV_FILE"
  echo "[INFO] Please run the environment loader script first:"
  echo "  python3 scripts/installer/env_loader.py"
  exit 1
fi

mkdir -p "$(dirname "$FAILED_LOG")"

ORDERED_IMAGES=()
ROCM_IMAGE=""

# 1. Core DBs
for key in POSTGRES REDIS NEO4J MINIO ELASTICSEARCH WEAVIATE MONGO; do
  img=$(grep "KOS_${key}_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
  [ -n "$img" ] && ORDERED_IMAGES+=("$img")
done
# 2. Ollama
img=$(grep "KOS_OLLAMA_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
[ -n "$img" ] && ORDERED_IMAGES+=("$img")
# 3. OpenWebUI
img=$(grep "KOS_OPENWEBUI_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
[ -n "$img" ] && ORDERED_IMAGES+=("$img")
# 4. NVIDIA
img=$(grep "KOS_NVIDIA_GPU_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
[ -n "$img" ] && ORDERED_IMAGES+=("$img")
# 5. Workflow
for key in N8N PENPOT NEXTCLOUD SUPABASE; do
  img=$(grep "KOS_${key}_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
  [ -n "$img" ] && ORDERED_IMAGES+=("$img")
done
# 6. Monitoring
for key in PROMETHEUS GRAFANA CADVISOR; do
  img=$(grep "KOS_${key}_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
  [ -n "$img" ] && ORDERED_IMAGES+=("$img")
done
# 7. Large images (A1111, ComfyUI, HuggingFace, InvokeAI)
for key in AUTOMATIC1111 COMFYUI HUGGINGFACE INVOKEAI; do
  img=$(grep "KOS_${key}_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)
  [ -n "$img" ] && ORDERED_IMAGES+=("$img")
done
# 8. ROCm (commented out next to NVIDIA)
ROCM_IMAGE=$(grep "KOS_AMD_GPU_IMAGE=" "$ENV_FILE" | cut -d'=' -f2-)

# Remove duplicates
ORDERED_IMAGES=($(printf "%s\n" "${ORDERED_IMAGES[@]}" | awk '!seen[$0]++'))

# Logging pull order
echo "[INFO] Pull order:" 
for img in "${ORDERED_IMAGES[@]}"; do
  echo "  $img"
done
[ -n "$ROCM_IMAGE" ] && echo "  # ROCm image (commented): $ROCM_IMAGE"
echo "-------------------------------------------"

rm -f "$FAILED_LOG"
PULLED_SUCCESS=0
PULLED_FAIL=0

retry_pull() {
  local image=$1
  [ -z "$image" ] && return 0
  local max_attempts=3
  local attempt=1
  while [ $attempt -le $max_attempts ]; do
    echo "[INFO] Pulling '$image' (attempt $attempt/$max_attempts)..."
    if docker pull "$image"; then
      echo "[SUCCESS] Successfully pulled '$image'"
      return 0
    else
      echo "[WARN] Failed to pull '$image' (attempt $attempt)"
    fi
    ((attempt++))
    sleep 2
  done
  echo "[ERROR] Failed to pull '$image' after $max_attempts attempts. Logging to $FAILED_LOG"
  echo "$image" >> "$FAILED_LOG"
  return 1
}

for image in "${ORDERED_IMAGES[@]}"; do
  retry_pull "$image"
  if [ $? -eq 0 ]; then
    ((PULLED_SUCCESS++))
  else
    ((PULLED_FAIL++))
  fi
done

TOTAL_IMAGES=$((PULLED_SUCCESS + PULLED_FAIL))
echo "-------------------------------------------"
echo "Image Pull Summary:"
echo "  - Success: $PULLED_SUCCESS / $TOTAL_IMAGES"
echo "  - Failed:  $PULLED_FAIL / $TOTAL_IMAGES"
echo "-------------------------------------------"

if [ $PULLED_FAIL -gt 0 ]; then
  echo "[ERROR] Some images failed to pull. Check the log for details: $FAILED_LOG"
  cat "$FAILED_LOG"
  exit 1
else
  echo " 44c [SUCCESS] All configured images were pulled successfully."
  exit 0
fi