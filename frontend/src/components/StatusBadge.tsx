import { statusLabel } from "../lib/dates";

const STEPS = ["draft", "sent_to_broker", "executed", "done"] as const;

type Props = { status: string };

export function StatusBadge({ status }: Props) {
  return (
    <span className={`badge status-${status}`} title={statusLabel(status)}>
      {statusLabel(status)}
    </span>
  );
}

export function WorkflowSteps({ status }: Props) {
  const idx = STEPS.indexOf(status as (typeof STEPS)[number]);
  return (
    <div className="workflow" aria-label={`Workflow: ${statusLabel(status)}`}>
      {STEPS.map((step, i) => (
        <span
          key={step}
          className={
            i < idx ? "workflow-step done" : i === idx ? "workflow-step current" : "workflow-step"
          }
        />
      ))}
    </div>
  );
}