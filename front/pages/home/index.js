const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const config = require('../../utils/config.js');

Page({
  data: {
    userInfo: {},
    overview: {},
    dailyTask: {},
    subjects: [],
    announcements: [],
    currentAnnouncementIndex: 0,
    banners: [], // 轮播图数据
    bannerInterval: 15000, // 轮播图自动切换间隔（毫秒），可自定义
    currentBannerIndex: 0, // 当前轮播图索引
    loading: false,
    navHeight: 0, // 导航栏总高度
    statusBarHeight: 0, // 状态栏高度
    accuracyBarColor: '#FAAD14', // 正确率进度条颜色
    featureGrid: [
      {
        id: 'practice',
        name: '每日练习',
        icon: '/images/practice.png',
        url: '/pages/practice/index',
        type: 'switchTab',
        color: '#4A90E2'
      },
      {
        id: 'mistake',
        name: '错题本',
        icon: '/images/mistake.png',
        url: '/pages/mistake/index',
        type: 'switchTab',
        color: '#FF6B6B'
      },
      {
        id: 'analysis',
        name: '学情分析',
        emoji: '📊',
        url: '/pages/analysis/index',
        type: 'navigateTo',
        color: '#50E3C2'
      },
      {
        id: 'history',
        name: '搜题记录',
        emoji: '🕒',
        url: '/pages/ai/history/index',
        type: 'navigateTo',
        color: '#F5A623'
      },
      {
        id: 'ai_chat',
        name: 'AI 助教',
        icon: '/images/ai_avatar.png',
        url: '/pages/ai/chat',
        type: 'navigateTo',
        color: '#9013FE'
      },
      {
        id: 'subjects',
        name: '科目专项',
        emoji: '📚',
        url: '', // 暂无统一入口，或者做成弹窗
        type: 'action',
        action: 'showSubjects',
        color: '#B8E986'
      }
    ]
  },

  onLoad() {
    this.calcNavBarHeight();
  },

  handleGridTap(e) {
    const { item } = e.currentTarget.dataset;
    if (!item) return;

    if (item.type === 'switchTab') {
      wx.switchTab({ url: item.url });
    } else if (item.type === 'navigateTo') {
      wx.navigateTo({ url: item.url });
    } else if (item.type === 'action') {
      if (item.action === 'showSubjects') {
        wx.showToast({
          title: '科目功能开发中',
          icon: 'none'
        });
      }
    }
  },

  calcNavBarHeight() {
    const systemInfo = wx.getWindowInfo();
    const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
    
    // 导航栏高度 = (胶囊按钮顶部位置 - 状态栏高度) * 2 + 胶囊按钮高度
    const navBarHeight = (menuButtonInfo.top - systemInfo.statusBarHeight) * 2 + menuButtonInfo.height;
    // 总高度 = 状态栏高度 + 导航栏高度 + 额外一点间距(20rpx左右)让视觉更舒适
    const totalHeaderHeight = systemInfo.statusBarHeight + navBarHeight;
    
    this.setData({
      navHeight: totalHeaderHeight,
      statusBarHeight: systemInfo.statusBarHeight
    });
  },

  onShow() {
    this.checkLogin();
  },

  checkLogin() {
    const token = wx.getStorageSync(config.tokenKey);
    const userInfo = wx.getStorageSync(config.userKey);
    
    if (!token) {
      wx.redirectTo({
        url: '/pages/auth/login'
      });
      return;
    }

    this.setData({ userInfo });
    this.loadData();
  },

  async loadData() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      // 加载轮播图数据
      const banners = await request.get(api.banner.active).catch(err => {
        console.error('加载轮播图失败:', err);
        return [];
      });

      // 加载学习概览数据
      const overviewData = await request.get(api.learning.overview, { time_window_days: 30 }).catch(err => {
        console.error('加载学习概览失败:', err);
        return null;
      });

      // 加载有效公告
      const announcementRes = await request.get(api.announcement.active, { limit: 5 }).catch(err => {
        console.error('加载公告失败:', err);
        return [];
      });

      // 处理学习概览数据
      let processedOverview = { total_study_days: 0, total_questions: 0, streak_days: 0 };
      let accuracyBarColor = '#FAAD14'; // 默认黄色
      if (overviewData) {
        const allTimeStats = overviewData.all_time_stats || {};
        const recentStats = overviewData.recent_stats || {};
        const last10Accuracy = overviewData.last_10_accuracy || {};
        const dailyStats = overviewData.daily_stats || {};
        const trendData = overviewData.trend || {};

        const accuracy = Math.round((last10Accuracy.accuracy || 0) * 100);

        // 计算正确率进度条颜色
        if (accuracy >= 80) {
          accuracyBarColor = '#52C41A'; // 绿色
        } else if (accuracy >= 60) {
          accuracyBarColor = '#FAAD14'; // 黄色
        } else {
          accuracyBarColor = '#FF4D4F'; // 红色
        }

        processedOverview = {
          // 全部历史统计
          total_study_days: overviewData.consecutive_days || 0, // 使用新的连续学习天数字段
          total_questions: allTimeStats.questions || 0,
          streak_days: overviewData.consecutive_days || 0,

          // 最近10题正确率
          last_10_accuracy: accuracy,
          last_10_accuracy_formatted: last10Accuracy.accuracy_formatted?.percentage || '0%',
          last_10_accuracy_level: last10Accuracy.accuracy_formatted?.level || '',

          // 每日答题数
          today_questions: dailyStats.answered_today || 0,
          recent_7_days_questions: dailyStats.answered_last_7_days || 0,

          // 学习趋势
          trend_direction: trendData.direction || 'stable',
          trend_change: trendData.change || '',
          trend_message: trendData.message || '',

          // 数据是否充足
          data_sufficient: overviewData.data_sufficient || false,

          // 近期统计
          recent_total_questions: recentStats.questions || 0,
          recent_correct_rate: Math.round((recentStats.accuracy || 0) * 100)
        };
      }

      this.setData({
        banners: Array.isArray(banners) ? banners : (banners.data || []),
        overview: processedOverview,
        dailyTask: { is_completed: false, completed_questions: 0, target_questions: 20 },
        subjects: [],
        announcements: Array.isArray(announcementRes) ? announcementRes : (announcementRes.data || []),
        accuracyBarColor: accuracyBarColor
      });
    } catch (err) {
      console.error('加载首页数据失败:', err);
    } finally {
      this.setData({ loading: false });
      wx.stopPullDownRefresh();
    }
  },

  onPullDownRefresh() {
    console.log('首页下拉刷新触发');
    
    // 显示刷新提示
    wx.showToast({
      title: '正在刷新...',
      icon: 'loading',
      duration: 1000
    });
    
    this.loadData().then(() => {
      console.log('首页数据刷新完成');
      
      // 显示刷新成功提示
      wx.showToast({
        title: '刷新成功',
        icon: 'success',
        duration: 1500
      });
    }).catch(err => {
      console.error('首页数据刷新失败:', err);
      
      // 显示刷新失败提示
      wx.showToast({
        title: '刷新失败，请重试',
        icon: 'none',
        duration: 2000
      });
    });
  },

  handleScan() {
    wx.navigateTo({
      url: '/pages/camera/index'
    });
  },

  onAnnouncementChange(e) {
    const { current, source } = e.detail;
    // 只有在自动滚动或用户手动触摸滑动时才更新索引
    if (source === 'autoplay' || source === 'touch') {
      this.setData({
        currentAnnouncementIndex: current
      });
    }
  },

  showCurrentAnnouncement() {
    const { announcements, currentAnnouncementIndex } = this.data;
    if (!announcements || announcements.length === 0) return;
    
    // 增加索引越界保护
    const safeIndex = currentAnnouncementIndex >= announcements.length ? 0 : currentAnnouncementIndex;
    const announcement = announcements[safeIndex];
    
    if (!announcement) {
      console.error('未找到对应公告:', safeIndex);
      return;
    }
    
    console.log('显示公告详情:', announcement);
    
    wx.showModal({
      title: announcement.title || '系统公告',
      content: announcement.content || '暂无详细内容',
      showCancel: false,
      confirmText: '我知道了',
      confirmColor: '#4A90E2'
    });
  },

  showAllAnnouncements() {
    if (this.data.announcements.length === 0) return;

    const list = this.data.announcements.map(a => `【${a.title}】\n${a.content || '暂无详细内容'}`).join('\n\n');

    wx.showModal({
      title: '系统公告',
      content: list,
      showCancel: false,
      confirmText: '我知道了',
      confirmColor: '#4A90E2'
    });
  },

  onBannerChange(e) {
    this.setData({
      currentBannerIndex: e.detail.current
    });
  },

  handleBannerTap(e) {
    const { item } = e.currentTarget.dataset;
    if (!item) return;

    // link_type 为 none 或 link_url 为空时不跳转
    if (!item.link_type || item.link_type === 'none' || !item.link_url) {
      return;
    }

    // 处理轮播图点击跳转
    if (item.link_type === 'url') {
      // 外部链接，使用 webview 打开
      wx.navigateTo({
        url: `/pages/webview/index?url=${encodeURIComponent(item.link_url)}`
      });
    } else if (item.link_type === 'page') {
      // 内部页面
      if (item.link_url.startsWith('/pages')) {
        wx.navigateTo({ url: item.link_url });
      } else if (item.link_url.startsWith('/')) {
        wx.navigateTo({ url: item.link_url });
      }
    } else if (item.link_type === 'mini_program') {
      // 跳转到其他小程序
      if (item.app_id && item.link_url) {
        wx.navigateToMiniProgram({
          appId: item.app_id,
          path: item.link_url
        });
      }
    }
  },

});
