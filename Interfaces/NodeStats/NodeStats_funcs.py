import os
import platform
import subprocess
import time
import psutil


def get_cpu_usage(interval=1):
    """Returns the current CPU usage percentage."""
    # interval=1 averages usage over 1 second for higher accuracy
    # print(f"CPU_Usage:{psutil.cpu_percent(interval=interval)}")
    return psutil.cpu_percent(interval=interval)


def get_cpu_temperature():
    """Returns CPU temperature in Celsius, supporting Linux, Raspberry Pi, macOS, and Windows."""
    # Method 1: standard psutil sensor API (Linux, Raspberry Pi, macOS)
    if hasattr(psutil, "sensors_temperatures"):
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Look for common sensor keys across linux/raspberry pi distros
                for key in ["cpu_thermal", "coretemp", "cpu-thermal", "k10temp"]:
                    if key in temps and temps[key]:
                        return temps[key][0].current

                # Fallback: return the first available sensor value
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        except Exception:
            pass

    # Method 2: Raspberry Pi specific fallback using vcgencmd
    try:
        cmd_output = (
            subprocess.check_output(["vcgencmd", "measure_temp"])
            .decode("utf-8")
            .strip()
        )
        # Parses output like: "temp=45.2'C"
        return float(cmd_output.replace("temp=", "").replace("'C", ""))
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    # Method 3: Linux / Raspberry Pi Direct Thermal Zone File Fallback
    thermal_file = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(thermal_file):
        try:
            with open(thermal_file, "r") as f:
                # Value is reported in millidegrees Celsius
                return float(f.read().strip()) / 1000.0
        except Exception:
            pass

    # Method 4: Windows WMI Fallback
    if platform.system() == "Windows":
        try:
            import wmi

            w = wmi.WMI(namespace="root\\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:
                # Convert Kelvin (tenths of Kelvin) to Celsius
                return (temperature_info[0].CurrentTemperature / 10.0) - 273.15
        except Exception:
            pass

    return None

def get_ram_metrics():
    """Returns RAM usage stats: used GB, total GB, and percentage."""
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024**3)
    total_gb = mem.total / (1024**3)
    return {
        "used_gb": used_gb,
        "total_gb": total_gb,
        "percent": mem.percent,
    }


def get_disk_metrics(path="/"):
    """Returns disk usage stats for the specified root/drive path."""
    # On Windows, path defaults to main drive 'C:\\' if '/' resolves incorrectly
    if platform.system() == "Windows" and path == "/":
        path = "C:\\"

    disk = psutil.disk_usage(path)
    used_gb = disk.used / (1024**3)
    total_gb = disk.total / (1024**3)
    return {
        "used_gb": used_gb,
        "total_gb": total_gb,
        "percent": disk.percent,
    }


class NetworkTracker:
    """Calculates network download/upload speeds over time."""

    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()

    def get_speeds(self):
        current_time = time.time()
        current_net_io = psutil.net_io_counters()

        elapsed_time = current_time - self.last_time
        if elapsed_time <= 0:
            elapsed_time = 1.0

        # Calculate bytes per second transferred
        bytes_sent_sec = (
            current_net_io.bytes_sent - self.last_net_io.bytes_sent
        ) / elapsed_time
        bytes_recv_sec = (
            current_net_io.bytes_recv - self.last_net_io.bytes_recv
        ) / elapsed_time

        # Update baseline for next iteration
        self.last_net_io = current_net_io
        self.last_time = current_time

        # Convert to KB/s or MB/s for readability
        up_speed = (
            f"{bytes_sent_sec / (1024**2):.2f} MB/s"
            if bytes_sent_sec >= 1024**2
            else f"{bytes_sent_sec / 1024:.1f} KB/s"
        )
        down_speed = (
            f"{bytes_recv_sec / (1024**2):.2f} MB/s"
            if bytes_recv_sec >= 1024**2
            else f"{bytes_recv_sec / 1024:.1f} KB/s"
        )

        return {"upload": up_speed, "download": down_speed}


if __name__ == "__main__":
    net_tracker = NetworkTracker()

    print(f"OS: {platform.system()} ({platform.machine()})")
    print("=" * 60)

    try:
        while True:
            # 1. CPU Metrics
            cpu_usage = get_cpu_usage(interval=1)
            cpu_temp = get_cpu_temperature()
            temp_str = (
                f"{cpu_temp:.1f} °C"
                if cpu_temp is not None
                else "N/A (Not Supported)"
            )

            # 2. RAM Metrics
            ram = get_ram_metrics()

            # 3. Disk Metrics
            disk = get_disk_metrics()

            # 4. Network Metrics
            net = net_tracker.get_speeds()

            # Print System Summary
            print(f"CPU:  {cpu_usage}% | Temp: {temp_str}")
            print(
                f"RAM:  {ram['percent']}% ({ram['used_gb']:.2f} GB / {ram['total_gb']:.2f} GB)"
            )
            print(
                f"DISK: {disk['percent']}% ({disk['used_gb']:.2f} GB / {disk['total_gb']:.2f} GB)"
            )
            print(f"NET:  ▼ Down: {net['download']} | ▲ Up: {net['upload']}")
            print("-" * 60)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")