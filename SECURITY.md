# Security Policy

## Reporting

Report suspected vulnerabilities privately through GitHub Security Advisories:

`https://github.com/thundersquared/zima-store/security/advisories/new`

If private reporting is unavailable, contact the repository maintainer through
GitHub and request a private channel. Do not open a public issue containing
credentials, exploit steps for a live host, or private configuration.

Never include tunnel tokens, API keys, MQTT credentials, Tailscale state,
Hermes data, session exports, or unredacted logs in a report.

## Supported Versions

Only the definitions on the `main` branch and the currently published GitHub
Pages bundle receive fixes. Pin an app definition to a reviewed commit when
operational change control requires it.

## Response Process

1. Acknowledge private reports within seven days.
2. Reproduce and classify the issue without requesting secrets.
3. Prepare a reviewed fix, digest update, or documented exception.
4. Publish a security advisory when disclosure is appropriate.
5. Retire affected image digests and update the published bundle.

Security fixes may bypass routine update age gates. No automatic merge or
automatic deployment is used for vulnerability fixes.

The CI builder is pinned to release `v1.1.2`, commit
`407bf02f7ca1d3d610c88c895dc28b016bdace48`, and runs without registry
credentials. Review the builder source before changing that pin.
