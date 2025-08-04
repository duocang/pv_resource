<template>
  <div class="dashboard">
    <el-header class="header">
      <h1>系统资源监控</h1>
      <div class="header-controls">
        <el-select v-model="updateInterval" @change="restartUpdating" style="width: 120px; margin-right: 10px;">
          <el-option label="5秒" :value="5001" />
          <el-option label="10秒" :value="10000" />
          <el-option label="30秒" :value="30010" />
        </el-select>
        <el-button type="primary" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-header>
    
    <el-main class="main-content">
      <!-- 现有的统计卡片 -->
      <div class="stats-cards">
        <el-row :gutter="20">
          <!-- CPU卡片 - 添加CPU型号显示 -->
          <el-col :span="6">
            <el-card class="stat-card cpu">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>CPU使用率</h3>
                  <p class="stat-value">{{ systemData.cpu?.percent?.toFixed(1) || 0 }}%</p>
                  <p class="stat-detail">{{ systemData.cpu?.brand || 'Unknown' }}</p>
                  <p class="stat-cores">{{ systemData.cpu?.count_logical || 0 }}核心</p>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 内存卡片 - 添加内存大小显示 -->
          <el-col :span="6">
            <el-card class="stat-card memory">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>内存使用率</h3>
                  <p class="stat-value">{{ systemData.memory?.virtual?.percent?.toFixed(1) || 0 }}%</p>
                  <p class="stat-detail">
                    {{ formatBytes(systemData.memory?.virtual?.used || 0) }} / 
                    {{ formatBytes(systemData.memory?.virtual?.total || 0) }}
                  </p>
                  <p class="stat-available">可用: {{ formatBytes(systemData.memory?.virtual?.available || 0) }}</p>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card disk">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><FolderOpened /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>磁盘使用率</h3>
                  <p class="stat-value">{{ systemData.disk?.percent?.toFixed(1) || 0 }}%</p>
                  <p class="stat-detail">  <!-- 新增 -->
                    {{ formatBytes(systemData.disk?.partitions?.[0]?.used || 0) }} / 
                    {{ formatBytes(systemData.disk?.partitions?.[0]?.total || 0) }}
                  </p>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card network">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>网络流量</h3>
                  <p class="stat-value">{{ formatBytes(networkSpeed) }}/s</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

            <!-- 新增：多核心CPU使用率折线图 -->
      <div class="cpu-cores-container">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card>
              <template #header>
                <h3>CPU各核心使用率趋势</h3>
              </template>
              <div ref="cpuCoresChart" class="chart-large"></div>
              
              <!-- CPU核心状态列表 -->
              <div class="cpu-cores-status">
                <div class="cores-grid">
                  <div 
                    v-for="(core, index) in systemData.cpu?.cores_detail || []" 
                    :key="core.core_id"
                    class="core-item"
                  >
                    <div 
                      class="core-color-indicator" 
                      :style="{ backgroundColor: getCoreColor(index) }"
                    ></div>
                    <span class="core-name">{{ core.name }}</span>
                    <span class="core-percent">{{ core.percent?.toFixed(1) || 0 }}%</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      
      <!-- 现有的图表容器 -->
      <div class="charts-container">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <h3>CPU使用率趋势</h3>
              </template>
              <div ref="cpuChart" class="chart"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card>
              <template #header>
                <h3>内存使用情况</h3>
              </template>
              <div ref="memoryChart" class="chart"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 新增：进程表格容器 -->
      <div class="process-tables">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="table-header">
                  <h3>CPU占用最高的进程</h3>
                  <el-tag type="info">实时更新</el-tag>
                </div>
              </template>
              <el-table 
                :data="systemData.processes?.top_cpu || []" 
                style="width: 100%"
                size="small"
                stripe
              >
                <el-table-column prop="pid" label="PID" width="80" />
                <el-table-column prop="name" label="进程名" width="120" show-overflow-tooltip />
                <el-table-column prop="username" label="用户" width="80" show-overflow-tooltip />
                <el-table-column 
                  prop="cpu_percent" 
                  label="CPU%" 
                  width="80"
                  :formatter="(row) => row.cpu_percent?.toFixed(1) + '%'"
                  sortable
                />
                <el-table-column 
                  prop="memory_mb" 
                  label="内存(MB)" 
                  width="100"
                  :formatter="(row) => row.memory_mb?.toFixed(1)"
                />
                <el-table-column prop="status" label="状态" width="80" />
                <el-table-column prop="create_time_str" label="启动时间" width="80" />
              </el-table>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="table-header">
                  <h3>内存占用最高的进程</h3>
                  <el-tag type="info">实时更新</el-tag>
                </div>
              </template>
              <el-table 
                :data="systemData.processes?.top_memory || []" 
                style="width: 100%"
                size="small"
                stripe
              >
                <el-table-column prop="pid" label="PID" width="80" />
                <el-table-column prop="name" label="进程名" width="120" show-overflow-tooltip />
                <el-table-column prop="username" label="用户" width="80" show-overflow-tooltip />
                <el-table-column 
                  prop="memory_percent" 
                  label="内存%" 
                  width="80"
                  :formatter="(row) => row.memory_percent?.toFixed(1) + '%'"
                  sortable
                />
                <el-table-column 
                  prop="memory_mb" 
                  label="内存(MB)" 
                  width="100"
                  :formatter="(row) => row.memory_mb?.toFixed(1)"
                />
                <el-table-column prop="status" label="状态" width="80" />
                <el-table-column prop="create_time_str" label="启动时间" width="80" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { SwitchButton, Cpu, Monitor, FolderOpened, Connection } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 图表引用
