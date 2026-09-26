# thundersquared Zima Store

Security-first ZimaOS v2 app store for trusted-LAN deployments.

Store URL:

`https://zima-store.oss.sqrd-cdn.com/store.json`

Configure repository secret `PAGES_DOMAIN` with value
`zima-store.oss.sqrd-cdn.com`. Publish workflow uses it for generated URLs and
Pages `CNAME` output.

Add that URL as a custom store in ZimaOS. This project publishes ZimaOS v2
metadata only. Legacy CasaOS v1 clients and `main.zip` stores are out of scope.
Manual Docker Compose import remains possible from each source definition.

## Included Apps

- Cloudflared: token-managed tunnel, no published port.
- MySpeed: bridge-mode speed-test monitoring on TCP 5216 with scheduled tests and persistent history.
- Jellyfin: LinuxServer bridge-mode media server on HTTP 8097, optional HTTPS
  8921, UDP discovery 7359/1900, read-only media, and configurable PUID/PGID
  ownership.
- Mosquitto: authenticated MQTT on TCP 1883 with first-run credential setup.
- Tailscale: kernel-mode client with persistent state and interactive login.
- Home Assistant: LinuxServer host-mode UI on TCP 8123 with zeroconf/mDNS/UPnP and Bluetooth discovery.
- Hermes Agent: gateway plus loopback-only dashboard on TCP 9119.
- TVHeadend: bridge-mode UI and HTSP on TCP 9981 and 9982 with GPU and DVB tuner passthrough.
- Zigbee2MQTT: bridge-mode Zigbee gateway on TCP 8080 with adapter hardware opt-in.

Every app image uses a pinned manifest-list digest and, where upstream
publishes one, an explicit version tag. Both
`amd64` and `arm64` are required. Hardware access remains opt-in except for
the documented Home Assistant Bluetooth D-Bus path and TVHeadend GPU/DVB
devices. Host networking is used only for documented discovery or VPN
exceptions. WAN exposure remains an
opt-in edit documented in the app metadata.

## Security Boundary

Definitions assume a trusted LAN. Do not expose app ports directly to the
Internet. Put externally reachable services behind an authenticated reverse
proxy, VPN, or tunnel. Never commit tunnel tokens, API keys, MQTT passwords,
Tailscale state, or Hermes data.

Hermes dashboard access is deliberately bound to host loopback. Use an SSH
tunnel or an authenticated Tailscale/Cloudflare path. The dashboard stores API
keys and must not be exposed to a LAN without an authentication layer.

TVHeadend starts in bridge mode without DVB devices, GPU devices, host
networking, or privileged mode. IPTV, SAT>IP, HDHomeRun, DVB adapters, and
multicast discovery require deliberate host-network/device changes.

MySpeed starts without password protection. Keep its HTTP port on a trusted LAN
while completing initial configuration and setting supported password protection;
put any externally reachable deployment behind an authenticated reverse proxy,
VPN, or tunnel. First startup downloads Ookla and LibreSpeed clients over
outbound HTTPS, so DNS, GitHub, or speed-test download failures can prevent
initialization. Scheduled tests consume WAN bandwidth; choose cron frequency
deliberately. Persistent MySpeed data includes speed history, password state,
node configuration, and integration or webhook credentials; treat volume
backups and migrations as sensitive.

MySpeed drops all Linux capabilities except `NET_ADMIN` and `NET_RAW`, which
Ookla requires for interface-bound speed tests. These permit network
administration and raw packet operations; keep MySpeed trusted-LAN-only and do
not add broader capabilities.

Home Assistant uses LinuxServer host networking for zeroconf/mDNS/UPnP and
Bluetooth discovery. Read-only `/run/dbus`, `NET_ADMIN`, and `NET_RAW` enable
Bluetooth when host BlueZ is configured; override the source path with
`HOME_ASSISTANT_DBUS_PATH` when needed. Host mode exposes port 8123 and any
configured Home Assistant listeners directly on the host, so keep it
trusted-LAN-only. Set `HOME_ASSISTANT_PUID` and `HOME_ASSISTANT_PGID` to the
IDs owning the config directory. USB, serial, and other device mappings remain
disabled by default.

Jellyfin publishes UDP 7359 client discovery and UDP 1900 SSDP/DLNA discovery
for trusted-LAN use. Keep both ports off untrusted networks; UDP 1900 also
requires no competing host SSDP service. Port 8921 is published for HTTPS but
remains inactive until certificates and Jellyfin HTTPS settings are configured.

## Build

GitHub Actions runs the official pinned ZimaOS v2 builder. The generated
`dist/` directory is ignored locally and published as the Pages artifact.
Manual Compose import uses the files under `Apps/` directly.

## Updates

Renovate maintains Docker tags and digests plus GitHub Action pins. Routine
updates wait one day. Security updates can bypass that delay.

Renovate does not touch `x-casaos.version`. The ZimaOS client decides whether
an app has an update from the store manifest, and the store build drops any
`x-casaos.version` that is not valid semver from `index.json`, which leaves the
app with no detectable update path. `scripts/reconcile_versions.py` owns that
field instead, and runs on every publish before the store is built:

- `version` mirrors the main image tag, cleaned by the optional `version_prefix`
  and `version_suffix` keys in the same `x-casaos` block, so
  `ghcr.io/tailscale/tailscale:v1.102.5` publishes as `1.102.5` and
  `eclipse-mosquitto:2.1.2-alpine` publishes as `2.1.2`. Both keys are consumed
  by the reconcile script, not by the store build. A prefix or suffix that no
  longer matches the tag is ignored and reported by `check`
- LinuxServer `tvheadend` publishes no version tag, so it carries a counter
  version that the same rule increments on every digest change
- `release_notes` and `update_at` are regenerated from the image reference that
  actually shipped, which removes the stale release notes that image-only
  updates used to leave behind. Release notes always quote the unmodified tag,
  and `update_at` uses the `YYYY-MM-DD` form the store metadata contract
  recommends. Both are only rewritten when the app itself changed, so
  `update_at` stays an honest "last app update" date

No hand edits are needed. A hand-edited version is normalized back to the image
tag on the next publish, so treat `version` as derived state: change the image
reference instead. Run `uv run scripts/reconcile_versions.py reconcile` locally
if you want the metadata to match an edit before it ships. Apps are edited as
round-trip YAML documents, so comments, quoting, and prose formatting are
preserved. The script pins its own dependency, so `uv run` is the only entry
point needed. `check` runs in CI, and `check-index` asserts the built
`index.json` exposes a semver version for every app.

One limitation comes from the client, not the store: an upstream rebuild that
reuses an existing tag and only changes the digest updates the `content_hash`
but not `version`, so ZimaOS may not offer it as an update. A new upstream tag
is always visible.

## License

Repository code and store definitions are Apache-2.0. Upstream applications,
images, trademarks, and icons retain their respective licenses.
