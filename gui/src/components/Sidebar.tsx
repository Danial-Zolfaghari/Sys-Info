import { TabId } from "../types";

interface SidebarProps {
  active: TabId;
  onChange: (tab: TabId) => void;
}

const tabs: { id: TabId; label: string; code: string }[] = [
  { id: "overview", label: "Overview", code: "01" },
  { id: "cpu", label: "Processor", code: "02" },
  { id: "memory", label: "Memory", code: "03" },
  { id: "motherboard", label: "Board", code: "04" },
  { id: "gpu", label: "Graphics", code: "05" },
  { id: "storage", label: "Storage", code: "06" },
  { id: "network", label: "Network", code: "07" },
  { id: "battery", label: "Power", code: "08" },
  { id: "system", label: "System", code: "09" },
];

export function Sidebar({ active, onChange }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          <span className="brand-chip" />
          <span className="brand-glow" />
        </div>
        <div className="brand-text">
          <strong>SysInfo</strong>
          <span>Hardware Instrument</span>
        </div>
      </div>

      <div className="sidebar-label">SECTIONS</div>
      <nav className="sidebar-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-item ${active === tab.id ? "active" : ""}`}
            onClick={() => onChange(tab.id)}
          >
            <span className="nav-code">{tab.code}</span>
            <span className="nav-label">{tab.label}</span>
            <span className="nav-arrow">→</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="footer-line" />
        <span>LOCAL DIAGNOSTICS</span>
      </div>
    </aside>
  );
}
