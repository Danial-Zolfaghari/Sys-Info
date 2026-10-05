import { ReactNode } from "react";

interface InfoCardProps {
  title: string;
  icon?: string;
  children: ReactNode;
  className?: string;
}

export function InfoCard({ title, icon, children, className = "" }: InfoCardProps) {
  return (
    <section className={`info-card ${className}`}>
      <header className="info-card-header">
        {icon && <span className="info-card-icon">{icon}</span>}
        <h3>{title}</h3>
      </header>
      <div className="info-card-body">{children}</div>
    </section>
  );
}

interface InfoRowProps {
  label: string;
  value: ReactNode;
}

export function InfoRow({ label, value }: InfoRowProps) {
  return (
    <div className="info-row">
      <span className="info-label">{label}</span>
      <span className="info-value">{value ?? "—"}</span>
    </div>
  );
}
