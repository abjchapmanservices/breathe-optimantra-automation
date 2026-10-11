#!/usr/bin/env bash
# Run ONLY after reviewing the exact image version, permissions, and terms.
# First deploys a disabled job. Execution requires an explicit second command.
set -euo pipefail
PROJECT="divine-glazing-511316-a1"
REGION="us-central1"
REPO="breathe-reporting"
RUNTIME_SA="breathe-reporting-runtime@${PROJECT}.iam.gserviceaccount.com"
: "${IMAGE_SHA:?Set the exact reviewed 40-character Git commit SHA}"
if [[ ! "$IMAGE_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "IMAGE_SHA must be a full git commit SHA."
  exit 1
fi
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/breathe-login-smoke:${IMAGE_SHA}"
gcloud run jobs deploy breathe-login-smoke \
  --project="$PROJECT" --region="$REGION" --image="$IMAGE" \
  --service-account="$RUNTIME_SA" \
  --set-env-vars=LOGIN_SMOKE_ENABLED=false,OPTIMANTRA_TERMS_APPROVED=false \
  --set-secrets=OPTIMANTRA_USERNAME=optimantra-username:latest,OPTIMANTRA_PASSWORD=optimantra-password:latest \
  --max-retries=0 --task-timeout=180s

echo "Disabled job deployed. Do not execute until live terms and selectors are approved."
echo "To run one approved test, separately execute:"
echo "gcloud run jobs execute breathe-login-smoke --project=$PROJECT --region=$REGION --wait --update-env-vars=LOGIN_SMOKE_ENABLED=true,OPTIMANTRA_TERMS_APPROVED=true"
