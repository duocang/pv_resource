from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSystemMonitor(ABC):
    """系统监控器基类"""
    
    @abstractmethod
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        pass
    
    @abstractmethod
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        pass
    
    @abstractmethod
    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        pass
    
    @abstractmethod
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        pass
    
    @abstractmethod
    def get_process_info(self) -> Dict[str, Any]:
        """获取进程信息"""
        pass
    
    @abstractmethod
    def get_system_load(self) -> Dict[str, Any]:
        """获取系统负载"""
        pass
    
    def get_all_info(self) -> Dict[str, Any]:
        """获取所有系统信息，子类可以重写此方法来自定义数据格式"""
        return {
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'processes': self.get_process_info(),
            'load': self.get_system_load()
        }