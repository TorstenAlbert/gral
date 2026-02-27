# FeedbackAgent

Computes fitness score and adaptively tunes GA parameters based on results.

**Reads:** best_cost, problem.optimal, verification.pass_rate, feedback.stagnant_count, fitness_history, strategies.params
**Writes:** fitness_history (append), feedback.gap, feedback.pass_rate, feedback.stagnant_count, feedback.ready_for_test, strategies.params
**Rules:** fitness = (pass_rate×100) + 1/(gap+0.01) + log(coverage+1). Cap mutpb at 0.3. ready_for_test only when gap < 0.05 AND pass_rate >= 0.95.
