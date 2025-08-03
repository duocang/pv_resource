import time
import threading
from collections import deque
from datetime import datetime
from typing import Dict, Any, Optional
from monitor_factory import MonitorFactory
from system_detector import SystemDetector

class SystemMonitor:
    def __init__(self, max_history=100):
        self.max_history = max_history
        self.history_data = deque(maxlen=max_history)
        self.current_data = {}
        self.monitoring = False
        self.lock = threading.Lock()
        
        # 检测系统并创建相应的监控器
        self.system_info = SystemDetector.detect_system()
        self.monitor = MonitorFactory.create_monitor()
        
        print(f"检测到系统: {self.system_info['system']} - {self.system_info['platform']}")
        print(f"使用监控器: {self.monitor.__class__.__name__}")
    
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """获取当前系统信息"""
        try:
            data = self.monitor.get_all_info()
            if data:  # 确保数据不为空
                data['system_detection'] = self.system_info
                data['timestamp'] = datetime.now().isoformat()
                return data
            else:
                print("监控器返回空数据")
                return None
        except Exception as e:
            print(f"获取系统信息时出错: {e}")
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            return None
    
    def start_monitoring(self):
        """开始监控系统"""
        self.monitoring = True
        print(f"开始监控系统 ({self.system_info['system']})...")
        
        while self.monitoring:
            try:
                data = self.get_system_info()
                if data:
                    with self.lock:
                        self.current_data = data
                        self.history_data.append(data)
                time.sleep(5)  # 每5秒采集一次数据
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(5)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        print("停止系统监控")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        with self.lock:
            return self.current_data.copy() if self.current_data else {}
    
    def get_history_data(self, limit=50) -> list:
        """获取历史数据"""
        with self.lock:
            return list(self.history_data)[-limit:]
    
    def get_system_detection_info(self) -> Dict[str, Any]:
        """获取系统检测信息"""
        return {
            'detected_system': self.system_info,
            'monitor_class': self.monitor.__class__.__name__,
            'supported_systems': MonitorFactory.get_supported_systems()
        }