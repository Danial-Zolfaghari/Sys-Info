import platform
import socket
import subprocess
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import psutil


def run_command(cmd, timeout=15):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def run_powershell(cmd):
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def get_os_info():
    info = {
        "operating_system": platform.system(),
        "system_name": platform.node(),
        "kernel_release": platform.release(),
        "architecture": platform.machine(),
    }
    if platform.system() == "Windows":
        result = run_powershell("(Get-CimInstance Win32_OperatingSystem).Caption")
        info["windows_edition"] = result or "N/A"
    return info


def get_cpu_info():
    info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
    }
    freq = psutil.cpu_freq()
    if freq:
        info["current_frequency_mhz"] = round(freq.current)

    if platform.system() == "Windows":
        ps_cmd = (
            "Get-CimInstance -ClassName Win32_Processor | "
            "Select-Object Name,Manufacturer,MaxClockSpeed | ConvertTo-Json"
        )
        result = run_powershell(ps_cmd)
        if result:
            try:
                data = json.loads(result)
                if isinstance(data, list):
                    data = data[0]
                info["model"] = data.get("Name", "N/A")
                info["manufacturer"] = data.get("Manufacturer", "N/A")
                info["max_frequency_mhz"] = data.get("MaxClockSpeed", "N/A")
            except Exception:
                pass
    return info


def get_memory_info():
    info = {}
    mem = psutil.virtual_memory()
    info["total_ram_gb"] = round(mem.total / (1024**3), 2)
    info["modules"] = []

    if platform.system() == "Windows":
        ps_cmd = """
        Get-CimInstance -ClassName Win32_PhysicalMemory |
        Select-Object Capacity,Speed,Manufacturer,MemoryType,PartNumber,SMBIOSMemoryType,
        ConfiguredClockSpeed,MemoryTechnology,BankLabel,DeviceLocator,MaxMemorySpeed | ConvertTo-Json
        """
        result = run_powershell(ps_cmd)
        if result:
            try:
                data = json.loads(result)
                if not isinstance(data, list):
                    data = [data]

                type_map = {
                    0: "Unknown",
                    1: "Other",
                    2: "DRAM",
                    20: "DDR",
                    21: "DDR2",
                    22: "DDR2 FB-DIMM",
                    24: "DDR3",
                    26: "DDR4",
                    34: "DDR5",
                }

                for i, mod in enumerate(data, 1):
                    capacity = mod.get("Capacity", 0)
                    capacity_gb = round(capacity / (1024**3), 2) if capacity else None

                    speed = mod.get("Speed", 0)
                    configured_speed = mod.get("ConfiguredClockSpeed", 0)
                    max_speed = mod.get("MaxMemorySpeed", 0)

                    manufacturer = mod.get("Manufacturer", "Unknown") or "Unknown"
                    if not manufacturer.strip():
                        manufacturer = "Unknown"

                    smbios_type = mod.get("SMBIOSMemoryType", 0)
                    mem_type = mod.get("MemoryType", 0)

                    if smbios_type and smbios_type > 0:
                        mem_type_str = type_map.get(smbios_type, f"DDR{smbios_type}")
                    elif mem_type and mem_type > 0:
                        mem_type_str = type_map.get(mem_type, str(mem_type))
                    else:
                        mem_type_str = mod.get("MemoryTechnology") or "Unknown"

                    part_number = mod.get("PartNumber", "Unknown") or "Unknown"
                    if not part_number.strip():
                        part_number = "Unknown"

                    bank_label = mod.get("BankLabel", "")
                    device_locator = mod.get("DeviceLocator", "")
                    location = bank_label or device_locator or f"Slot {i}"

                    speed_info = "N/A"
                    if speed and speed > 0:
                        if configured_speed and configured_speed > 0 and configured_speed != speed:
                            speed_info = f"{speed} MHz (Running) / {configured_speed} MHz (XMP)"
                        elif max_speed and max_speed > 0 and max_speed != speed:
                            speed_info = f"{speed} MHz (Running) / {max_speed} MHz (Max)"
                        else:
                            speed_info = f"{speed} MHz"

                    info["modules"].append(
                        {
                            "slot": i,
                            "location": location,
                            "capacity_gb": capacity_gb,
                            "type": mem_type_str,
                            "speed": speed_info,
                            "manufacturer": manufacturer,
                            "part_number": part_number.strip(),
                        }
                    )

                info["note"] = (
                    "Speed shown is current running speed. Check BIOS for XMP/EXPO profile."
                )
            except Exception:
                pass

    return info


