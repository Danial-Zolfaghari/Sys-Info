import { useCallback, useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Sidebar } from "./components/Sidebar";
import { InfoCard, InfoRow } from "./components/InfoCard";
import { DiskBar } from "./components/DiskBar";
import { GpuCard } from "./components/GpuCard";
import { ExportResult, SystemData, TabId } from "./types";
import "./App.css";

function LoadingView() {
  return (
    <div className="loading-view">
      <div className="scanner" />
      <h2>Scanning Hardware</h2>
      <p>Reading CPU, memory, GPU, storage and system telemetry...</p>
    </div>
  );
}

function ErrorView({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="error-view">
      <div className="error-icon">!</div>
      <h2>Unable to load system info</h2>
      <p>{message}</p>
      <button className="btn primary" onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}

function App() {
  const [data, setData] = useState<SystemData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>("overview");
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [version, setVersion] = useState("1.0.0");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<SystemData>("get_system_info");
      setData(result);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    invoke<{ version: string }>("get_app_info")
      .then((info) => setVersion(info.version))
      .catch(() => {});
  }, [load]);

  const handleExport = async () => {
    if (!data) return;

    setExporting(true);
    setExportMsg(null);
    try {
      const directory = await invoke<string | null>("pick_export_folder");
      if (!directory) {
        return;
      }

      const result = await invoke<ExportResult>("export_reports", {
        data,
        directory,
      });
      setExportMsg(`Reports saved to: ${directory}`);
      void result;
    } catch (e) {
      setExportMsg(`Export failed: ${e}`);
    } finally {
      setExporting(false);
    }
  };

  const renderContent = () => {
    if (loading) return <LoadingView />;
    if (error) return <ErrorView message={error} onRetry={load} />;
    if (!data) return null;

    switch (tab) {
      case "overview":
        return (
          <div className="content-grid">
            <InfoCard title="System" icon="🖥">
              <InfoRow label="OS" value={data.os.windows_edition || data.os.operating_system} />
              <InfoRow label="Hostname" value={data.os.system_name} />
              <InfoRow label="Architecture" value={data.os.architecture} />
            </InfoCard>
            <InfoCard title="Processor" icon="⚡">
              <InfoRow label="Model" value={data.cpu.model} />
              <InfoRow
                label="Cores"
                value={`${data.cpu.physical_cores} physical / ${data.cpu.logical_cores} logical`}
              />
              <InfoRow label="Frequency" value={`${data.cpu.current_frequency_mhz ?? "—"} MHz`} />
            </InfoCard>
            <InfoCard title="Memory" icon="▣">
              <InfoRow label="Total RAM" value={`${data.memory.total_ram_gb} GB`} />
              <InfoRow label="Modules" value={data.memory.modules.length} />
            </InfoCard>
            <InfoCard title="Graphics" icon="◆">
              {data.gpu.map((g, i) => (
                <InfoRow key={i} label={g.name || g.status || "GPU"} value={g.vram || "—"} />
              ))}
            </InfoCard>
            <div className="span-2">
              <InfoCard title="Storage Overview" icon="▥">
                <div className="disk-list">
                  {data.disk.map((d) => (
                    <DiskBar
                      key={d.device}
                      device={d.device}
                      model={d.model}
                      type={d.type}
                      usedPercent={d.used_percent}
                      usedGb={d.used_gb}
                      totalGb={d.total_gb}
                      freeGb={d.free_gb}
                      fileSystem={d.file_system}
                    />
                  ))}
                </div>
              </InfoCard>
            </div>
          </div>
        );

      case "cpu":
        return (
          <InfoCard title="Processor Details" icon="⚡" className="full-width">
            <InfoRow label="Model" value={data.cpu.model} />
            <InfoRow label="Manufacturer" value={data.cpu.manufacturer} />
            <InfoRow label="Physical Cores" value={data.cpu.physical_cores} />
            <InfoRow label="Logical Cores" value={data.cpu.logical_cores} />
            <InfoRow label="Current Frequency" value={`${data.cpu.current_frequency_mhz ?? "—"} MHz`} />
            <InfoRow label="Max Frequency" value={`${data.cpu.max_frequency_mhz ?? "—"} MHz`} />
          </InfoCard>
        );

      case "memory":
        return (
          <div className="content-stack">
            <InfoCard title="RAM Summary" icon="▣">
              <InfoRow label="Total Installed" value={`${data.memory.total_ram_gb} GB`} />
              {data.memory.note && <p className="note">{data.memory.note}</p>}
            </InfoCard>
            {data.memory.modules.map((mod) => (
              <InfoCard key={mod.slot} title={`Module ${mod.slot} — ${mod.location}`} icon="▣">
                <InfoRow label="Capacity" value={`${mod.capacity_gb} GB`} />
                <InfoRow label="Type" value={mod.type} />
                <InfoRow label="Speed" value={mod.speed} />
                <InfoRow label="Manufacturer" value={mod.manufacturer} />
                <InfoRow label="Part Number" value={mod.part_number} />
              </InfoCard>
            ))}
          </div>
        );

      case "motherboard":
        return (
          <InfoCard title="Motherboard & BIOS" icon="▤" className="full-width">
            <InfoRow label="Manufacturer" value={data.motherboard.manufacturer} />
            <InfoRow label="Model" value={data.motherboard.model} />
            <InfoRow label="Version" value={data.motherboard.version} />
            <InfoRow label="Serial Number" value={data.motherboard.serial_number} />
            <hr className="divider" />
            <InfoRow label="BIOS Manufacturer" value={data.motherboard.bios_manufacturer} />
            <InfoRow label="BIOS Version" value={data.motherboard.bios_version} />
            <InfoRow label="BIOS Serial" value={data.motherboard.bios_serial} />
            <InfoRow label="BIOS Release Date" value={data.motherboard.bios_release_date} />
          </InfoCard>
        );

      case "gpu":
        return (
          <div className="gpu-grid">
            {data.gpu.map((gpu, i) => (
              <GpuCard key={i} gpu={gpu} index={i} />
            ))}
          </div>
        );

      case "storage":
        return (
          <div className="disk-list full">
            {data.disk.map((d) => (
              <DiskBar
                key={d.device}
                device={d.device}
                model={d.model}
                type={d.type}
                usedPercent={d.used_percent}
                usedGb={d.used_gb}
                totalGb={d.total_gb}
                freeGb={d.free_gb}
                fileSystem={d.file_system}
              />
            ))}
          </div>
        );

      case "network":
        return (
          <div className="content-stack">
            {data.network.map((iface) => (
              <InfoCard key={iface.interface} title={iface.interface} icon="◎">
                <InfoRow label="IPv4" value={iface.ipv4} />
                <InfoRow label="IPv6" value={iface.ipv6} />
                <InfoRow label="MAC Address" value={iface.mac} />
              </InfoCard>
            ))}
          </div>
        );

      case "battery":
        return (
          <InfoCard title="Battery Status" icon="◉" className="full-width">
            {!data.battery.present ? (
              <>
                <InfoRow label="Status" value={data.battery.status} />
                <InfoRow label="Note" value={data.battery.note} />
              </>
            ) : (
              <>
                <div className="battery-visual">
                  <div className="battery-shell">
                    <div
                      className="battery-level"
                      style={{ width: `${data.battery.percent ?? 0}%` }}
                    />
                  </div>
                  <span className="battery-percent">{data.battery.percent}%</span>
                </div>
                <InfoRow label="Power Source" value={data.battery.plugged ? "Plugged in" : "On battery"} />
                <InfoRow label="Status" value={data.battery.charging ? "Charging" : "Discharging"} />
                <InfoRow label="Time Remaining" value={data.battery.time_remaining} />
              </>
            )}
          </InfoCard>
        );

      case "system":
        return (
          <InfoCard title="System Time & Uptime" icon="◷" className="full-width">
            <InfoRow label="Current Time" value={data.system.current_time} />
            <InfoRow label="Timezone" value={data.system.timezone} />
            <InfoRow label="Boot Time" value={data.system.boot_time} />
            <InfoRow
              label="Uptime"
              value={`${data.system.uptime_days}d ${data.system.uptime_hours}h ${data.system.uptime_minutes}m`}
            />
          </InfoCard>
        );

      default:
        return null;
    }
  };

  return (
    <div className="app-shell">
      <Sidebar active={tab} onChange={setTab} />
      <main className="main-panel">
        <header className="topbar">
          <div>
            <h1>{tab.charAt(0).toUpperCase() + tab.slice(1)}</h1>
            <p className="subtitle">Hardware telemetry · local diagnostics</p>
          </div>
          <div className="topbar-actions">
            <button className="btn ghost" onClick={load} disabled={loading}>
              Refresh
            </button>
            <button className="btn primary" onClick={handleExport} disabled={exporting || loading || !data}>
              {exporting ? "Exporting..." : "Export Reports"}
            </button>
          </div>
        </header>

        {exportMsg && (
          <div className="toast" onClick={() => setExportMsg(null)}>
            {exportMsg}
          </div>
        )}

        {data && !loading && !error && (
          <div className="telemetry-strip">
            <div className="telemetry-item">
              <div className="label">Host</div>
              <div className="value">{data.os.system_name}</div>
            </div>
            <div className="telemetry-item">
              <div className="label">Processor</div>
              <div className="value mono">{data.cpu.model ?? "—"}</div>
            </div>
            <div className="telemetry-item">
              <div className="label">Memory</div>
              <div className="value mono">{data.memory.total_ram_gb} GB</div>
            </div>
            <div className="telemetry-item">
              <div className="label">Platform</div>
              <div className="value">{data.os.windows_edition || data.os.operating_system}</div>
            </div>
          </div>
        )}

        <div className="content-area">{renderContent()}</div>

        <footer className="statusbar">
          <span>SysInfo v{version}</span>
          <span>
            {loading ? "Scanning hardware…" : `${data?.os.system_name ?? "—"} · ${data?.os.architecture ?? ""}`}
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;
