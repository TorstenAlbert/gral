# TestRunner

Runs the pytest suite when feedback.ready_for_test is True.

**Reads:** feedback.ready_for_test
**Writes:** test_passed, promise
**Rules:** Only runs tests/test_np_solver.py (the integration test). Never modifies test files. Reports pass/fail to orchestrator.
