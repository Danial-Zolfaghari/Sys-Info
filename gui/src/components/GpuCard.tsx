import { GpuInfo } from "../types";

interface GpuCardProps {
  gpu: GpuInfo;
  index: number;
}

export function GpuCard({ gpu, index }: GpuCardProps) {
  if (gpu.status) {
    return (
      <article className="gpu-card empty">
        <p>{gpu.status}</p>
      </article>
    );
  }

  const isDiscrete = gpu.type === "discrete";

  return (
    <article className={`gpu-card ${isDiscrete ? "discrete" : "integrated"}`}>
      <div className="gpu-card-header">
        <span className="gpu-index">GPU {index + 1}</span>
        <span className="gpu-type-badge">{isDiscrete ? "Discrete" : "Integrated"}</span>
      </div>
      <h4>{gpu.name}</h4>
      <div className="gpu-specs">
        <div>
          <span className="spec-label">VRAM</span>
          <span className="spec-value">{gpu.vram}</span>
        </div>
        <div>
          <span className="spec-label">Driver</span>
          <span className="spec-value mono">{gpu.driver}</span>
        </div>
        <div className="gpu-processor">
          <span className="spec-label">Processor</span>
          <span className="spec-value mono">{gpu.processor}</span>
        </div>
      </div>
    </article>
  );
}
