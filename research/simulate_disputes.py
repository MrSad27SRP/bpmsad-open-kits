"""Paired synthetic experiment. Run with Python 3."""
import math
import random
import statistics

rng = random.Random(2701)
cases = [(rng.expovariate(1 / 24), rng.expovariate(1 / 20),
          rng.expovariate(1 / 12)) for _ in range(10000)]

def metrics(times):
    p95 = sorted(times)[math.ceil(.95 * len(times)) - 1]
    return statistics.median(times), p95, 100 * sum(t > 72 for t in times) / len(times)

print("extra_hours,policy,median_hours,p95_hours,over_72_pct")
for overhead in (0, 6, 12, 18):
    baseline = [evidence + queue + review for evidence, queue, review in cases]
    parallel = [max(evidence, queue) + review + overhead
                for evidence, queue, review in cases]
    for policy, times in (("serial", baseline), ("parallel", parallel)):
        print(f"{overhead},{policy}," + ",".join(f"{m:.2f}" for m in metrics(times)))
