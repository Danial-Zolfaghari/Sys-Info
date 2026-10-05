interface DiskBarProps {
  device: string;
  model: string;
  type: string;
  usedPercent: number;
  usedGb: number;
  totalGb: number;
  freeGb: number;
  fileSystem: string;
}

const typeLabels: Record<string, string> = {
  nvme: "NVMe SSD",
  hdd: "HDD / SATA",
  usb: "USB / Removable",
};

function usageClass(percent: number): string {
  if (percent >= 90) return "critical";
  if (percent >= 75) return "warning";
  return "healthy";
}

export function DiskBar({
  device,
  model,
  type,
  usedPercent,
  usedGb,
  totalGb,
  freeGb,
  fileSystem,
}: DiskBarProps) {
  const cls = usageClass(usedPercent);

  return (
    <article className="disk-card">
      <div className="disk-card-top">
        <div>
          <h4>{device}</h4>
          <p className="disk-meta">
            {model} · {typeLabels[type] || type} · {fileSystem}
          </p>
        </div>
        <span className={`disk-badge ${cls}`}>{usedPercent}% used</span>
      </div>
      <div className="disk-bar-track">
        <div
          className={`disk-bar-fill ${cls}`}
          style={{ width: `${Math.min(usedPercent, 100)}%` }}
        />
      </div>
      <div className="disk-stats">
        <span>{usedGb} GB used</span>
        <span>{freeGb} GB free</span>
        <span>{totalGb} GB total</span>
      </div>
    </article>
  );
}
