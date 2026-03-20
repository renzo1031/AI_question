const common = require('../../utils/common.js')

Page({
  data: {
    loading: true,
    activeTab: 'all',
    practiceRecommend: [
      {
        id: 1,
        title: '二次函数综合练习',
        description: '包含二次函数的图像、性质和应用的综合题目',
        difficulty: 2,
        difficultyText: '中等',
        difficultyTheme: 'warning',
        tags: ['函数', '图像', '应用'],
        questionCount: 15,
        completedCount: 234,
        accuracy: 78
      },
      {
        id: 2,
        title: '英语完形填空专项训练',
        description: '针对完形填空题型的专项训练，提高语感和逻辑推理能力',
        difficulty: 3,
        difficultyText: '困难',
        difficultyTheme: 'danger',
        tags: ['完形填空', '语法', '词汇'],
        questionCount: 20,
        completedCount: 156,
        accuracy: 65
      },
      {
        id: 3,
        title: '物理力学基础练习',
        description: '力学基础概念和公式的应用练习',
        difficulty: 1,
        difficultyText: '简单',
        difficultyTheme: 'success',
        tags: ['力学', '基础', '公式'],
        questionCount: 12,
        completedCount: 412,
        accuracy: 85
      }
    ],
    knowledgeRecommend: [
      {
        id: 1,
        title: '函数的单调性与奇偶性',
        description: '掌握函数单调性和奇偶性的判断方法及其应用',
        subject: '数学',
        mastery: 65,
        progressColor: 'var(--td-warning-color)',
        relatedQuestions: 28,
        studyTime: 45
      },
      {
        id: 2,
        title: '定语从句',
        description: '学习定语从句的用法和关系词的选择',
        subject: '英语',
        mastery: 40,
        progressColor: 'var(--td-error-color)',
        relatedQuestions: 35,
        studyTime: 60
      },
      {
        id: 3,
        title: '牛顿运动定律',
        description: '理解牛顿三大运动定律及其应用',
        subject: '物理',
        mastery: 80,
        progressColor: 'var(--td-success-color)',
        relatedQuestions: 22,
        studyTime: 30
      }
    ],
    courseRecommend: [
      {
        id: 1,
        title: '高中数学函数专题',
        description: '系统讲解高中数学中的函数知识，包括基本概念、性质和应用',
        cover: 'https://tdesign.gtimg.com/miniprogram/images/example1.png',
        teacher: '王老师',
        duration: '2小时30分',
        students: 1256,
        rating: 4.8,
        isHot: true
      },
      {
        id: 2,
        title: '英语语法精讲',
        description: '详细讲解英语语法中的重点难点，帮助你攻克语法难关',
        cover: 'https://tdesign.gtimg.com/miniprogram/images/example2.png',
        teacher: '李老师',
        duration: '3小时15分',
        students: 892,
        rating: 4.6,
        isHot: false
      },
      {
        id: 3,
        title: '物理力学入门',
        description: '从基础概念开始，循序渐进地学习物理力学知识',
        cover: 'https://tdesign.gtimg.com/miniprogram/images/example3.png',
        teacher: '张老师',
        duration: '1小时45分',
        students: 634,
        rating: 4.7,
        isHot: false
      }
    ]
  },

  onLoad() {
    this.initPage()
  },

  // 初始化页面
  initPage() {
    this.setData({ loading: true })
    
    // 获取推荐内容
    this.getRecommendData()
    
    // 模拟加载延迟
    setTimeout(() => {
      this.setData({ loading: false })
    }, 800)
  },

  // 获取推荐数据
  getRecommendData() {
    // 这里可以调用API获取个性化推荐内容
    // 目前使用模拟数据
  },

  // 切换标签
  onTabChange(e) {
    const value = e.detail.value
    this.setData({ activeTab: value })
  },

  // 跳转到练习
  goToPractice(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/practice/chapter-practice?id=${id}`
    })
  },

  // 跳转到知识点
  goToKnowledge(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/practice/knowledge-practice?id=${id}`
    })
  },

  // 跳转到课程
  goToCourse(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/course/detail?id=${id}`
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.initPage()
    wx.stopPullDownRefresh()
  }
})