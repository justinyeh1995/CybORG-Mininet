# Tests Notes

1. Unit Tests for individual functions and methods, such as the correct generation of YAML topologies, parsing of network commands, or translation of actions.
2. Integration Tests to verify that different modules (e.g., Topology Generator, CLI Manager, Action Translator) interact correctly.
3. System Tests to validate the complete functionality of the system, such as running a simulated network scenario from start to finish.
4. Performance Tests to measure the response times and resource usage under different network simulation loads.

## Is there a @BeforeAll, @AfterAll, @BeforeEach, @AfterEach equivalent in Python?

In Python, the `unittest` module provides the `setUpClass`, `tearDownClass`, `setUp`, and `tearDown` methods to perform setup and teardown operations for test cases. These methods can be used to achieve similar functionality as `@BeforeAll`, `@AfterAll`, `@BeforeEach`, and `@AfterEach` in JUnit.

In pytest, the `pytest` module provides fixtures that can be used to achieve similar functionality as `@BeforeAll`, `@AfterAll`, `@BeforeEach`, and `@AfterEach` in JUnit. For example, the `@pytest.fixture` decorator can be used to define setup and teardown functions that can be applied to test functions using the `@pytest.mark.usefixtures` decorator. Using a session-scoped fixture can achieve similar functionality as `@BeforeAll` and `@AfterAll` in JUnit.