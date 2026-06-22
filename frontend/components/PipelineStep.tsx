type PipelineStepProps = {
  step: string;
  title: string;
  detail: string;
};

export function PipelineStep({ step, title, detail }: PipelineStepProps) {
  return (
    <div className="pipeline-step">
      <div className="step-number">{step}</div>
      <div>
        <h3>{title}</h3>
        <p className="muted">{detail}</p>
      </div>
    </div>
  );
}
