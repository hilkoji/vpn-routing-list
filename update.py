"""Build a plain-text GL.iNet subscription from public sources."""
import ipaddress
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = (
    ("https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Russia/inside-raw.lst", 800, False),
    ("https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Services/tiktok.lst", 1, False),
    ("https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Services/telegram.lst", 10, False),
    ("https://core.telegram.org/resources/cidr.txt", 1, True),
)


def parse(text, ipv4_only=False):
    result = set()
    for raw in text.splitlines():
        value = raw.strip().lower()
        if not value or value.startswith("#"):
            continue
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            if ipv4_only:
                raise ValueError("Non-network entry in the subnet source")
            name = value.lstrip(".")
            if len(name) > 253 or not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*",
                name,
            ) or ("." not in name and value != ".ua"):
                raise ValueError("Invalid domain entry")
            result.add(value)
        else:
            if not ipv4_only or network.version == 4:
                result.add(str(network))
    return result


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "vpn-routing-list/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Source exceeds size limit")
    return data.decode("utf-8-sig")


def build(root=ROOT, fetcher=fetch):
    entries = set()
    for url, minimum, ipv4_only in SOURCES:
        source = parse(fetcher(url), ipv4_only)
        if not minimum <= len(source) <= 10000:
            raise ValueError("Unexpected source size")
        entries.update(source)
    entries.update(parse((root / "additions.txt").read_text(encoding="utf-8")))
    exclusions = {line.strip().lower() for line in (root / "exclusions.txt").read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}
    entries.difference_update(exclusions)
    required = {"x.com", "youtube.com", "googlevideo.com", "telegram.org", "tiktok.com", "72.56.28.223/32"}
    if not required <= entries or ".ua" in entries or "ua" in entries:
        raise ValueError("Required additions or exclusions not preserved")
    output = root / "domains.txt"
    if output.exists():
        old = parse(output.read_text(encoding="utf-8"))
        if len(entries) < len(old) * 0.8:
            raise ValueError("List shrank by more than 20%; retaining previous version")
    content = "\n".join(sorted(entries)) + "\n"
    temporary = output.with_suffix(".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, output)
    return len(entries)


if __name__ == "__main__":
    print(f"Validated {build()} entries")
