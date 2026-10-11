# Production setup

The repository currently contains only non-production tests. Do not add passwords to code or send them in chat.

For an approved runtime, use a dedicated OptiMantra account and a managed secret store. Actual exports may contain patient information. Confirm OptiMantra automation permission, an appropriate HIPAA agreement and security controls, encrypted storage, access limitations, and retention before running live report collection.

In GitHub, Settings > Secrets and variables > Actions permits configuration of secrets for future approved jobs. Do not enter real OptiMantra credentials there for the current GitHub-hosted test workflow. Avoid passing real report data through GitHub-hosted runners until the environment has been approved.
