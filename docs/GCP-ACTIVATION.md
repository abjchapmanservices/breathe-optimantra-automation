# GCP activation: synthetic Cloud Run

**Project:** `divine-glazing-511316-a1`
**Region:** `us-central1`
**Repository:** `abjchapmanservices/breathe-optimantra-automation`

No login, reports, emails, QBO transactions, or patient data are handled by the deployment.

## 1. Administrator checks
Confirm the project belongs to Breathe, billing is enabled, Google Cloud BAA covers each selected service, and Cloud Run Jobs, IAM, Artifact Registry, and Secret Manager are approved for the intended future workflows.

An administrator can review `infra/gcp-bootstrap-synthetic.sh` and run it in Google Cloud Shell after validating the IAM bindings. This creates Artifact Registry and two dedicated service accounts. It does not provision secrets or enable scheduled runs.

## 2. Configure Workload Identity Federation (WIF)
Use Google Cloud IAM > Workload Identity Federation. Create or reuse a GitHub OIDC provider with conditions that restrict use to this GitHub repository AND the `gcp-synthetic` environment, not all GitHub users. Example attribute mapping:

- `google.subject=assertion.sub`
- `attribute.repository=assertion.repository`
- `attribute.ref=assertion.ref`
- `attribute.environment=assertion.environment`

Example attribute condition:

`assertion.repository == 'abjchapmanservices/breathe-optimantra-automation' && assertion.environment == 'gcp-synthetic' && assertion.ref == 'refs/heads/main'`

Bind the deploy service account's `roles/iam.workloadIdentityUser` to the restricted workload identity principal set in the WIF pool. Confirm that organization policies allow WIF and that only the intended provider can impersonate the account.

See Google's official documentation for OIDC provider and principal set setup. Avoid long-lived JSON service-account keys.

## 3. Create GitHub environment
Repository Settings > Environments > New environment: `gcp-synthetic`. Restrict deployment branches to `main`, and optionally require an authorized reviewer.

Create these **environment variables** under `gcp-synthetic`:

| Variable | Value |
| --- | --- |
| `GCP_ARTIFACT_REPOSITORY` | `breathe-reporting` |
| `GCP_RUNTIME_SERVICE_ACCOUNT` | `breathe-reporting-runtime@divine-glazing-511316-a1.iam.gserviceaccount.com` |
| `GCP_DEPLOY_SERVICE_ACCOUNT` | `breathe-github-deployer@divine-glazing-511316-a1.iam.gserviceaccount.com` |
| `GCP_WIF_PROVIDER` | Full provider resource name, e.g. `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL/providers/PROVIDER` |

Do not invent project numbers, WIF pool IDs, or provider IDs. Copy their exact resource names from the GCP Console.

## 4. Deploy manually
Open GitHub Actions > **Deploy synthetic Cloud Run Job to GCP** > Run workflow. The workflow runs without OptiMantra secrets and performs synthetic validation, pushes a container, deploys a Cloud Run Job, and executes it once.

If the run fails, check IAM permissions and provider restrictions. Do not loosen permissions blindly.

## 5. Future production gate
Before any live data processing:
- Confirm OptiMantra authorization and login conditions.
- Confirm the BAA, service suitability, retention, logging, and security review of the exact GCP project.
- Implement browser automation only in the approved GCP environment.
- Store username/password in GCP Secret Manager only. Grant only the runtime identity secret-accessor permissions on the two required secrets.
- Never upload patient-level data into GitHub Actions logs, artifacts, or repository.
- Ensure the export is immediately stripped of identifiers before authorized financial email delivery.
- Implement reconciliation, alerting, access control, error retry strategy and duplicate protection.
- Do not schedule or automate QBO postings until reviewed and explicitly enabled.
