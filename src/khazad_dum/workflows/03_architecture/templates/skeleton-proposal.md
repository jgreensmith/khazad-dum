# Skeleton Project Proposal — {{PROJECT}}

## Stack
- Language / build: {{Rust / cargo workspace}}

## Workspace Layout
<!-- The directory/crate tree to be created in the $CWD root by the Complete step. -->
```
{{project}}/
  Cargo.toml            # workspace manifest
  crates/
    {{crate}}/
      Cargo.toml
      src/lib.rs
      tests/
```

## Crates / Modules

| Path | Responsibility | Maps to (C4 container / bounded context) |
|------|----------------|------------------------------------------|
| {{crates/...}} | {{what it owns}} | {{container / context}} |

## Testing
- **Predetermined test commands:** {{e.g. `cargo test`}}
- **Test layout:** {{where tests live, e.g. per-crate `tests/`}}

## Scaffold Commands
<!-- Exact commands the Complete step (1.3.2) runs to create the skeleton. Structure only. -->
```bash
{{e.g. cargo new --lib crates/core ...}}
```
