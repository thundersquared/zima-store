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
- Jellyfin: non-root media server, TCP 8096 only, read-only media mount.
- Mosquitto: authenticated MQTT on TCP 1883 with first-run credential setup.
- Tailscale: kernel-mode client with persistent state and interactive login.
- Home Assistant: bridge-mode UI on TCP 8123 without privileged access.
- Hermes Agent: gateway plus loopback-only dashboard on TCP 9119.
- TVHeadend: bridge-mode UI and HTSP on TCP 9981 and 9982.
- Zigbee2MQTT: bridge-mode Zigbee gateway on TCP 8080 with adapter hardware opt-in.

Every app image uses an explicit version tag and manifest-list digest. Both
`amd64` and `arm64` are required. Hardware access, host networking, and WAN
exposure are opt-in edits documented in the app metadata, not defaults.

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

## Build

GitHub Actions runs the official pinned ZimaOS v2 builder. The generated
`dist/` directory is ignored locally and published as the Pages artifact.
Manual Compose import uses the files under `Apps/` directly.

## Updates

Renovate maintains Docker tags/digests, GitHub Action pins, and matching
`x-casaos.version` metadata. Routine updates wait five days. Security updates
can bypass that delay. TVHeadend tracks the moving LinuxServer `latest` tag and
uses digest changes as its update signal.

## License

Repository code and store definitions are Apache-2.0. Upstream applications,
images, trademarks, and icons retain their respective licenses.
