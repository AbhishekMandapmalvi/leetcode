"""
Reproduce the Twitter QPS + 5-year media storage estimate from chapter 2.

Assumptions
-----------
- 300M MAU
- 50% of MAU are DAU  -> 150M DAU
- 2 tweets/user/day on average
- 10% of tweets contain media (avg 1 MB)
- Tweet retention: 5 years
- Peak QPS ~ 2x average
"""

SECONDS_PER_DAY = 86_400
DAYS_PER_YEAR = 365


def humanize(n: float, units=("B", "KB", "MB", "GB", "TB", "PB", "EB")) -> str:
    for u in units:
        if n < 1024:
            return f"{n:.2f} {u}"
        n /= 1024
    return f"{n:.2f} ZB"


def main() -> None:
    mau = 300_000_000
    dau_fraction = 0.5
    tweets_per_user_per_day = 2
    media_fraction = 0.10
    media_avg_bytes = 1 * 1024 * 1024  # 1 MB
    retention_years = 5
    peak_factor = 2

    dau = int(mau * dau_fraction)
    daily_tweets = dau * tweets_per_user_per_day
    qps = daily_tweets / SECONDS_PER_DAY
    peak_qps = qps * peak_factor

    media_per_sec = qps * media_fraction
    daily_media_bytes = daily_tweets * media_fraction * media_avg_bytes
    total_media_bytes = daily_media_bytes * DAYS_PER_YEAR * retention_years

    print("=== Twitter back-of-the-envelope ===")
    print(f"MAU                  : {mau:,}")
    print(f"DAU (50% of MAU)     : {dau:,}")
    print(f"Daily tweets         : {daily_tweets:,}")
    print(f"Tweet QPS (avg)      : {qps:,.0f}")
    print(f"Tweet QPS (peak ~2x) : {peak_qps:,.0f}")
    print(f"Media tweets/sec     : {media_per_sec:,.0f}")
    print(f"Daily new media      : {humanize(daily_media_bytes)}")
    print(f"5-year media storage : {humanize(total_media_bytes)}")


if __name__ == "__main__":
    main()
