from typing import Optional
from system_detector import SystemDetector
from monitors.base_monitor import BaseSystemMonitor
from monitors.linux_monitor import LinuxSystemMonitor
from monitors.macos_monitor import MacOSSystemMonitor
from monitors.windows_monitor import WindowsSystemMonitor

class MonitorFactory:
    """监控器工厂类"""
    
    _monitors = {
        'linux': LinuxSystemMonitor,
        'ubuntu': LinuxSystemMonitor,
        'centos': LinuxSystemMonitor,
        'debian': LinuxSystemMonitor,
        'fedora': LinuxSystemMonitor,
        'macos': MacOSSystemMonitor,
        'windows': WindowsSystemMonitor
    }
    
    @classmethod
    def create_monitor(cls, system_type: Optional[str] = None) -> BaseSystemMonitor:
        """创建系统监控器"""
        if system_type is None:
            system_type = SystemDetector.get_system_type()
        
        monitor_class = cls._monitors.get(system_type)
        if monitor_class is None:
            # 默认使用Linux监控器
            monitor_class = LinuxSystemMonitor
        
        return monitor_class()
    
    @classmethod
    def get_supported_systems(cls) -> list:
        """获取支持的系统列表"""
        return list(cls._monitors.keys())