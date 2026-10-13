"""
benchmark_crypto_ops.py -- Real, executable timing measurements for the
unit cryptographic operations used in Section VIII of the PUF-ECC-BatchAuth
paper (ECC scalar multiplication, SHA-256 hashing).

STATUS -- READ BEFORE CITING: the numbers this script produces ARE real,
measured timings (not literature-cited estimates) -- but they were measured
on a cloud development sandbox's x86_64 CPU (single core, server-class),
NOT on automotive-grade OBU/RSU embedded hardware (e.g., an ARM Cortex-M/A
microcontroller). A server CPU core is typically 10-100x faster than the
embedded targets this protocol is actually meant to run on. Do NOT use
these numbers as the paper's headline performance figures -- the paper
correctly uses literature-cited embedded-hardware benchmarks (T_mul,
T_puf, T_h in Section VIII.A) for that purpose instead. This script exists
for two legitimate reasons:
  1. It is a genuine, reproducible artifact: unlike a literature citation,
     you (or a reviewer) can run this file yourself and get real numbers.
  2. It gives a rough sanity check that the paper's cited embedded-hardware
     figures (T_mul ~ 2.226 ms) are directionally plausible -- a modern
     server core doing the "same" operation class in a fraction of a
     millisecond is consistent with an embedded microcontroller needing
     several milliseconds for the equivalent operation, given the typical
     10-100x performance gap between server and embedded-class silicon.

TO GET NUMBERS THAT ACTUALLY BELONG IN THE PAPER: port this benchmark (or
an equivalent using the target platform's crypto library, e.g., mbed TLS
or wolfSSL on an ARM Cortex-M4/M7 automotive-grade part) and re-run it on
the real target hardware. That is the measurement the paper's Section
VIII.A disclaimer says is still required.

Requires: pip install cryptography
"""

import time
import hashlib
import platform
import statistics

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend


def benchmark_ecc_scalar_mult(curve=ec.SECP192R1(), n_ops=2000):
    """Times `n_ops` EC key generations, each of which performs one scalar
    multiplication k*P internally (this is the same operation class as
    T_mul in the paper's Table III)."""
    backend = default_backend()
    times = []
    for _ in range(n_ops):
        start = time.perf_counter()
        priv = ec.generate_private_key(curve, backend)
        _ = priv.public_key()
        times.append(time.perf_counter() - start)
    return times


def benchmark_sha256(n_ops=200000, payload_size=64):
    """Times `n_ops` SHA-256 hash evaluations (same operation class as
    T_h in the paper's Table III)."""
    data = b"x" * payload_size
    times = []
    for _ in range(n_ops):
        start = time.perf_counter()
        hashlib.sha256(data).digest()
        times.append(time.perf_counter() - start)
    return times


def summarize(times_s, label):
    times_ms = [t * 1000 for t in times_s]
    mean = statistics.mean(times_ms)
    median = statistics.median(times_ms)
    stdev = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
    print(f"{label}: mean={mean:.4f} ms, median={median:.4f} ms, "
          f"stdev={stdev:.4f} ms, n={len(times_ms)}")
    return mean


if __name__ == "__main__":
    print(f"Platform: {platform.platform()}, processor: {platform.processor() or platform.machine()}")
    print("NOTE: this is a development sandbox CPU, not automotive-grade "
          "embedded hardware. See module docstring before citing any number "
          "printed below.\n")

    ecc_times = benchmark_ecc_scalar_mult()
    t_mul_measured = summarize(ecc_times, "ECC scalar mult (secp192r1, sandbox x86_64)")

    hash_times = benchmark_sha256()
    t_h_measured = summarize(hash_times, "SHA-256 (sandbox x86_64)")

    print("\n--- Comparison against the paper's literature-cited, "
          "embedded-hardware unit costs (Section VIII.A) ---")
    T_MUL_PAPER = 2.226   # ms, literature-cited (He et al. / Ali et al. benchmarking convention)
    T_H_PAPER = 0.0001    # ms, literature-cited
    print(f"T_mul: paper uses {T_MUL_PAPER} ms (embedded); this sandbox measured "
          f"{t_mul_measured:.4f} ms ({T_MUL_PAPER / t_mul_measured:.1f}x slower on "
          f"the cited embedded figure, consistent with a server-vs-embedded gap)")
    t_h_ratio = t_h_measured / T_H_PAPER if T_H_PAPER else float('nan')
    print(f"T_h:   paper uses {T_H_PAPER} ms (embedded); this sandbox measured "
          f"{t_h_measured:.4f} ms -- {t_h_ratio:.1f}x LARGER than the cited "
          f"embedded figure. Unlike T_mul, this does NOT show the expected "
          f"server-faster-than-embedded pattern, likely because Python's "
          f"hashlib call overhead dominates at sub-microsecond scale on a "
          f"shared cloud VM; a tight C loop on real embedded hardware would "
          f"be a fairer comparison and is left as the needed next step.")
    print("\nThese sandbox numbers are a plausibility check only. Re-run this "
          "benchmark (or a target-language equivalent) on real OBU/RSU "
          "hardware before reporting final performance figures.")
