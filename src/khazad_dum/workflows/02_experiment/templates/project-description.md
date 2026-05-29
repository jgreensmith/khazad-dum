# {{Project Title}} — Experiment Plan (iteration 2)

<!-- This is the experiment phase input. Promote the Research phase outputs
     (output/refined-project-plan.md + output/experiment-recommendations.md)
     into this file and refine by hand between gate cycles. -->

## Project Overview


## What the Experiment Must Determine
<!-- The open decisions the experiment exists to resolve, framed as WAN-comms
     questions: which protocol/transport, measured by which metric (latency
     distribution, throughput, jitter, setup time, loss), and what outcome
     decides each open question. -->


## Protocol(s) & Metrics Under Test
<!-- Which communication protocol(s)/transport(s) the local app and remote app
     will exercise across the WAN, and exactly which numbers you will compare. -->


## Constraints & Resources
<!-- Fixed topology (do not change): a remote app on AWS EC2 (Ubuntu) + a local
     app in a Docker container on the home lab (computron), talking over a
     Twingate TLS tunnel (the WAN link under test). khazad-dum drives the run
     and collects results via a listener on each endpoint. AWS regions:
     us-east-1/2, us-west-2, eu-west-1/2, eu-central-1 (pick one that gives a
     realistic WAN distance). -->


## Success Criteria
<!-- How will you know the experiment answered the question? Be specific about
     the numbers / thresholds that count as a result. -->
