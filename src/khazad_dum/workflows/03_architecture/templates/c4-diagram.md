# C4 Architecture — {{PROJECT}}

## Level 1 — System Context

```mermaid
C4Context
  title System Context for {{PROJECT}}
  Person(user, "{{Actor}}", "{{description}}")
  System(system, "{{System name}}", "{{what it does}}")
  System_Ext(ext, "{{External system}}", "{{description}}")
  Rel(user, system, "{{interaction}}")
  Rel(system, ext, "{{interaction}}")
```

## Level 2 — Containers

```mermaid
C4Container
  title Container diagram for {{PROJECT}}
  Person(user, "{{Actor}}", "{{description}}")
  Container_Boundary(c, "{{System name}}") {
    Container(app, "{{Container}}", "Rust", "{{responsibility}}")
    ContainerDb(db, "{{Datastore}}", "{{tech}}", "{{what it holds}}")
  }
  Rel(user, app, "{{interaction}}")
  Rel(app, db, "{{reads/writes}}")
```

## Architectural Notes
<!-- Key boundaries, data flow, and decisions that the diagrams don't fully capture. -->
- {{note}}
