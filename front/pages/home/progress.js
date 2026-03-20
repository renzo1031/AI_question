const common = require('../../utils/common.js')

Page({
  data: {
    loading: true,
    empty: false,
    activeTab: 'subject',
    overallProgress: {
      completed: 42,
      total: 78,
      percentage: 54
    },
    subjectProgress: [
      {
        id: 1,
        name: '数学',
        icon: 'chart',
        color: '#0052d9',
        percentage: 65,
        studyTime: '32小时',
        completed: 13,
        total: 20
      },
      {
        id: 2,
        name: '英语',
        icon: 'translation',
        color: '#00a870',
        percentage: 48,
        studyTime: '28小时',
        completed: 12,
        total: 25
      },
      {
        id: 3,
        name: '物理',
        icon: 'lightbulb',
        color: '#ed7b2f',
        percentage: 72,
        studyTime: '24小时',
        completed: 13,
        total: 18
      },
      {
        id: 4,
        name: '化学',
        icon: 'flask',
        color: '#d54941',
        percentage: 35,
        studyTime: '18小时',
        completed: 4,
        total: 15
      }
    ],
    chapterProgress: [
      {
        id: 1,
        subject: '数学 - 函数',
        description: '一次函数、二次函数、指数函数与对数函数',
        percentage: 75
      },
      {
        id: 2,
        subject: '数学 - 几何',
        description: '平面几何、立体几何、解析几何',
        percentage: 60
      },
      {
        id: 3,
        subject: '英语 - 语法',
        description: '时态、语态、从句、非谓语动词',
        percentage: 45
      },
      {
        id: 4,
        subject: '英语 - 词汇',
        description: '高频词汇、短语搭配、词根词缀',
        percentage: 52
      },
      {
        id: 5,
        subject: '物理 - 力学',
        description: '运动学、动力学、功和能',
        percentage: 80
      },
      {
        id: 6,
        subject: '物理 - 电磁学',
        description: '电场、磁场、电磁感应',
        percentage: 65
      }
    ],
    knowledgeProgress: [
      {
        id: 1,
        name: '二次函数',
        subject: '数学',
        mastery: 85,
        questionCount: 25,
        accuracy: 88
      },
      {
        id: 2,
        name: '定语从句',
        subject: '英语',
        mastery: 45,
        questionCount: 30,
        accuracy: 62
      },
      {
        id: 3,
        name: '牛顿运动定律',
        subject: '物理',
        mastery: 75,
        questionCount: 20,
        accuracy: 80
      },
      {
        id: 4,
        name: '化学方程式',
        subject: '化学',
        mastery: 30,
        questionCount: 35,
        accuracy: 55
      },
      {
        id: 5,
        name: '三角函数',
        subject: '数学',
        mastery: 60,
        questionCount: 28,
        accuracy: 70
      },
      {
        id: 6,
        name: '时态与语态',
        subject: '英语',
        mastery: 55,
        questionCount: 32,
        accuracy: 68
      }
    ]
  },

  onLoad() {
    this.initPage()
  },

  // 初始化页面
  initPage() {
    this.setData({ loading: true, empty: false })
    
    // 获取进度数据
    this.getProgressData()
    
    // 模拟加载延迟
    setTimeout(() => {
      this.setData({ loading: false })
    }, 800)
  },

  // 获取进度数据
  getProgressData() {
    // 这里可以调用API获取实际进度数据
    // 目前使用模拟数据
    
    // 检查是否有数据
    const hasData = this.data.subjectProgress.length > 0
    this.setData({ empty: !hasData })
  },

  // 切换标签
  onTabChange(e) {
    const value = e.detail.value
    this.setData({ activeTab: value })
  },

  // 跳转到科目详情
  goToSubjectDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/study/subject-detail?id=${id}`
    })
  },

  // 跳转到章节详情
  goToChapterDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/study/chapter-detail?id=${id}`
    })
  },

  // 练习知识点
  practiceKnowledge(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/practice/knowledge-practice?id=${id}`
    })
  },

  // 复习知识点
  reviewKnowledge(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/study/knowledge-review?id=${id}`
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.initPage()
    wx.stopPullDownRefresh()
  }
})