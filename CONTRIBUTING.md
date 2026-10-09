# Contributing

## Before Opening A Pull Request

- Read the app security boundary in `README.md` and the relevant Compose file.
- Do not include secrets, local paths outside documented defaults, or generated
  `dist/` files.

## App Changes

Keep runtime settings in Compose and store metadata in top-level `x-casaos`.
Every editable environment variable, published port, and persistent volume
needs a service-level `x-casaos` description.

Do not add Docker socket mounts, host root mounts, broad device mounts,
`privileged: true`, or direct WAN assumptions. Hardware access remains opt-in
unless app metadata documents a required exception. Discovery and host-network
changes must be documented with their security and networking consequences.

## Dependency Changes

Prefer Renovate-generated image and action updates. Keep image tags and
`x-casaos.version` synchronized. Omit optional `x-casaos.update_at` metadata to
avoid stale dates. Keep image references pinned to manifest-list digests and
confirm both required architectures before merge.

## Amp Orbs

`.agents/setup` prepares the Debian 12 orb snapshot with Docker Compose, `uv`,
the version-reconciliation dependencies, and the ZimaOS builder. It reads the
`uv` version and builder commit from the validation workflow. Warm setup skips
system installs and builder downloads, and lets `uv` check cached dependencies.
`.agents/resume` needs no services or authentication and installs nothing.

Validate from the repository root without a Docker daemon or app containers:

```bash
for compose_file in Apps/*/docker-compose.yml; do
  PUID=1000 PGID=1000 TZ=UTC docker compose -f "$compose_file" config -q
done
uv run --no-project scripts/reconcile_versions.py check

builder="$HOME/.cache/zima-store/build-appstore-action"
"$builder/.venv/bin/python" "$builder/scripts/build_appstore.py" \
  --source . --output dist --base-url https://validation.invalid
uv run --no-project scripts/reconcile_versions.py check-index dist/index.json
cp category-list.json recommend-list.json dist/
```

The build may query public image registries and download assets. Setup only
prepares tools and dependencies; it does not build or publish the store, pull
app images, or run the scheduled Trivy scans. No secrets are required.

## Review And Merge

Pull requests require one human approval and all required checks. Renovate does
not auto-merge. Keep commits signed when repository rules enforce signing.
