const common = require('../../utils/common.js')

Page({
  data: {
    loading: true,
    userInfo: {
      avatarUrl: 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0',
      nickName: ''
    },
    todayStudyTime: 0,
    userStats: {
      totalDays: 0,
      totalQuestions: 0,
      accuracy: 0
    },
    weekData: [
      { day: '周一', label: '一', hours: 1.5, height: 60, color: 'var(--td-brand-color)' },
      { day: '周二', label: '二', hours: 2.2, height: 88, color: 'var(--td-brand-color)' },
      { day: '周三', label: '三', hours: 0.8, height: 32, color: 'var(--td-brand-color)' },
      { day: '周四', label: '四', hours: 1.2, height: 48, color: 'var(--td-brand-color)' },
      { day: '周五', label: '五', hours: 2.5, height: 100, color: 'var(--td-brand-color)' },
      { day: '周六', label: '六', hours: 3.0, height: 120, color: 'var(--td-brand-color)' },
      { day: '周日', label: '日', hours: 1.8, height: 72, color: 'var(--td-brand-color)' }
    ],
    subjectProgress: [
      { subject: '数学', progress: 75 },
      { subject: '语文', progress: 60 },
      { subject: '英语', progress: 85 },
      { subject: '物理', progress: 45 }
    ],
    todayTasks: [
      {
        id: 1,
        title: '完成数学函数练习',
        description: '二次函数与指数函数',
        status: 'completed'
      },
      {
        id: 2,
        title: '背诵英语单词',
        description: 'Unit 5 单词表',
        status: 'inProgress'
      },
      {
        id: 3,
        title: '完成物理作业',
        description: '力学综合题',
        status: 'pending'
      }
    ],
    suggestions: [
      {
        id: 1,
        content: '您的数学学习进度较快，建议增加一些难题练习来提升能力'
      },
      {
        id: 2,
        content: '物理学习进度较慢，建议每天增加30分钟的学习时间'
      },
      {
        id: 3,
        content: '本周学习时长较上周增加了15%，继续保持！'
      }
    ]
  },

  onLoad() {
    this.initPage()
  },

  onShow() {
    this.refreshData()
  },

  // 初始化页面
  initPage() {
    this.setData({ loading: true })
    
    // 获取用户信息
    this.getUserInfo()
    
    // 获取学习数据
    this.getStudyData()
    
    // 模拟加载延迟
    setTimeout(() => {
      this.setData({ loading: false })
    }, 1000)
  },

  // 获取用户信息
  getUserInfo() {
    const userInfo = common.getStorage('userInfo') || this.data.userInfo
    this.setData({ userInfo })
  },

  // 获取学习数据
  getStudyData() {
    // 模拟获取今日学习时间
    const todayStudyTime = common.getStorage('todayStudyTime') || 45
    
    // 模拟获取用户统计数据
    const userStats = common.getStorage('userStats') || {
      totalDays: 15,
      totalQuestions: 128,
      accuracy: 78
    }
    
    // 模拟获取学科进度
    const subjectProgress = common.getStorage('subjectProgress') || this.data.subjectProgress
    
    // 模拟获取今日任务
    const todayTasks = common.getStorage('todayTasks') || this.data.todayTasks
    
    // 模拟获取学习建议
    const suggestions = common.getStorage('suggestions') || this.data.suggestions
    
    this.setData({
      todayStudyTime,
      userStats,
      subjectProgress,
      todayTasks,
      suggestions
    })
  },

  // 刷新数据
  refreshData() {
    // 每次显示页面时刷新学习时间
    const todayStudyTime = common.getStorage('todayStudyTime') || 0
    this.setData({ todayStudyTime })
  },

  // 跳转到任务页面
  goToTasks() {
    wx.navigateTo({
      url: '/pages/home/tasks'
    })
  },

  // 跳转到文本解题
  goToTextSolve() {
    wx.switchTab({
      url: '/pages/solve/text-solve'
    })
  },

  // 跳转到拍照解题
  goToPhotoSolve() {
    wx.navigateTo({
      url: '/pages/solve/photo-solve'
    })
  },

  // 跳转到智能练习
  goToSmartPractice() {
    wx.switchTab({
      url: '/pages/practice/smart-recommend'
    })
  },

  // 跳转到错题本
  goToWrongQuestions() {
    wx.navigateTo({
      url: '/pages/practice/wrong-questions'
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.initPage()
    wx.stopPullDownRefresh()
  }
})