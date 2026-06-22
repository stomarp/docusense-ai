type ScoreCardProps = {
  label: string;
  value: string | number;
  helper: string;
};

export function ScoreCard({ label, value, helper }: ScoreCardProps) {
  return (
    <div className="score-card">
      <p className="card-label">{label}</p>
      <h3>{value}</h3>
      <p className="muted">{helper}</p>
    </div>
  );
}
