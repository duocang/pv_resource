import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/login', {
          username,
          password
        })
        
        if (response.data.success) {
          this.token = response.data.token
          localStorage.setItem('token', this.token)
          
          // // 添加调试信息
          // console.log('Token saved:', this.token)
          // console.log('LocalStorage token:', localStorage.getItem('token'))
          
          // 设置axios默认header
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
          
          // // 验证header是否正确设置
          // console.log('Authorization header:', axios.defaults.headers.common['Authorization'])
          
          return { success: true }
        } else {
          return { success: false, message: response.data.message }
        }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.message || '登录失败' 
        }
      }
    },
    
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    
    initializeAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        // 安全的调试信息 - 只显示token的前几位和后几位
        const tokenPreview = this.token.length > 10 
          ? `${this.token.substring(0, 10)}...${this.token.substring(this.token.length - 10)}`
          : 'token_present'
        
        console.log('Auth initialized with token:', tokenPreview)
        console.log('Authorization header configured successfully')
      } else {
        console.log('No token found for initialization')
      }
    }
  }
})