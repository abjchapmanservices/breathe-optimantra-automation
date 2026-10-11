#!/usr/bin/env bash
# Run manually as a Breathe GCP administrator after reviewing the access model.
# This bootstraps a SYNTHETIC-ONLY deployment, not live OptiMantra access.
set -euo pipefail
PROJECT_ID="divine-glazing-511316-a1"
REGION="us-central1"
REPOSITORY="breathe-reporting"
RUNTIME_SA="breathe-reporting-runtime"
DEPLOY_SA="breathe-github-deployer"
: "${GITHUB_OWNER:=abjchapmanservices}"
: "${GITHUB_REPO:=breathe-optimantra-automation}"

gcloud config set project "$PROJECT_ID"
gcloud services enable artifactregistry.googleapis.com run.googleapis.com iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com cloudresourcemanager.googleapis.com
gcloud artifacts repositories describe "$REPOSITORY" --location "$REGION" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "$REPOSITORY" --repository-format=docker --location="$REGION" --description="Synthetic Breathe reporting images"
gcloud iam service-accounts describe "${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1 || \
  gcloud iam service-accounts create "$RUNTIME_SA" --display-name="Breathe reporting runtime"
gcloud iam service-accounts describe "${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1 || \
  gcloud iam service-accounts create "$DEPLOY_SA" --display-name="GitHub synthetic job deployer"

# Scoped Artifact Registry push, Cloud Run deploy, and runtime SA impersonation.
gcloud artifacts repositories add-iam-policy-binding "$REPOSITORY" --location="$REGION" \
  --member="serviceAccount:${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.developer"
gcloud iam service-accounts add-iam-policy-binding "${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --member="serviceAccount:${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

echo "Created image repository and service accounts."
echo "Next: configure restricted GitHub Workload Identity Federation and environment variables."
echo "Runtime SA: ${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Deploy SA: ${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Note: roles/run.developer is project-scoped. Review IAM before executing."
