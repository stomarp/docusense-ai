type ProductPillarProps = {
  label: string;
  title: string;
  description: string;
};

export function ProductPillar({ label, title, description }: ProductPillarProps) {
  return (
    <div className="product-pillar">
      <p className="card-label">{label}</p>
      <h3>{title}</h3>
      <p className="muted">{description}</p>
    </div>
  );
}