const cpuChart = ref()
const memoryChart = ref()
const cpuCoresChart = ref()  // 新增：多核心图表引用

// 数据状态
const systemData = reactive({})
const networkSpeed = ref(0)
let charts = {}
let updateTimer = null

// 添加网络数据历史记录
let lastNetworkData = null
let lastNetworkTime = null

// 新增：CPU核心颜色配置
const coreColors = [
  '#409eff', '#67c23a', '#e6a23c', '#f56c6c', 
  '#909399', '#c71585', '#ff6347', '#32cd32',
  '#1e90ff', '#ff69b4', '#ffd700', '#8a2be2',
  '#00ced1', '#ff4500', '#9acd32', '#dc143c',
  '#409eff', '#67c23a', '#e6a23c', '#f56c6c', 
  '#909399', '#c71585', '#ff6347', '#32cd32',
  '#1e90ff', '#ff69b4', '#ffd700', '#8a2be2',
  '#00ced1', '#ff4500', '#9acd32', '#dc143c',
  '#409eff', '#67c23a', '#e6a23c', '#f56c6c', 
  '#909399', '#c71585', '#ff6347', '#32cd32',
  '#1e90ff', '#ff69b4', '#ffd700', '#8a2be2',
  '#00ced1', '#ff4500', '#9acd32', '#dc143c'
]

// 获取核心颜色
const getCoreColor = (index) => {
  return coreColors[index % coreColors.length]
}

// 初始化图表
const initCharts = () => {
  // CPU使用率趋势图
  charts.cpu = echarts.init(cpuChart.value)
  charts.cpu.setOption({
    title: { 
      text: 'CPU使用率趋势',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: { 
      trigger: 'axis',
      formatter: function(params) {
        return `时间: ${params[0].axisValue}<br/>CPU使用率: ${params[0].value}%`
      }
    },
    xAxis: { type: 'category', data: [] },
    yAxis: { 
      type: 'value', 
      min: 0, 
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: 'CPU使用率',
      type: 'line',
      data: [],
      smooth: true,
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#409eff' },
      areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }
    }]
  })
  
  // 内存使用饼图
  charts.memory = echarts.init(memoryChart.value)

  charts.memory.setOption({
    title: { 
      text: '内存使用情况', 
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: { trigger: 'item' },
    series: [{
      name: '内存使用',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '60%'],
      data: [
        { value: 0, name: '已使用' },
        { value: 0, name: '可用' }
      ]
    }]
  })

