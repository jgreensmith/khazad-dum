
# Test Development Workflow (Red Phase)

## Objective
Define the expected behavior of the feature by writing comprehensive tests that specify the expected behavior at multiple levels. Tests should fail as this workflow is scoped only to the red phase. No production code should be written in this phase, only tests that reference the empty methods from the feature's modules. **Do NOT modify any existing tests.** Your role is only to write **NEW** tests that define the expected behavior of the feature without implementing any production code.

## Assumptions
- The feature's architecture and module structure has already been designed in the design phase with skeleton implementations for new code. 
- These skeleton implementations have correct method signatures but empty bodies (`todo!()`, `panic!()`, or `unimplemented!()`), so they compile successfully but do not yet implement any logic.


## Requirements

### Stage 1: Create Comprehensive Tests
1. Write unit tests for individual components (structs, functions, validators)
   - Place unit tests in `#[cfg(test)]` modules within the same file as the code being tested
   - Unit tests should be close to the implementation for context and maintainability
2. Write integration tests that verify end-to-end feature behavior
   - Place integration tests in a new `e2e_tests` crate as separate files
   - Each integration test file should focus on a specific feature workflow or scenario
3. Tests must cover:
   - Normal/happy path cases for complete feature workflows
   - Edge cases and boundary conditions
   - Error conditions, invalid inputs, and failure scenarios
   - Integration between multiple components
4. Tests should be well-documented with comments explaining what they validate and why

### Stage 2: Complete Red Phase
1. Ensure all tests compile and fail (red phase)
2. Ensure NO production code is written, only tests. skeleton implementations should still have correct method signatures but empty bodies (`todo!()`, `panic!()`, or `unimplemented!()`), so they compile successfully but do not yet implement any logic.


## Test Design Requirements

- **Test File Organization**:
  - Unit tests: Place in `#[cfg(test)]` modules within the same `.rs` file as the code being tested
  - Integration tests: Place in separate `.rs` files in the `e2e_tests` crate
  - Each integration test file should have a descriptive name reflecting the feature or workflow it tests
- **Clear Test Naming**: Use descriptive test names that indicate feature behavior and expected outcome
- **Well-Documented Tests**: Include comments explaining the purpose, setup, expected outcome, and why each test case matters
- **Comprehensive Coverage**: 
  - All public API endpoints and methods used by the feature
  - All error paths and validation logic
  - Boundary conditions and edge cases
  - Integration between components
- **Single Responsibility**: Each test validates one specific behavior; avoid testing multiple concerns in a single test
- **Arrange-Act-Assert Pattern**: Structure tests with clear setup, action, and assertion sections
- **Meaningful Assertions**: Use assertions that provide clear failure messages when tests fail
- **Mock/Fixture Strategy**: Define how external dependencies will be mocked or stubbed for unit tests
- **Test Independence**: Tests should be isolated and runnable in any order without side effects or dependencies

## Success Criteria

- [ ] **Stage 1 - Create Comprehensive Tests**:
  - [ ] Unit tests are placed in `#[cfg(test)]` modules within the same files as the code they test
  - [ ] Integration tests are placed in separate files in the `e2e_tests` crate
  - [ ] All unit test code compiles successfully without errors
  - [ ] All integration test code compiles successfully without errors
- [ ] **Stage 2 - Complete Red Phase**:
  - [ ] All tests fail when executed, confirming the red phase status
  - [ ] No production code is written; only tests are added referencing the empty method signatures from the design phase
  - [ ] Test cases cover normal behavior, edge cases, and error conditions comprehensively
  - [ ] Tests are well-documented with comments explaining their purpose and expected behavior

