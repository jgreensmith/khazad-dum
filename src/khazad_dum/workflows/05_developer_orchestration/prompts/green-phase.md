
# Build & Implementation Workflow (Green Phase)

## Objective
Make ALL failing tests pass. **Do NOT modify, add, or edit any existing tests.** This workflow assumes that new tests have  been written during red-phase for a new skeleton feature created during the design-phase. Your role is only to implement production code that makes all tests pass. 

## Requirements

### Phase 1: Implementation Cycle
1. Implement the minimum code required to make failing tests pass
2. Write clear, concise code with inline comments explaining logic
3. Run `cargo test` automatically after each implementation
4. **Do NOT modify, create, or edit any tests** - only write production code
5. Repeat this cycle until all tests pass

### Phase 2: Documentation & Polish
1. Once all tests pass:
   - Add or update Rust doc comments (///) for the function
   - Include examples in doc comments when appropriate
   - Update any relevant module-level documentation
   - Ensure code follows Rust style guidelines
2. Run `cargo fmt` and `cargo clippy --all-targets --all-features -- -D warnings` to ensure code quality
3. Run `cargo test` one final time to verify everything still works

## Implementation Guidelines
- Implement only what's necessary to pass the tests
- Avoid over-engineering or adding untested features
- Write code that is readable and maintainable
- Use appropriate Rust idioms and best practices
- Add inline comments explaining non-obvious logic
- **CRITICAL: Do not modify, create, or delete any test files or test code**
- **Only write production code to make existing tests pass**

## Documentation Requirements
- Write doc comments (///) for all public functions
- Include at least one example in doc comments
- Update module-level documentation if needed
- Ensure all types and parameters are documented
- Explain error cases in documentation

## Success Criteria
- [ ] All tests pass
- [ ] Minimum viable implementation complete
- [ ] Code has proper Rust documentation
- [ ] No compiler warnings
- [ ] Function behavior matches test expectations
- [ ] Code formatted with `cargo fmt`
- [ ] No clippy warnings with `cargo clippy`

## Notes

- Run cargo test after each implementation cycle
- Ensure all code changes maintain backward compatibility
- **Never touch test files or test code - if tests need changes, that is outside this workflow's scope**
- Tests are the specification; implement production code to satisfy them, not the other way around
