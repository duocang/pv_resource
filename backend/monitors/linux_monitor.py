import psutil
import subprocess
import os
from typing import Dict, Any
from .base_monitor import BaseSystemMonitor

class LinuxSystemMonitor(BaseSystemMonitor):
    """Linux系统监控器"""
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        cpu_info = {
            'percent': psutil.cpu_percent(interval=1),
            'count_logical': psutil.cpu_count(logical=True),
            'count_physical': psutil.cpu_count(logical=False),
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
        }
        
        # 获取CPU频率
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info['frequency'] = {
                    'current': cpu_freq.current,
                    'min': cpu_freq.min,
                    'max': cpu_freq.max
                }
        except:
            pass
        
        # 获取CPU温度（Linux特有）
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                cpu_info['temperature'] = temps
        except:
            pass
        
        return cpu_info
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'virtual': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'active': getattr(memory, 'active', 0),
                'inactive': getattr(memory, 'inactive', 0),
                'buffers': getattr(memory, 'buffers', 0),
                'cached': getattr(memory, 'cached', 0)
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        disk_info = {'partitions': [], 'io': {}}
        
        # 获取分区信息
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info['partitions'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                })
            except PermissionError:
                continue
        
        # 获取磁盘IO信息
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_info['io'] = {
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count
                }
        except:
            pass
        
        return disk_info
    
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        network_info = {'interfaces': {}, 'io': {}}
        
        # 获取网络接口信息
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                network_info['interfaces'][interface] = []
                for addr in addrs:
                    network_info['interfaces'][interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
        except:
            pass
        
        # 获取网络IO信息
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                network_info['io'] = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
        except:
            pass
        
        return network_info
    
    def get_process_info(self) -> Dict[str, Any]:
        """获取进程信息"""
        processes = []
        try:
            for proc in psutil.process_iter([
                'pid', 'name', 'cpu_percent', 'memory_percent', 
                'memory_info', 'create_time', 'status', 'username'
            ]):
                try:
                    proc_info = proc.info
                    
                    if proc_info.get('cpu_percent') is None:
                        proc_info['cpu_percent'] = 0.0
                    if proc_info.get('memory_percent') is None:
                        proc_info['memory_percent'] = 0.0
                    
                    memory_info = proc_info.get('memory_info')
                    if memory_info:
                        proc_info['memory_mb'] = memory_info.rss / 1024 / 1024
                    else:
                        proc_info['memory_mb'] = 0.0
                    
                    create_time = proc_info.get('create_time')
                    if create_time:
                        import datetime
                        proc_info['create_time_str'] = datetime.datetime.fromtimestamp(create_time).strftime('%H:%M:%S')
                    else:
                        proc_info['create_time_str'] = 'N/A'
                    
                    if not proc_info.get('username'):
                        proc_info['username'] = 'N/A'
                    
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"获取进程信息时出错: {e}")
            pass
        
        try:
            top_cpu = sorted(processes, 
                           key=lambda x: x.get('cpu_percent') or 0, 
                           reverse=True)[:5]
            top_memory = sorted(processes, 
                          key=lambda x: x.get('memory_percent') or 0, 
                          reverse=True)[:5]
        except Exception as e:
            print(f"排序进程信息时出错: {e}")
            top_cpu = []
            top_memory = []
        
        return {
            'count': len(processes),
            'top_cpu': top_cpu,
            'top_memory': top_memory
        }
    
    def get_system_load(self) -> Dict[str, Any]:
        """获取系统负载"""
        load_info = {}
        
        # 获取系统负载
        try:
            load_avg = os.getloadavg()
            load_info['load_avg'] = {
                '1min': load_avg[0],
                '5min': load_avg[1],
                '15min': load_avg[2]
            }
        except:
            pass
        
        # 获取系统运行时间
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                load_info['uptime'] = uptime_seconds
        except:
            pass
        
        return load_info