import psutil
import subprocess
from typing import Dict, Any
from .base_monitor import BaseSystemMonitor

class MacOSSystemMonitor(BaseSystemMonitor):
    """macOS系统监控器"""

    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        cpu_info = {
            'percent': psutil.cpu_percent(interval=1),
            'count_logical': psutil.cpu_count(logical=True),
            'count_physical': psutil.cpu_count(logical=False),
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
        }
        
        # macOS特有的CPU信息
        try:
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                cpu_info['brand'] = result.stdout.strip()
        except:
            pass
        
        return cpu_info

    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息 - macOS简化版本"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # 在macOS中，更准确的可用内存计算
        # available = free + inactive + cached
        # 但psutil已经做了这个计算，我们主要修正used的计算

        total = memory.total
        available = memory.available

        # 修正：真实使用的内存 = 总内存 - 可用内存
        real_used = total - available

        # 重新计算使用率
        real_percent = (real_used / total) * 100 if total > 0 else 0

        memory_info = {
            'virtual': {
                'total': total,
                'available': available,
                'used': real_used,  # 使用修正后的值
                'free': memory.free,
                'percent': real_percent  # 使用修正后的百分比
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }

        # macOS特有的内存压力信息
        try:
            result = subprocess.run(['memory_pressure'], capture_output=True, text=True)
            if result.returncode == 0:
                memory_info['pressure'] = result.stdout.strip()
        except:
            pass

        return memory_info

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
            # 获取更详细的进程信息
            for proc in psutil.process_iter([
                'pid', 'name', 'cpu_percent', 'memory_percent', 
                'memory_info', 'create_time', 'status', 'username'
            ]):
                try:
                    proc_info = proc.info
                    
                    # 确保cpu_percent和memory_percent不为None
                    if proc_info.get('cpu_percent') is None:
                        proc_info['cpu_percent'] = 0.0
                    if proc_info.get('memory_percent') is None:
                        proc_info['memory_percent'] = 0.0
                    
                    # 添加内存使用量（MB）
                    memory_info = proc_info.get('memory_info')
                    if memory_info:
                        proc_info['memory_mb'] = memory_info.rss / 1024 / 1024
                    else:
                        proc_info['memory_mb'] = 0.0
                    
                    # 格式化创建时间
                    create_time = proc_info.get('create_time')
                    if create_time:
                        import datetime
                        proc_info['create_time_str'] = datetime.datetime.fromtimestamp(create_time).strftime('%H:%M:%S')
                    else:
                        proc_info['create_time_str'] = 'N/A'
                    
                    # 处理用户名
                    if not proc_info.get('username'):
                        proc_info['username'] = 'N/A'
                    
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"获取进程信息时出错: {e}")
            pass
        
        # 安全的排序，获取前5个
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
            load_avg = psutil.getloadavg()
            load_info['load_avg'] = {
                '1min': load_avg[0],
                '5min': load_avg[1],
                '15min': load_avg[2]
            }
        except:
            pass
        
        # 获取系统运行时间
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True)
            if result.returncode == 0:
                load_info['uptime_info'] = result.stdout.strip()
        except:
            pass
        
        return load_info

    def get_all_info(self) -> Dict[str, Any]:
        """获取所有系统信息，格式化为前端期望的结构"""
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        network_info = self.get_network_info()
        process_info = self.get_process_info()
        load_info = self.get_system_load()
        
        # 计算主磁盘使用率（通常是根分区）
        main_disk_percent = 0
        if disk_info['partitions']:
            # 找到根分区或最大的分区
            main_partition = max(disk_info['partitions'], 
                               key=lambda x: x.get('total', 0))
            main_disk_percent = main_partition.get('percent', 0)
        
        return {
            'cpu': {
                'percent': cpu_info.get('percent', 0),
                'count_logical': cpu_info.get('count_logical', 0),
                'count_physical': cpu_info.get('count_physical', 0),
                'brand': cpu_info.get('brand', 'Unknown')
            },
            'memory': {
                'percent': memory_info['virtual'].get('percent', 0),
                'total': memory_info['virtual'].get('total', 0),
                'used': memory_info['virtual'].get('used', 0),
                'available': memory_info['virtual'].get('available', 0)
            },
            'disk': {
                'percent': main_disk_percent,
                'partitions': disk_info['partitions'],
                'io': disk_info.get('io', {})
            },
            'network': {
                'interfaces': network_info.get('interfaces', {}),
                'io': network_info.get('io', {})
            },
            'processes': process_info,
            'load': load_info
        }