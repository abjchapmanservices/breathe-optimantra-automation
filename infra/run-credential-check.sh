#!/usr/bin/env bash
# Deploy a separate credential-presence check using the image already deployed
# by the synthetic GitHub pipeline. No credential values are printed.
set -euo pipefail
PROJECT="divine-glazing-511316-a1"
REGION="us-central1"
SOURCE_JOB="breathe-optimantra-reporting"
TEST_JOB="breathe-credential-check"
RUNTIME_SA="breathe-reporting-runtime@${PROJECT}.iam.gserviceaccount.com"

gcloud iam service-accounts describe "$RUNTIME_SA" --project="$PROJECT" >/dev/null
for secret in optimantra-username optimantra-password; do
  gcloud secrets describe "$secret" --project="$PROJECT" >/dev/null
done

IMAGE="$(gcloud run jobs describe "$SOURCE_JOB" \
  --project="$PROJECT" --region="$REGION" \
  --format='value(spec.template.spec.template.spec.containers[0].image)')"
if [[ -z "$IMAGE" ]]; then
  echo "No deployed synthetic image found. Rerun the GitHub synthetic deployment."
  exit 1
fi

gcloud run jobs deploy "$TEST_JOB" \
  --project="$PROJECT" --region="$REGION" \
  --image="$IMAGE" \
  --service-account="$RUNTIME_SA" \
  --command=python \
  --args=-m,src.credential_check \
  --set-env-vars=LIVE_MODE=false \
  --set-secrets=OPTIMANTRA_USERNAME=optimantra-username:latest,OPTIMANTRA_PASSWORD=optimantra-password:latest \
  --max-retries=0 \
  --task-timeout=300s

gcloud run jobs execute "$TEST_JOB" \
  --project="$PROJECT" --region="$REGION" --wait
echo "Credential job finished. Check execution status; credential values were not printed by this script."
