
# Implement Cargo Workspace

## Objective
Restructure the project into a Cargo workspace with separate server and client crates. Scope is **project structure only**. Do not implement client functionality yet.

## Important
- The **client is a new feature** and should not be built or coded in this prompt
- Focus only on workspace organization and directory structure
- **Do not modify existing tests**

## Requirements
1. Create a root `Cargo.toml` defining the workspace with server and client members
2. Create `server/` directory and move existing server code into it with its own `Cargo.toml`
3. Create `client/` directory with a minimal `Cargo.toml` (structure only, no implementation)
4. Update module paths and references to reflect new structure
5. Ensure the server crate compiles independently

## Success Criteria
- Workspace structure is properly configured with root and member `Cargo.toml` files
- Server crate compiles without errors
- Existing tests continue to pass
- No code is lost or broken during migration