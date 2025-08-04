import psutil
import logging

logger = logging.getLogger(__name__)

def get_memory_info():
    """获取内存信息"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = {
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
                'percent': swap.percent,
                'sin': getattr(swap, 'sin', 0),   # 从磁盘交换到内存的字节数
                'sout': getattr(swap, 'sout', 0)  # 从内存交换到磁盘的字节数
            }
        }
        return memory_info
    except Exception as e:
        logger.error(f"获取内存信息失败: {e}")
        return {'virtual': {}, 'swap': {}}


a = get_memory_info()
print(a)