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

## Review And Merge

Pull requests require one human approval and all required checks. Renovate does
not auto-merge. Keep commits signed when repository rules enforce signing.
