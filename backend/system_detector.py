import platform
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SystemDetector:
    """系统检测器"""
    
    @staticmethod
    def detect_system() -> Dict[str, str]:
        """检测当前系统信息"""
        return {
            'system': platform.system().lower(),
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version,
            'release': platform.release(),
            'version': platform.version()
        }
    
    @staticmethod
    def get_system_type() -> str:
        """获取系统类型"""
        system = platform.system().lower()
        if system == 'linux':
            # 进一步检测Linux发行版
            try:
                with open('/etc/os-release', 'r') as f:
                    content = f.read()
                    if 'ubuntu' in content.lower():
                        return 'ubuntu'
                    elif 'centos' in content.lower():
                        return 'centos'
                    elif 'debian' in content.lower():
                        return 'debian'
                    elif 'fedora' in content.lower():
                        return 'fedora'
                    else:
                        return 'linux'
            except:
                return 'linux'
        elif system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        else:
            return 'unknown'