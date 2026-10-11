# Breathe Google Cloud production architecture (pre-deployment)

## Architecture
- GitHub: source code, review and synthetic CI only.
- Google Cloud Artifact Registry: image repository for approved builds.
- Cloud Run **Jobs**: batch execution, using a dedicated least-privilege service account.
- Secret Manager: future credentials, accessible only by the specific runtime identity.
- Cloud Scheduler: future daily trigger, not enabled until secure live workflow is approved.
- Cloud Logging: metadata-only operational logs; no report contents, patient names or browser traces.

The current container intentionally runs **synthetic-only**. LIVE_MODE=true fails.
No real login, exports, emails or QuickBooks writes are implemented.

## Required confirmations before provisioning
1. Exact Google Cloud project ID and deployment region.
2. Which Google Cloud services are included in Breathe's signed BAA, and the security team's approval for this data flow.
3. Who can provision service accounts, Artifact Registry, Secret Manager, Cloud Run Jobs, IAM, and later Scheduler.
4. Whether GitHub Actions is allowed to build images. GitHub hosted runners must **not** receive PHI.
5. OptiMantra authorization/terms for automated access and a dedicated minimal-permission account.
6. Approved recipient list and delivery mechanism for summary-only reports.

## Safe rollout sequence
1. Verify synthetic GitHub test workflow.
2. Build a synthetic container using the GitHub container build test.
3. After the GCP administrator provisions the project resources, build/push the reviewed container image using Google Cloud approved deployment tooling.
4. Use the reference script in infra/cloud-run-job.example.sh to deploy an intentionally synthetic-only Cloud Run Job.
5. Test Cloud Run execution; verify no sensitive logging and review IAM.
6. Implement browser automation and report collection **only in the approved Cloud Run environment**, after external access authorization and security review.
7. Use Secret Manager for username/password; never store credentials in code, CSV files, GitHub issues, action logs, or chat. Do not add them to the current GitHub workflows.
8. Validate date filters, practitioner grouping removal, CSV export, parsing, approved secure retention, reconciliation, and idempotency.
9. Add approved summary email delivery and only then an explicit daily schedule.

## Credential procedure, once approved
Create separate secrets named `optimantra-username` and `optimantra-password` in the approved Google Cloud project's **Secret Manager**. Enter values directly in the Google Cloud Console or an approved administrator workflow. Grant the Cloud Run job service account `roles/secretmanager.secretAccessor` **only** on those two secrets. Avoid broader project-level secret access. Mount them as secrets at runtime, not build time. Rotate on staff departure or suspected exposure.

Do **not** use an administrator's personal OptiMantra account when a dedicated restricted service account is available. Any OptiMantra consent checkbox or site terms must be approved by the account owner; do not bypass security prompts.

## Deployment authentication
For future GitHub-to-Google deployment prefer Workload Identity Federation and narrowly scoped deployment permissions, not a long-lived Google service-account JSON key in GitHub. No credentials or GCP access are configured by this change.

## Privacy
GitHub's private repo setting and Google Cloud BAA alone do not automatically make every involved service or workflow HIPAA compliant. The specific services, configuration, retention, access, and disclosure paths need approval.
