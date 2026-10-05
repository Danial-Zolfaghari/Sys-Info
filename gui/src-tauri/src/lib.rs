use serde::Serialize;
use serde_json::Value;
use std::{fs, path::{Path, PathBuf}, process::Command};
use tauri::Manager;

#[derive(Serialize)]
struct AppInfo { version: String }

#[derive(Serialize)]
struct ExportResult { summary: String, full: String }

fn collector_candidates(app: &tauri::AppHandle) -> Vec<PathBuf> {
    let mut paths = Vec::new();
    if let Ok(resource_dir) = app.path().resource_dir() {
        paths.push(resource_dir.join("resources").join("sys-info-collector.exe"));
        paths.push(resource_dir.join("sys-info-collector.exe"));
    }
    paths.push(PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("resources").join("sys-info-collector.exe"));
    paths
}

#[tauri::command]
fn get_system_info(app: tauri::AppHandle) -> Result<Value, String> {
    let collector = collector_candidates(&app).into_iter().find(|p| p.exists())
        .ok_or_else(|| "Bundled system collector was not found. Rebuild the application.".to_string())?;
    let output = Command::new(&collector).output().map_err(|e| format!("Unable to start collector: {e}"))?;
    if !output.status.success() {
        return Err(format!("Collector failed: {}", String::from_utf8_lossy(&output.stderr)));
    }
    serde_json::from_slice(&output.stdout).map_err(|e| format!("Invalid collector JSON: {e}"))
}

#[tauri::command]
fn get_app_info() -> AppInfo { AppInfo { version: env!("CARGO_PKG_VERSION").to_string() } }

#[tauri::command]
fn pick_export_folder() -> Option<String> {
    rfd::FileDialog::new().pick_folder().map(|p| p.to_string_lossy().to_string())
}

#[tauri::command]
fn export_reports(data: Value, directory: String) -> Result<ExportResult, String> {
    let dir = Path::new(&directory);
    fs::create_dir_all(dir).map_err(|e| e.to_string())?;
    let full = dir.join("sysinfo-report.json");
    let summary = dir.join("sysinfo-summary.txt");
    let pretty = serde_json::to_string_pretty(&data).map_err(|e| e.to_string())?;
    fs::write(&full, &pretty).map_err(|e| e.to_string())?;
    let os = data.get("os").and_then(|v| v.get("windows_edition").or_else(|| v.get("operating_system"))).and_then(Value::as_str).unwrap_or("Unknown");
    let host = data.get("os").and_then(|v| v.get("system_name")).and_then(Value::as_str).unwrap_or("Unknown");
    let text = format!("SysInfo Summary\n================\nHost: {host}\nOS: {os}\n\nFull report: {}\n", full.display());
    fs::write(&summary, text).map_err(|e| e.to_string())?;
    Ok(ExportResult { summary: summary.to_string_lossy().to_string(), full: full.to_string_lossy().to_string() })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_system_info, get_app_info, pick_export_folder, export_reports])
        .run(tauri::generate_context!())
        .expect("error while running SysInfo");
}
