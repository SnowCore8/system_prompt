# Complex Logic: Decision Tables and State Tables

When rules involve multiple condition combinations or state transitions, do not put them in one large diagram. Use a
table as the source of truth; diagrams are overview only.

## When to Use

| Situation | Use |
|---|---|
| Multiple conditions select one action | Decision table |
| A task moves between states on events | State table |
| Both states and condition branches | State table; condition column references a decision table |
| Computation, loops, or data structures | Pseudocode or pure functions with table-driven tests |

## Decision Tables

### Decision Table Template

| Order | Condition A | Condition B | Condition C | Action |
|---|---|---|---|---|
| 1 | No | * | * | Report only |
| 2 | Yes | Yes | None | Refuse |
| 3 | Yes | Yes | Has plan | Execute |
| 4 | Yes | No | * | Execute |

- Order: first match wins, top to bottom; if you use "last match wins," say so.
- `*` means any value, and `-` means not applicable; define both symbols.
- Action: one observable result per row.
- Default: state which branch applies when no row matches.

### Decision Table Example: Authorization

| Order | Explicit consent | Production | Rollback plan | Action |
|---|---|---|---|---|
| 1 | No | * | * | Report only; do not execute |
| 2 | Yes | Yes | None | Refuse; require a rollback plan first |
| 3 | Yes | Yes | Has plan | Execute; keep the rollback path |
| 4 | Yes | No | * | Execute |

"Explicit consent" means direct, explicit approval for that operation; a vague "let's leave it like this" does not
count. If no row matches, reject and report by default.

## State Tables

### State Table Template

| Current state | Event | Condition | Next state | Action |
|---|---|---|---|---|
| Awaiting authorization | User consents | Non-production | Executing | Start changes |
| Awaiting authorization | User refuses | - | Rejected | Stop; do not work around it |

- Every state/event combination must be defined explicitly or fall to a default row.
- Mark terminal states; never silently return from a terminal state to executing.
- The condition column may reference a decision table's conclusion; do not repeat it.

### State Table Example: Inventory to Plan to Evaluate to Implement to Verify to Commit to Deliver to Done

| Current state | Event | Condition | Next state | Action |
|---|---|---|---|---|
| Inventory | Task accepted | Scope and authorization are clear | Plan | Record scope, current state, dependencies, and constraints |
| Inventory | Task accepted | Scope or authorization is unclear | Blocked | Ask for clarification or report; do not plan |
| Plan | Inventory complete | Splittable, or more than four steps | Evaluate | Define steps, owners, and acceptance; delegate or create a todo list |
| Plan | Inventory complete | Single linear path | Evaluate | Define a one-step-at-a-time plan; do not delegate |
| Evaluate | Plan approved | Risk is acceptable and reversible | Implement | Start the change with the chosen approach, rollback path, and platform tools |
| Evaluate | Plan approved | High risk or no rollback | Blocked | Ask for confirmation or propose an alternative |
| Blocked | Risk accepted | User accepts the residual risk | Implement | Apply the approved change |
| Implement | Change complete | Change stays within scope | Verify | Confirm the diff and freeze the change |
| Implement | Change in progress | Root cause is structural | Implement | Refactor; do not stack another patch |
| Implement | Blocker found | - | Blocked | Report the blocker and what is already done |
| Verify | Implementation complete | Relevant and full tests pass | Commit | Collect evidence and real output |
| Verify | Implementation complete | Tests fail or were not run | Implement | Fix; do not commit; if not run, say "not run" |
| Commit | Verification passed | Diff is clean and contains no secrets or build artifacts | Deliver | Review the diff, split commits, and write the message |
| Commit | Verification passed | Secret, build artifact, or scope creep found | Implement | Remove or repair the issue; do not commit |
| Deliver | Delivery sent | - | Done | Report delivery; close the task |
| Deliver | Feedback received | - | Inventory | Start a new cycle with the feedback |

For small tasks, collapse Inventory, Plan, and Evaluate into one pass; never skip Verify, Commit, or Deliver checks.
Any unlisted combination stays in the current state and reports; do not guess.

## Model-Friendly Writing

- Use booleans or enums in condition columns, not long sentences.
- Put one result in the action column; never write "handle as appropriate."
- Keep the table near the rule; do not put it only in an appendix.
- Add 3-5 boundary cases after the table: default, exception, conflict, insufficient information.
- When a diagram is needed, it is overview only; if diagram and table conflict, the table wins.
- When nesting exceeds two levels or the table starts repeating, split sub-decisions or switch to pseudocode or
  pure functions.

## Maintenance and Acceptance

- Change the table first, then the diagram; never hand-edit the diagram without syncing the table.
- Update boundary cases when rules change.
- When the logic is too complex for a table, write a pure function with table-driven tests; do not make the prompt
  carry an algorithm.
- Diagrams are overview only; the source of truth is always the table or code.
