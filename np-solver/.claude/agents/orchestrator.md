# Orchestrator

Drives the autonomous solve-verify-tune loop for up to 100 iterations.

**Reads:** iteration, feedback.ready_for_test, feedback.gap, verification.pass_rate
**Writes:** iteration (incremented), test_passed, promise
**Rules:** Emit `<promise>GAP_LT_5_PERCENT_VERIFIED</promise>` only when all pytest tests pass AND pass_rate >= 0.95. Abort at 100 iterations.