// 新增：初始化多核心CPU图表
  charts.cpuCores = echarts.init(cpuCoresChart.value)
  charts.cpuCores.setOption({
    title: { 
      // text: 'CPU各核心使用率趋势',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      },
      left: 'center',
      top: 10
    },
    tooltip: { 
      trigger: 'axis',
      formatter: function(params) {
        let result = `时间: ${params[0].axisValue}<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ${param.value}%<br/>`
        })
        return result
      }
    },
    legend: {
      type: 'scroll',
      orient: 'horizontal',
      top: 40,
      left: 'center',
      data: []
    },
    grid: {
      top: 10,      // 减少顶部空白
      bottom: 0,   // 减少底部空白
      left: 20,     // 减少左侧空白
      right: 20,    // 减少右侧空白
      containLabel: true  // 确保坐标轴标签完全显示
    },
    xAxis: { 
      type: 'category', 
      data: [],
      axisLabel: {
        rotate: 45,
        fontSize: 12
      }
    },
    yAxis: { 
      type: 'value', 
      min: 0, 
      max: 100,
      axisLabel: {
        formatter: '{value}%',
        fontSize: 12
      }
    },
    series: []
  })

}

// 更新图表数据
const updateCharts = () => {
  const currentTime = new Date().toLocaleTimeString()
  
  // 更新CPU趋势图
  if (charts.cpu && systemData.cpu) {
    const option = charts.cpu.getOption()
    const xData = option.xAxis[0].data
    const seriesData = option.series[0].data
    
    // 添加新数据点
    xData.push(currentTime)
    seriesData.push(systemData.cpu.percent || 0)
    
    // 保持最多20个数据点
    if (xData.length > 20) {
      xData.shift()
      seriesData.shift()
    }
    
    charts.cpu.setOption({
      title: {
        text: `CPU使用率趋势\n${systemData.cpu?.brand || 'Unknown'} (${systemData.cpu?.count_logical || 0}核心)`,
        textStyle: {
          fontSize: 14,
          fontWeight: 'normal'
        }
      },
      xAxis: { data: xData },
      series: [{ data: seriesData }]
    })
  }
  
  // 更新内存饼图
  if (charts.memory && systemData.memory?.virtual) {
    const used = systemData.memory.virtual.used || 0
    const available = systemData.memory.virtual.available || 0
    const total = systemData.memory.virtual.total || 0
    
    // 添加调试打印
    console.log('Memory Data:', {
      used: formatBytes(used),
      available: formatBytes(available),
      total: formatBytes(total),
      percent: ((used / total) * 100).toFixed(1) + '%'
    });
    
    charts.memory.setOption({
      title: {
        text: `内存使用情况\n总计: ${formatBytes(total)}`,
        left: 'center',
        textStyle: {
          fontSize: 14,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: function(params) {
          const percentage = ((params.value / total) * 100).toFixed(1)
          return `${params.name}: ${formatBytes(params.value)} (${percentage}%)`
        }
      },
      series: [{
        name: '内存使用',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '60%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'outside',
          formatter: function(params) {
            return `${params.name}\n${formatBytes(params.value)}`
          }
        },
        labelLine: {
          show: true
        },
        data: [
          { 
            value: used, 
            name: '已使用',
            itemStyle: { color: '#67c23a' }
          },
          { 
            value: available, 
            name: '可用',
            itemStyle: { color: '#e6f7ff' }
          }
        ]
      }]
    })
  }


    // 新增：更新多核心CPU图表
  if (charts.cpuCores && systemData.cpu?.cores_detail) {
    const option = charts.cpuCores.getOption()
    const xData = option.xAxis[0].data
    const coresData = systemData.cpu.cores_detail
    
    // 添加新时间点
    xData.push(currentTime)
    
    // 保持最多60个数据点（5分钟数据）
    if (xData.length > 60) {
      xData.shift()
    }
    
    // 更新每个核心的数据系列
    const series = []
    const legendData = []
    
    coresData.forEach((core, index) => {
      const seriesName = core.name
      legendData.push(seriesName)
      
      // 获取现有系列数据或创建新的
      let seriesData = []
      if (option.series && option.series[index]) {
        seriesData = [...option.series[index].data]
      }
      
      // 添加新数据点
      seriesData.push(core.percent || 0)
      
      // 保持数据点数量一致
      if (seriesData.length > 60) {
        seriesData.shift()
      }
      
      series.push({
        name: seriesName,
        type: 'line',
        data: seriesData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        itemStyle: { color: getCoreColor(index) },
        lineStyle: { color: getCoreColor(index) }
      })
    })
    
    charts.cpuCores.setOption({
      // legend: { data: legendData },
      xAxis: { data: xData },
      series: series
    })
  }
}