def get_motherboard_info():
    info = {}
    if platform.system() == "Windows":
        ps_cmd = (
            "Get-CimInstance -ClassName Win32_BaseBoard | "
            "Select-Object Manufacturer,Product,Version,SerialNumber | ConvertTo-Json"
        )
        result = run_powershell(ps_cmd)
        if result:
            try:
                data = json.loads(result)
                if isinstance(data, list):
                    data = data[0]
                info["manufacturer"] = data.get("Manufacturer", "N/A")
                info["model"] = data.get("Product", "N/A")
                info["version"] = data.get("Version", "N/A")
                info["serial_number"] = data.get("SerialNumber", "N/A")
            except Exception:
                pass

        bios_cmd = (
            "Get-CimInstance -ClassName Win32_BIOS | "
            "Select-Object Manufacturer,Version,SerialNumber,ReleaseDate | ConvertTo-Json"
        )
        bios_result = run_powershell(bios_cmd)
        if bios_result:
            try:
                data = json.loads(bios_result)
                if isinstance(data, list):
                    data = data[0]
                info["bios_manufacturer"] = data.get("Manufacturer", "N/A")
                info["bios_version"] = data.get("Version", "N/A")
                info["bios_serial"] = data.get("SerialNumber", "N/A")
                release_date = data.get("ReleaseDate", "N/A")
                if release_date and release_date.startswith("/Date"):
                    match = re.search(r"\((\d+)\)", release_date)
                    if match:
                        timestamp = int(match.group(1)) / 1000
                        release_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                info["bios_release_date"] = release_date
            except Exception:
                pass

    if not info:
        info["status"] = "Run as administrator for full details"
    return info


def get_amd_vram():
    reg_cmd = (
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\'
        '{4d36e968-e325-11ce-bfc1-08002be10318}\\0000" /v HardwareInformation.qwMemorySize'
    )
    result = run_command(reg_cmd)
    if result:
        match = re.search(r"0x([0-9a-fA-F]+)", result)
        if match:
            try:
                vram_bytes = int(match.group(1), 16)
                if vram_bytes > 0:
                    vram_gb = round(vram_bytes / (1024**3))
                    if vram_gb >= 1:
                        return vram_gb
            except Exception:
                pass
    return None


def get_nvidia_vram():
    nvidia_smi = run_command(
        "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"
    )
    if nvidia_smi:
        for line in nvidia_smi.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                return parts[0], parts[1]
    return None, None


def get_gpu_info():
    gpus = []
    nvidia_name, nvidia_vram = get_nvidia_vram()
    amd_vram = get_amd_vram()

    if platform.system() == "Windows":
        ps_cmd = """
        Get-CimInstance -ClassName Win32_VideoController |
        Select-Object Name,AdapterRAM,DriverVersion,VideoProcessor,Status | ConvertTo-Json
        """
        result = run_powershell(ps_cmd)
        if result:
            try:
                data = json.loads(result)
                if not isinstance(data, list):
                    data = [data]

                for gpu in data:
                    name = gpu.get("Name", "")
                    if not name or not name.strip():
                        continue

                    vram = gpu.get("AdapterRAM", 0)
                    vram_str = f"{round(vram / (1024**3))} GB" if vram and vram > 0 else "N/A"

                    is_amd = "AMD" in name or "Radeon" in name
                    is_nvidia = "NVIDIA" in name or "GeForce" in name
                    is_intel = (
                        "Intel" in name
                        or "UHD" in name
                        or "Iris" in name
                        or "Xe" in name
                    )
                    is_microsoft = (
                        "Microsoft" in name
                        or "Basic" in name
                        or "Standard" in name
                        or "Display" in name
                    )

                    if is_amd and amd_vram and amd_vram > 0:
                        vram_str = f"{amd_vram} GB"
                    if is_nvidia and nvidia_vram:
                        vram_str = nvidia_vram
                        if nvidia_name:
                            name = nvidia_name

                    gpu_type = "discrete"
                    if is_intel or is_microsoft:
                        gpu_type = "integrated"

                    gpus.append(
                        {
                            "name": name,
                            "vram": vram_str,
                            "type": gpu_type,
                            "driver": gpu.get("DriverVersion", "N/A"),
                            "processor": gpu.get("VideoProcessor", "N/A"),
                        }
                    )
            except Exception:
                pass

    if not gpus:
        gpus.append({"status": "No GPU detected"})
    return gpus


