# Module 1: Scientific Agent Runtime V2

## Architecture review

WAVE already had three execution layers: the JSON-checkpoint `WorkflowController` for deterministic stage execution, the database-backed `UnifiedScientificWorkflowOrchestrator` for DBTL module sequencing and gates, and safe tool executors with timeouts, allowlists, retries, idempotency and error classification. Project events already provide the shared audit ledger. Modules 2–4 own reasoning, evidence and biological representation.

The missing control-plane concepts were a first-class scientific task spanning module runs, an explicit arbitrary dependency graph, a scientific capability registry richer than a function list, and a consolidated runtime-only execution/failure/feedback history. Module 1 adds those concepts without replacing either existing engine: runtime nodes delegate work to existing modules and the DBTL node points to the existing orchestrator.

Potential conflicts are avoided by storing references rather than copying module objects, never writing scientific knowledge, and never selecting a biological intervention. The default planner decomposes only into capability categories: diagnosis, evidence retrieval, world-model query, design generation, simulation, evaluation, human approval and DBTL execution.

## Runtime flow

```text
Scientific objective
  -> ScientificTask + dependency graph
  -> ready capability node(s)
  -> existing Module 2 / 3 / 4 / Virtual Cell / Evaluator / Orchestrator
  -> immutable RuntimeExecutionRecord
  -> graph readiness update
  -> explicit human approval gate
  -> existing DBTL orchestrator
```

Failures are classified and either returned to `ready` for an explicit retry or escalated to `human_review`. They are never silently discarded. Human decisions support approve, reject, request modification and override.

## Schemas

### ScientificTask

Required fields are `task_id`, objective, constraints, current stage, task status, completed and pending steps, module outputs, human actions and execution history. Additive fields link the project and existing workflow run and preserve structured failure state. Lifecycle values are created, planning, executing, waiting module, human review, completed and failed.

### RuntimeTaskNode

Each graph node contains a stable ID, task ID, scientific capability name, owning module, dependency node IDs, explicit status, input/output references and a human-approval flag. Nodes contain no scientific conclusions.

### ScientificCapability

Each registered capability describes its name, owning module, scientific capability, input and output schemas, limitations, provenance, uncertainty, invocation kind and invocation reference. This registry answers what a tool can scientifically do rather than only which function can be called.

### RuntimeExecutionRecord

The append-only record preserves task/node IDs, capability, module/tool, full input and output payloads, structured errors, provenance, start time and end time. Runtime memory consists only of these records plus task state and human actions.

## API and frontend

`/api/scientific-runtime/tasks` creates/lists tasks; task detail exposes graph and execution memory. Node completion and failure endpoints update state explicitly. Human-action endpoints implement governance. `/capabilities` registers and queries capability metadata. The project route `/projects/{project_id}/runtime` shows current task, graph nodes, execution history, failures and approval actions.

## Validation and limitations

Tests cover graph decomposition, dependency release, execution history, failure escalation and human modification. Python compilation, runtime tests, orchestrator regression and frontend build validate integration.

The planner is deliberately deterministic and capability-level; adaptive graph revision is currently represented by `request_modification` returning the task to planning, not autonomous replanning. Module invocation remains explicit through existing module APIs rather than an unrestricted generic dispatcher. This prevents Runtime from becoming a second agent framework or uncontrolled autonomous executor.