// 在fetchSystemStatus函数中
const fetchSystemStatus = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/system-status', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.data.success) {
      // 添加调试打印：查看原始响应数据
      console.log('API Response Memory:', response.data.data.memory)
      
      // 计算网络速度
      const currentTime = Date.now()
      const currentNetworkData = response.data.data.network?.io
      
      if (lastNetworkData && lastNetworkTime && currentNetworkData) {
        const timeDiff = (currentTime - lastNetworkTime) / 1000 // 转换为秒
        const bytesSentDiff = (currentNetworkData.bytes_sent || 0) - (lastNetworkData.bytes_sent || 0)
        const bytesRecvDiff = (currentNetworkData.bytes_recv || 0) - (lastNetworkData.bytes_recv || 0)
        
        // 计算总速度（上传+下载）
        const totalSpeed = (bytesSentDiff + bytesRecvDiff) / timeDiff
        networkSpeed.value = Math.max(0, totalSpeed) // 确保不为负数
        
        console.log('Network Speed Calculation:', {
          timeDiff,
          bytesSentDiff,
          bytesRecvDiff,
          totalSpeed: formatBytes(totalSpeed) + '/s'
        })
      }
      
      // 更新历史数据
      if (currentNetworkData) {
        lastNetworkData = { ...currentNetworkData }
        lastNetworkTime = currentTime
      }
      
      Object.assign(systemData, response.data.data)
      updateCharts()
    }
  } catch (error) {
    console.error('请求失败:', error.response?.data)
    ElMessage.error('获取系统状态失败')
  }
}

// 格式化字节为GB（专门用于内存显示）
const formatBytesToGB = (bytes) => {
  if (bytes === 0) return '0 GB'
  const gb = bytes / (1024 * 1024 * 1024)
  return gb.toFixed(1) + ' GB'
}

// 格式化字节（通用）
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 退出登录
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 修改更新间隔设置
const updateInterval = ref(5001) // 默认5秒

// 重启定时更新
const restartUpdating = () => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
  startUpdating()
}

// 启动定时更新
const startUpdating = () => {
  fetchSystemStatus()
  updateTimer = setInterval(() => {
    fetchSystemStatus()
  }, updateInterval.value)
}

onMounted(() => {
  initCharts()
  startUpdating()
})

onUnmounted(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
  Object.values(charts).forEach(chart => chart.dispose())
})
</script>

<style scoped>
.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-controls {
  display: flex;
  align-items: center;
}

.header h1 {
  margin: 0;
  color: #303133;
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 48px;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #909399;
}

.stat-value {
  margin: 0 0 5px 0;
  font-size: 24px;
  font-weight: bold;
}

.stat-detail {
  margin: 0 0 3px 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.2;
}

.stat-cores,
.stat-available {
  margin: 0;
  font-size: 11px;
  color: #909399;
  line-height: 1.2;
}

/* 调整卡片高度以容纳更多信息 */
.stat-card {
  height: 140px;
}

.cpu .stat-icon { color: #409eff; }
.memory .stat-icon { color: #67c23a; }
.disk .stat-icon { color: #e6a23c; }
.network .stat-icon { color: #f56c6c; }

.cpu .stat-value { color: #409eff; }
.memory .stat-value { color: #67c23a; }
.disk .stat-value { color: #e6a23c; }
.network .stat-value { color: #f56c6c; }

.chart {
  height: 300px;
}

.process-tables {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  color: #303133;
}

.el-table {
  font-size: 12px;
}

.el-table .el-table__cell {
  padding: 8px 0;
}

/* 新增样式 */
.cpu-cores-container {
  margin-bottom: 20px;
}

.chart-large {
  height: 400px;
}

.cpu-cores-status {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.cores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1px;
}

.core-item {
  display: flex;
  align-items: center;
  padding: 1px 1px;
  /* background: #f8f9fa; */
  /* border-radius: 6px; */
  /* border: 1px solid #e9ecef; */ /* 去掉外边框 */
  width: 150px;
}

.core-color-indicator {
  width: 16px;      /* 增大矩形方块：从12px改为16px */
  height: 16px;     /* 增大矩形方块：从12px改为16px */
  border-radius: 1px; /* 稍微调整圆角：从2px改为3px */
  margin-right: 3px;
  flex-shrink: 0;
}

.core-name {
  flex: 1;
  font-size: 14px;
  color: #606266;
}

.core-percent {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  /* margin-right: 30px; */
}
</style>