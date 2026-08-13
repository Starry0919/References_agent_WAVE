# Concurrency stress report

The production process-wide semaphore is bounded and batch default is two LLM workers. A real provider attempt at workers=2 was made but did not complete, so throughput, rate-limit and duplicate-call rates are not estimable. Workers=4 was not attempted after workers=2 failed to yield durable results. Keep the conservative default at two until a controlled external run supplies evidence.
