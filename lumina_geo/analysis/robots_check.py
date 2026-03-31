import sys
import urllib.robotparser
from urllib.parse import urlparse

from lumina_geo.reporting.models import AIAccessResult

MAJOR_AI_BOTS = {
    "GPTBot": "ChatGPT",
    "ChatGPT-User": "ChatGPT",
    "PerplexityBot": "Perplexity",
    "ClaudeBot": "Claude",
    "anthropic-ai": "Claude",
    "Google-Extended": "Google Gemini & AI Overviews",
    "Bingbot": "Microsoft Copilot",
}


def check_robots(target: str) -> AIAccessResult:
    if not target.startswith("http"):
        return AIAccessResult(
            checked=False,
            blocked_bots=[],
            all_bots_allowed=True,
            critical=False,
            fixes=[],
        )

    parsed = urlparse(target)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
    except Exception as exc:
        print(f"[lumina-geo] Warning: could not fetch robots.txt — {exc}", file=sys.stderr)
        return AIAccessResult(
            checked=False,
            blocked_bots=[],
            all_bots_allowed=True,
            critical=False,
            fixes=["Could not fetch robots.txt — verify it is publicly accessible."],
        )

    blocked: list[str] = []
    seen_platforms: set[str] = set()

    for bot, platform in MAJOR_AI_BOTS.items():
        if not rp.can_fetch(bot, target) and platform not in seen_platforms:
            seen_platforms.add(platform)
            blocked.append(f"{bot} ({platform})")

    critical = len(blocked) > 0
    fixes = [
        f"Unblock {entry} in robots.txt — this platform cannot currently cite your page."
        for entry in blocked
    ]

    print(
        f"[lumina-geo] robots.txt: {'BLOCKED: ' + ', '.join(blocked) if critical else 'all major AI bots allowed'}",
        file=sys.stderr,
    )

    return AIAccessResult(
        checked=True,
        blocked_bots=blocked,
        all_bots_allowed=not critical,
        critical=critical,
        fixes=fixes,
    )
