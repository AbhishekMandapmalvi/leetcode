"""
Generic QPS / storage / bandwidth estimator.

Inputs: DAU, actions per user per day, average payload size in bytes,
        retention in years, peak factor, read:write ratio.
Outputs: avg QPS, peak QPS, daily storage, total storage over retention,
         read QPS, write QPS, bandwidth.
"""

from dataclasses import dataclass

SECONDS_PER_DAY = 86_400
DAYS_PER_YEAR = 365


@dataclass
class EstimateInputs:
    dau: int
    actions_per_user_per_day: float
    payload_bytes: int
    retention_years: float = 1.0
    peak_factor: float = 2.0
    read_write_ratio: float = 1.0  # reads per write


@dataclass
class EstimateOutputs:
    write_qps_avg: float
    write_qps_peak: float
    read_qps_avg: float
    read_qps_peak: float
    daily_new_storage_bytes: float
    total_storage_bytes: float
    bandwidth_bytes_per_sec: float


def estimate(inp: EstimateInputs) -> EstimateOutputs:
    daily_actions = inp.dau * inp.actions_per_user_per_day
    write_qps = daily_actions / SECONDS_PER_DAY
    read_qps = write_qps * inp.read_write_ratio

    daily_bytes = daily_actions * inp.payload_bytes
    total_bytes = daily_bytes * DAYS_PER_YEAR * inp.retention_years

    return EstimateOutputs(
        write_qps_avg=write_qps,
        write_qps_peak=write_qps * inp.peak_factor,
        read_qps_avg=read_qps,
        read_qps_peak=read_qps * inp.peak_factor,
        daily_new_storage_bytes=daily_bytes,
        total_storage_bytes=total_bytes,
        bandwidth_bytes_per_sec=write_qps * inp.payload_bytes,
    )


def humanize_bytes(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} EB"


def humanize_qps(qps: float) -> str:
    if qps >= 1e6:
        return f"{qps/1e6:.2f} M QPS"
    if qps >= 1e3:
        return f"{qps/1e3:.2f} K QPS"
    return f"{qps:.2f} QPS"


def report(inp: EstimateInputs) -> None:
    out = estimate(inp)
    print("=== Inputs ===")
    print(f"DAU                  : {inp.dau:,}")
    print(f"Actions/user/day     : {inp.actions_per_user_per_day}")
    print(f"Payload size         : {humanize_bytes(inp.payload_bytes)}")
    print(f"Retention            : {inp.retention_years} years")
    print(f"Peak factor          : {inp.peak_factor}x")
    print(f"Read:write ratio     : {inp.read_write_ratio}:1")
    print("\n=== Outputs ===")
    print(f"Write QPS (avg/peak) : {humanize_qps(out.write_qps_avg)} / {humanize_qps(out.write_qps_peak)}")
    print(f"Read  QPS (avg/peak) : {humanize_qps(out.read_qps_avg)} / {humanize_qps(out.read_qps_peak)}")
    print(f"Daily new storage    : {humanize_bytes(out.daily_new_storage_bytes)}")
    print(f"Total storage        : {humanize_bytes(out.total_storage_bytes)}")
    print(f"Bandwidth (write)    : {humanize_bytes(out.bandwidth_bytes_per_sec)}/s")


if __name__ == "__main__":
    # Example: a generic social app
    report(EstimateInputs(
        dau=10_000_000,
        actions_per_user_per_day=5,
        payload_bytes=1_000,
        retention_years=3,
        peak_factor=2.5,
        read_write_ratio=100,
    ))
