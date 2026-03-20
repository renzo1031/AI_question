const request = require('../../utils/request.js');
const api = require('../../utils/api.js');

Page({
  data: {
    loading: true,
    overview: null,
    ability: null,
    feedback: [],
    timeWindow: 30
  },

  onShow() {
    this.loadAllData();
  },

  async loadAllData() {
    this.setData({ loading: true });
    try {
      const [overview, ability, feedback] = await Promise.all([
        request.get(api.learning.overview, { time_window_days: this.data.timeWindow }),
        request.get(api.learning.ability, { time_window_days: this.data.timeWindow }),
        request.get(api.learning.feedback)
      ]);

      // 处理overview数据以适配新的API结构
      const processedOverview = overview ? {
        ...overview,
        trend: overview.trend?.direction === 'up' ? '进步' : 
               overview.trend?.direction === 'down' ? '需加油' : '保持稳定',
        daily_stats: overview.daily_stats || [],
        recent_stats: overview.recent_stats || {},
        all_time_stats: overview.all_time_stats || {},
        last_10_accuracy: overview.last_10_accuracy?.accuracy || 0
      } : null;

      this.setData({
        overview: processedOverview,
        ability,
        feedback: feedback || [],
        loading: false
      });
    } catch (err) {
      console.error('加载学习分析数据失败:', err);
      this.setData({ loading: false });
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      });
    }
  },

  changeTimeWindow(e) {
    const days = e.currentTarget.dataset.days;
    if (days === this.data.timeWindow) return;
    
    this.setData({ timeWindow: days }, () => {
      this.loadAllData();
    });
  },

  practiceWeakPoint(e) {
    const { point } = e.currentTarget.dataset;
    // 这里可以跳转到练习页面，自动筛选该知识点的题目
    wx.navigateTo({
      url: `/pages/practice/index?subject=${point.subject}&knowledge=${point.knowledge_point}`
    });
  }
});
