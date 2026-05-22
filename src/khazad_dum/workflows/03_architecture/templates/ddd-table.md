# Domain Model — {{PROJECT}}

## Ubiquitous Language

| Term | Definition |
|------|------------|
| {{term}} | {{precise definition, no ambiguity}} |

## DDD Building Blocks

| Bounded Context | Aggregate | Entities | Value Objects | Domain Events | Invariants |
|-----------------|-----------|----------|---------------|---------------|------------|
| {{context}} | {{aggregate root}} | {{entities}} | {{value objects}} | {{events}} | {{rules that must always hold}} |

## Architectural Layers
<!-- The horizontal layers of the system. The Project Management phase (1.4) cuts
     VERTICAL slices across these layers: each slice is one feature delivered
     end-to-end through every layer it touches. Define each layer and what lives in
     it precisely, so "end-to-end" is unambiguous when the next phase slices.
     The four rows below are the default DDD layered architecture — rename, add, or
     remove layers to match the actual system. -->

| Layer | Responsibility | Key Components / Modules | Maps to (C4 container / crate) |
|-------|----------------|--------------------------|--------------------------------|
| Presentation / Interface | {{how actors interact — UI, API, CLI}} | {{...}} | {{...}} |
| Application | {{use-case orchestration, application services}} | {{...}} | {{...}} |
| Domain | {{aggregates, entities, domain logic — the core}} | {{...}} | {{...}} |
| Infrastructure | {{persistence, external services, messaging, config}} | {{...}} | {{...}} |
