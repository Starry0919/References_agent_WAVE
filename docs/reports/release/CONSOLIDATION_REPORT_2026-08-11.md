# WAVE Agent Platform Consolidation Report

Date: 2026-08-11

## Conclusion

The `WAVE_Agent_Platform` directory created on 2026-08-10 was an independent copy of the main WAVE application, not a complete consolidation of the former repository. The original handoff explicitly excluded research prompts, references, the standalone vEcoli project, historical run snapshots, and repository metadata.

This consolidation keeps the runnable WAVE application at the directory root and places non-core but non-disposable material under `project_assets/` and `archive/`.

## Active application

- Backend: `harness/`
- Frontend: `frontend/`
- Workflows: `workflows/`
- Knowledge: `knowledge/`
- Tests: `tests/`
- Embedded Poe Code CLI: `.poe-code-cli/`

The post-copy System Prompt externalization change from the former working tree was merged into the active application. Its prompt is now at `harness/paper_extraction/prompts/experimental_design_system_prompt.md`; both the prompt content and `SKILL.md` content participate in the extraction cache identity. The newer transport-exit recovery behavior in the consolidated copy was retained.

## Preserved project assets

- `project_assets/research_prompts/`: research prompts, design notes, and the standalone experimental-design extraction component.
- `project_assets/reference/`: papers, converted references, evaluation material, and supporting scripts.
- `project_assets/independent_projects/vEcoli/`: standalone vEcoli source tree and its own Git history. Its local virtual environment was deliberately excluded because it is reproducible.
- `project_assets/historical_runs/root/`: former repository-level run states, result JSON files, and generated outputs retained for reproducibility.

## Preserved archive material

- `archive/repository_handoff_2026-08-10/`: the documentation-only reorganization reports produced on 2026-08-10 and the former repository-level diagram.
- `archive/original_main_runtime/`: the former main application's older ledger, workflow runs, workspace state, paper artifacts, and nested Git backup. These may contain research history that is not byte-identical to the active copy.
- `archive/legacy_agent_materials/`: helper notes and configuration material that was outside the copied application.

## Intentionally not consolidated

The following items are reproducible caches, installed dependencies, empty directories, duplicate packages, or a redundant ZIP copy. They may be deleted after this report is reviewed:

- Former Python virtual environments and Python caches under the old `agent/` tree.
- Former `node_modules`, `.next`, `.vinext`, and build outputs collected under the sibling `disposable_generated_assets/` directory.
- The old duplicate Poe Code CLI under the former `agent/` tree; the active copy is `.poe-code-cli/`.
- The sibling `WAVE_Agent_Platform.zip`, which is an older snapshot and is not the source of truth.
- Sibling `.pytest_cache/`, `.claude/`, and `test/` directories when empty or cache-only.
- The sibling `.git/` shell left by Windows after its contents were moved. It contains no files; the working repository metadata is now `WAVE_Agent_Platform/.git/`.

No file was deleted during consolidation.

## Verification

- The active extraction regression test file passed after merging the external System Prompt change: 10 tests passed.
- Backend `import main; import harness` passed.
- The broader paper-extraction test group exceeded a 180-second command limit without emitting a failure; it is recorded as incomplete, not failed. The system Python also lacks optional `PyMuPDF/fitz`, while the former virtual environment contains it.
- The frontend production build passed: TypeScript validation completed and Vite transformed 2309 modules. Vite reported the pre-existing large-chunk performance warning.
- Git metadata and history were moved into this directory so this directory is the repository root.
- The active `main`, `origin/main`, and `HEAD` references all resolve to commit `c198f88`.
