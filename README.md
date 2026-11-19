# VPN routing list

Plain-text domain/IPv4 subscription for GL.iNet. Public routing destinations only; no client configuration or VPN credentials.

Sources: [itdoginfo/allow-domains](https://github.com/itdoginfo/allow-domains) Russia/inside-raw.lst, Services/tiktok.lst, Services/telegram.lst; [official Telegram IPv4 ranges](https://core.telegram.org/resources/cidr.txt).

`additions.txt` preserves local additions. `exclusions.txt` removes exact entries: the country-wide `.ua` suffix is excluded, while individual `.ua` domains remain eligible.

GitHub Actions builds the file daily at 22:15 UTC (01:15 Moscow), on relevant source changes, or manually. Scheduled runs can be delayed; check the latest successful run. GitHub may disable schedules in inactive public repositories, so this requires occasional maintenance. The router checks the published file using its own native subscription scheduler. Upstream failures or invalid data leave the previous file unchanged.

Subscription: https://raw.githubusercontent.com/hilkoji/vpn-routing-list/main/domains.txt

Run `python3 -m unittest -v` then `python3 update.py`. No third-party Python packages required.
