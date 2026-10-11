#!/usr/bin/env bash
# Reference commands only. Do not execute without project/security approval.
set -euo pipefail
: "${GCP_PROJECT_ID:?Set approved GCP project ID}"
: "${GCP_REGION:?Set approved GCP region}"
: "${IMAGE_URI:?Set approved image URI}"
: "${RUNTIME_SA:?Set Cloud Run job runtime service account email}"

# All commands run under your authenticated, authorized gcloud identity.
# Do not grant credential access in synthetic mode.
gcloud config set project "$GCP_PROJECT_ID"
gcloud run jobs deploy breathe-optimantra-reporting \
  --region "$GCP_REGION" \
  --image "$IMAGE_URI" \
  --service-account "$RUNTIME_SA" \
  --set-env-vars LIVE_MODE=false,REPORT_MODE=synthetic \
  --task-timeout=600s \
  --max-retries=0

# When authorized, manually execute synthetic validation:
# gcloud run jobs execute breathe-optimantra-reporting --region "$GCP_REGION" --wait
