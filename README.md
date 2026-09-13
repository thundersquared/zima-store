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
- Jellyfin: LinuxServer bridge-mode media server on HTTP 8097, optional HTTPS
  8921, UDP discovery 7359/1900, read-only media, and configurable PUID/PGID
  ownership.
- Mosquitto: authenticated MQTT on TCP 1883 with first-run credential setup.
- Tailscale: kernel-mode client with persistent state and interactive login.
- Home Assistant: LinuxServer host-mode UI on TCP 8123 with zeroconf/mDNS/UPnP and Bluetooth discovery.
- Hermes Agent: gateway plus loopback-only dashboard on TCP 9119.
- TVHeadend: bridge-mode UI and HTSP on TCP 9981 and 9982.
- Zigbee2MQTT: bridge-mode Zigbee gateway on TCP 8080 with adapter hardware opt-in.

Every app image uses an explicit version tag and manifest-list digest. Both
`amd64` and `arm64` are required. Hardware access remains opt-in except for
the documented Home Assistant Bluetooth D-Bus path. Host networking is used
only for documented discovery or VPN exceptions. WAN exposure remains an
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

Renovate maintains Docker tags/digests, GitHub Action pins, and matching
`x-casaos.version` metadata. Routine updates wait five days. Security updates
can bypass that delay. TVHeadend tracks the moving LinuxServer `latest` tag and
uses digest changes as its update signal.

## License

Repository code and store definitions are Apache-2.0. Upstream applications,
images, trademarks, and icons retain their respective licenses.
