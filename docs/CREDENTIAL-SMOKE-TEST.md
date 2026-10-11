# GCP credential injection test

After the organization confirms Cloud Run Jobs and Secret Manager are approved for the specific environment under its BAA, deploy a separate **credential-only** test job to GCP. Do not reuse or modify the synthetic financial reporting job. The test code is `src/credential_check.py`.

## What it does
- Checks that `OPTIMANTRA_USERNAME` and `OPTIMANTRA_PASSWORD` are set and nonempty
- Requires `LIVE_MODE=false`
- Prints only a pass/fail statement; never logs any credential values
- Does not connect to OptiMantra, retrieve a report, or access patient records

## Example, after approved deployment
Use an image built from the current reviewed Dockerfile and already published in the existing Artifact Registry. Replace IMAGE_URI with the exact image URI taken from the reviewed synthetic Cloud Run deployment; never guess it.

```bash
gcloud run jobs deploy breathe-credential-check \
  --project=divine-glazing-511316-a1 \
  --region=us-central1 \
  --image="IMAGE_URI" \
  --service-account=breathe-reporting-runtime@divine-glazing-511316-a1.iam.gserviceaccount.com \
  --command=python \
  --args=-m,src.credential_check \
  --set-env-vars=LIVE_MODE=false \
  --set-secrets=OPTIMANTRA_USERNAME=optimantra-username:latest,OPTIMANTRA_PASSWORD=optimantra-password:latest \
  --max-retries=0

gcloud run jobs execute breathe-credential-check \
  --project=divine-glazing-511316-a1 \
  --region=us-central1 --wait
```

Do not paste secret contents into CLI arguments. A successful credential test alone does **not** authorize live report downloads. Complete vendor automation permission, BAA scope and data handling review, and approved live login implementation first.
