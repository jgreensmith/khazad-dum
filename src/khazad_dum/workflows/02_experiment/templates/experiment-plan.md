# {{Project Title}} — Experiment Plan

<!-- The specific WAN-comms experiment to run. Human-owned: stays UNCHANGED
     through the step (answer questionnaires in-file). The agent folds your
     answers into the refined experiment plan + payload under process/. -->

## What the Experiment Must Determine
<!-- The open decisions this experiment resolves, as WAN-comms questions: which
     protocol/transport, measured by which metric (latency distribution,
     throughput, jitter, setup time, loss), and what outcome decides each. -->


## Protocol(s) & Metrics Under Test
<!-- Which protocol(s)/transport(s) the local app and remote app exercise across
     the WAN, and exactly which numbers you will compare. -->


## Load & Result Shape
<!-- Load pattern (rate, sample count or duration) and the machine-readable
     result columns/fields/units the client should record. -->


## Success Criteria
<!-- The numbers/thresholds that count as a result. -->


## Fixed Topology (do not change)
<!-- Remote app on AWS EC2 (Ubuntu) ⇄ local app in a Docker container on the home
     lab, over a Twingate TLS tunnel (the WAN link under test). khazad-dum drives
     the run + collects results via a listener on each endpoint. AWS regions:
     us-east-1/2, us-west-2, eu-west-1/2, eu-central-1 — pick one that gives a
     realistic WAN distance. -->
