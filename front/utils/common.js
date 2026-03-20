// 通用工具函数
const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

const formatDate = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()

  return `${[year, month, day].map(formatNumber).join('-')}`
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

// 显示提示信息
const showToast = (title, icon = 'none', duration = 2000) => {
  wx.showToast({
    title,
    icon,
    duration
  })
}

// 显示加载中
const showLoading = (title = '加载中') => {
  wx.showLoading({
    title,
    mask: true
  })
}

// 隐藏加载中
const hideLoading = () => {
  wx.hideLoading()
}

// 显示确认对话框
const showModal = (title, content) => {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      success: (res) => {
        resolve(res.confirm)
      }
    })
  })
}

// 获取用户信息
const getUserInfo = () => {
  return new Promise((resolve, reject) => {
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (res) => {
        resolve(res.userInfo)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 登录
const login = () => {
  return new Promise((resolve, reject) => {
    wx.login({
      success: (res) => {
        resolve(res.code)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 选择图片
const chooseImage = (count = 1) => {
  return new Promise((resolve, reject) => {
    wx.chooseImage({
      count,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        resolve(res.tempFilePaths)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 上传文件
const uploadFile = (filePath, url, formData = {}) => {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url,
      filePath,
      name: 'file',
      formData,
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          resolve(res.data)
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 网络请求
const request = (url, method = 'GET', data = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method,
      data,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 本地存储
const setStorage = (key, data) => {
  try {
    wx.setStorageSync(key, data)
    return true
  } catch (e) {
    return false
  }
}

// 获取本地存储
const getStorage = (key) => {
  try {
    return wx.getStorageSync(key)
  } catch (e) {
    return null
  }
}

// 删除本地存储
const removeStorage = (key) => {
  try {
    wx.removeStorageSync(key)
    return true
  } catch (e) {
    return false
  }
}

// 防抖函数
const debounce = (func, wait) => {
  let timeout
  return function(...args) {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      func.apply(this, args)
    }, wait)
  }
}

// 节流函数
const throttle = (func, wait) => {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= wait) {
      lastTime = now
      func.apply(this, args)
    }
  }
}

// 生成随机ID
const generateId = (length = 8) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// 计算学习时间
const calculateStudyTime = (startTime, endTime) => {
  const start = new Date(startTime)
  const end = new Date(endTime)
  const diff = end - start
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  return {
    hours,
    minutes,
    totalMinutes: Math.floor(diff / (1000 * 60))
  }
}

// 格式化学习时间
const formatStudyTime = (minutes) => {
  if (minutes < 60) {
    return `${minutes}分钟`
  } else {
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`
  }
}

// 计算正确率
const calculateAccuracy = (correct, total) => {
  if (total === 0) return 0
  return Math.round((correct / total) * 100)
}

// 获取难度等级文本
const getDifficultyText = (level) => {
  const difficultyMap = {
    1: '简单',
    2: '中等',
    3: '困难',
    4: '极难'
  }
  return difficultyMap[level] || '未知'
}

// 获取科目图标
const getSubjectIcon = (subject) => {
  const iconMap = {
    '语文': 'book',
    '数学': 'chart',
    '英语': 'translation',
    '物理': 'lightbulb',
    '化学': 'chemistry',
    '生物': 'leaf',
    '历史': 'time',
    '地理': 'location',
    '政治': 'flag'
  }
  return iconMap[subject] || 'book'
}

// 获取科目颜色
const getSubjectColor = (subject) => {
  const colorMap = {
    '语文': '#e34d59',
    '数学': '#0052d9',
    '英语': '#ed7b2f',
    '物理': '#00a870',
    '化学': '#722ed1',
    '生物': '#00b8a9',
    '历史': '#d54941',
    '地理': '#059b9a',
    '政治': '#eb7350'
  }
  return colorMap[subject] || '#0052d9'
}

module.exports = {
  formatTime,
  formatDate,
  formatNumber,
  showToast,
  showLoading,
  hideLoading,
  showModal,
  getUserInfo,
  login,
  chooseImage,
  uploadFile,
  request,
  setStorage,
  getStorage,
  removeStorage,
  debounce,
  throttle,
  generateId,
  calculateStudyTime,
  formatStudyTime,
  calculateAccuracy,
  getDifficultyText,
  getSubjectIcon,
  getSubjectColor
}