def get_storage_info():
    storage_by_letter = {}
    ps_cmd = """Get-Disk | ForEach-Object {
    $disk = $_
    Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue | ForEach-Object {
        [PSCustomObject]@{
            DriveLetter = $_.DriveLetter
            FriendlyName = $disk.FriendlyName
            BusType = $disk.BusType
        }
    }
} | Where-Object { $_.DriveLetter } | ConvertTo-Json"""

    result = run_powershell(ps_cmd)
    if result:
        try:
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]

            for disk in data:
                drive_letter = disk.get("DriveLetter", "")
                friendly_name = disk.get("FriendlyName", "Unknown")
                bus_type = disk.get("BusType", "SATA")

                if drive_letter:
                    key = f"{drive_letter}:"
                    bus_upper = bus_type.upper() if bus_type else ""
                    if "NVME" in bus_upper:
                        storage_type = "nvme"
                    elif "USB" in bus_upper:
                        storage_type = "usb"
                    else:
                        storage_type = "hdd"

                    storage_by_letter[key] = {
                        "type": storage_type,
                        "model": friendly_name,
                    }
        except Exception:
            pass

    return storage_by_letter


def get_disk_info():
    disks = []
    storage_by_letter = get_storage_info()

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            drive_letter = partition.device.split(":")[0] + ":"

            storage_type = "hdd"
            model = "Unknown"
            if drive_letter in storage_by_letter:
                info = storage_by_letter[drive_letter]
                model = info.get("model", "Unknown")
                storage_type = info.get("type", "hdd")

            if "USB" in partition.device or "Removable" in partition.fstype:
                storage_type = "usb"

            used_percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0

            disks.append(
                {
                    "device": partition.device,
                    "model": model,
                    "type": storage_type,
                    "file_system": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "used_percent": round(used_percent, 1),
                }
            )
        except Exception:
            pass

    return disks


def get_network_info():
    interfaces = []
    addrs = psutil.net_if_addrs()
    for interface, addresses in addrs.items():
        ipv4 = ""
        ipv6 = ""
        mac = ""
        for addr in addresses:
            if addr.family == socket.AF_INET:
                ipv4 = addr.address
            elif addr.family == socket.AF_INET6:
                ipv6 = addr.address
            elif addr.family == psutil.AF_LINK:
                mac = addr.address

        if ipv4 or ipv6 or mac:
            interfaces.append(
                {
                    "interface": interface,
                    "ipv4": ipv4 or None,
                    "ipv6": ipv6 or None,
                    "mac": mac or None,
                }
            )
    return interfaces


def get_battery_info():
    battery = psutil.sensors_battery()
    if not battery:
        return {
            "present": False,
            "status": "No battery detected",
            "note": "Desktop PC or battery not present",
        }

    info = {
        "present": True,
        "percent": battery.percent,
        "plugged": battery.power_plugged,
        "charging": battery.power_plugged,
    }

    if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
        info["time_remaining"] = "Unlimited (Plugged In)"
    elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
        info["time_remaining"] = "Unknown"
    else:
        hours = battery.secsleft // 3600
        minutes = (battery.secsleft % 3600) // 60
        info["time_remaining"] = f"{hours}h {minutes}m"

    return info


def get_system_info():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    now = datetime.now()
    return {
        "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_days": uptime.days,
        "uptime_hours": uptime.seconds // 3600,
        "uptime_minutes": (uptime.seconds % 3600) // 60,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": str(now.astimezone().tzinfo),
    }


def collect_all():
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            "os": executor.submit(get_os_info),
            "cpu": executor.submit(get_cpu_info),
            "memory": executor.submit(get_memory_info),
            "motherboard": executor.submit(get_motherboard_info),
            "gpu": executor.submit(get_gpu_info),
            "disk": executor.submit(get_disk_info),
            "network": executor.submit(get_network_info),
            "battery": executor.submit(get_battery_info),
            "system": executor.submit(get_system_info),
        }
        return {key: future.result() for key, future in futures.items()}


def collect_all_json():
    return json.dumps(collect_all(), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print(collect_all_json())
