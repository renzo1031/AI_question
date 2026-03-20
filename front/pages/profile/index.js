const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const config = require('../../utils/config.js');

Page({
  data: {
    userInfo: null,
    stats: {
      question_count: 0,
      study_days: 0,
      accuracy: '0%'
    },
    points: 0,
    level: 1,
    navHeight: 0,
    statusBarHeight: 0
  },

  onLoad() {
    this.calcNavBarHeight();
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
    if (token) {
      this.getUserInfo();
    } else {
      this.setData({ userInfo: null });
    }
  },

  async getUserInfo() {
    try {
      const userRes = await request.get(api.user.me);
      
      if (userRes) {
        // 格式化加入时间
        let joinDate = '';
        if (userRes.created_at) {
          const date = new Date(userRes.created_at);
          const year = date.getFullYear();
          const month = (date.getMonth() + 1).toString().padStart(2, '0');
          const day = date.getDate().toString().padStart(2, '0');
          joinDate = `${year}-${month}-${day}`;
        }
        
        userRes.joinDate = joinDate;
        
        // 处理账号显示 (优先手机号，其次邮箱)
        userRes.displayAccount = userRes.phone || userRes.email || '';
      }

      // 获取学习统计数据
      const overviewData = await request.get(api.learning.overview, { time_window_days: 30 }).catch(err => {
        console.error('获取学习统计失败:', err);
        return null;
      });

      let stats = {
        question_count: 0,
        study_days: 0,
        accuracy: '0%'
      };

      if (overviewData) {
        const allTimeStats = overviewData.all_time_stats || {};
        const recentStats = overviewData.recent_stats || {};
        
        stats = {
          question_count: allTimeStats.questions || 0,
          study_days: overviewData.consecutive_days || 0,
          accuracy: allTimeStats.accuracy_formatted?.percentage || '0%'
        };
      }

      this.setData({
        userInfo: userRes || {},
        stats: stats
      });
    } catch (err) {
      console.error('获取用户信息失败', err);
      // 如果获取失败，可能是token过期，request.js会处理，或者只是网络问题
    }
  },

  goLogin() {
    wx.navigateTo({
      url: '/pages/auth/login'
    });
  },

  navigateTo(e) {
    const url = e.currentTarget.dataset.url;
    if (!this.data.userInfo) {
      this.goLogin();
      return;
    }
    wx.navigateTo({ url });
  },

  showTip() {
    wx.showToast({
      title: '功能开发中...',
      icon: 'none'
    });
  },

  async handleLogout() {
    const confirm = await wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      confirmText: '退出',
      confirmColor: '#FF4D4F'
    });

    if (confirm.confirm) {
      wx.showLoading({ title: '正在退出...' });
      try {
        await request.post(api.auth.logout);
      } catch (err) {
        console.error('退出登录请求失败:', err);
      } finally {
        // 无论接口是否成功，本地都清除状态并跳转
        wx.removeStorageSync(config.tokenKey);
        wx.removeStorageSync(config.refreshTokenKey);
        wx.removeStorageSync(config.userKey);
        
        this.setData({ userInfo: null });
        wx.hideLoading();
        
        wx.reLaunch({
          url: '/pages/auth/login'
        });
      }
    }
  }
});
