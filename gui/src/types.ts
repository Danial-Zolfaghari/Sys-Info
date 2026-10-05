export interface OsInfo {
  operating_system: string;
  system_name: string;
  kernel_release: string;
  architecture: string;
  windows_edition?: string;
}

export interface CpuInfo {
  physical_cores?: number;
  logical_cores?: number;
  current_frequency_mhz?: number;
  model?: string;
  manufacturer?: string;
  max_frequency_mhz?: number | string;
}

export interface MemoryModule {
  slot: number;
  location: string;
  capacity_gb: number | null;
  type: string;
  speed: string;
  manufacturer: string;
  part_number: string;
}

export interface MemoryInfo {
  total_ram_gb: number;
  modules: MemoryModule[];
  note?: string;
}

export interface MotherboardInfo {
  manufacturer?: string;
  model?: string;
  version?: string;
  serial_number?: string;
  bios_manufacturer?: string;
  bios_version?: string;
  bios_serial?: string;
  bios_release_date?: string;
  status?: string;
}

export interface GpuInfo {
  name?: string;
  vram?: string;
  type?: string;
  driver?: string;
  processor?: string;
  status?: string;
}

export interface DiskInfo {
  device: string;
  model: string;
  type: string;
  file_system: string;
  total_gb: number;
  used_gb: number;
  free_gb: number;
  used_percent: number;
}

export interface NetworkInfo {
  interface: string;
  ipv4: string | null;
  ipv6: string | null;
  mac: string | null;
}

export interface BatteryInfo {
  present: boolean;
  percent?: number;
  plugged?: boolean;
  charging?: boolean;
  time_remaining?: string;
  status?: string;
  note?: string;
}

export interface SystemInfo {
  boot_time: string;
  uptime_days: number;
  uptime_hours: number;
  uptime_minutes: number;
  current_time: string;
  timezone: string;
}

export interface SystemData {
  os: OsInfo;
  cpu: CpuInfo;
  memory: MemoryInfo;
  motherboard: MotherboardInfo;
  gpu: GpuInfo[];
  disk: DiskInfo[];
  network: NetworkInfo[];
  battery: BatteryInfo;
  system: SystemInfo;
}

export type TabId =
  | "overview"
  | "cpu"
  | "memory"
  | "motherboard"
  | "gpu"
  | "storage"
  | "network"
  | "battery"
  | "system";

export interface ExportResult {
  summary?: string;
  full?: string;
}
