# {{Project Title}} — Experiment Report

## Summary
<!-- 2–4 sentences: what was tested and the headline result. -->

## Setup
- **Topology:** remote app (AWS EC2, region …) ⇄ local app (home-lab Docker container), over a
  Twingate TLS tunnel.
- **Protocol(s) under test:**
- **Metric(s):**
- **Load / duration / sample count:**

## Results
<!-- Embed the generated figures and cite the numbers from output/graphs/stats.json. -->

![latency](graphs/latency-cdf.png)

| Metric | Value |
|--------|-------|
| samples | |
| median latency | |
| p95 latency | |
| throughput | |

## Interpretation
<!-- What the numbers mean for communicating over the WAN, judged against the plan's
     success criteria. Which open questions are now resolved? -->

## Limitations
<!-- Sample size, single region, variance, any failed runs. -->

## Open Questions for Architecture
<!-- Anything the experiment did not settle that the next phase must resolve. -->
