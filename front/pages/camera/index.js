const config = require('../../utils/config.js');
const api = require('../../utils/api.js');

Page({
  data: {
    navHeight: 0,
    flashMode: 'off',
    devicePosition: 'back',
    historyList: []
  },

  onLoad() {
    // 获取导航栏高度适配
    const sysInfo = wx.getWindowInfo();
    this.setData({
      navHeight: sysInfo.statusBarHeight
    });
    
    // 创建相机上下文
    this.ctx = wx.createCameraContext();

    this.loadHistory();
  },

  onShow() {
    this.loadHistory();
    if (wx.getStorageSync('search_pending')) {
      wx.removeStorageSync('search_pending');
      wx.redirectTo({
        url: '/pages/ai/search-result/index?from=camera'
      });
    }
  },

  loadHistory() {
    const history = wx.getStorageSync('searchHistory') || [];
    if (Array.isArray(history)) {
      this.setData({
        historyList: history.slice(0, 5) // 只显示最近5条
      });
    }
  },

  openHistory(e) {
    const index = e.currentTarget.dataset.index;
    const item = this.data.historyList[index];
    if (item && item.result) {
      wx.setStorageSync('searchResult', item.result);
      wx.setStorageSync('searchImagePath', item.imagePath);
      wx.navigateTo({
        url: '/pages/ai/search-result/index'
      });
    }
  },

  clearHistory() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空搜题历史吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('searchHistory');
          this.setData({ historyList: [] });
          
          // 清理本地文件（可选）
          // 实际项目中建议定期清理或使用 LRU 策略
        }
      }
    });
  },

  handleBack() {
    wx.navigateBack();
  },

  toggleFlash() {
    this.setData({
      flashMode: this.data.flashMode === 'on' ? 'off' : 'on'
    });
  },

  // 拍照
  takePhoto() {
    this.ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        const tempFilePath = res.tempImagePath;
        this.doCrop(tempFilePath);
      },
      fail: (err) => {
        console.error('拍照失败', err);
        wx.showToast({ title: '拍照失败', icon: 'none' });
      }
    });
  },

  // 从相册选择
  chooseFromAlbum() {
    wx.chooseImage({
      count: 1,
      sizeType: ['original'],
      sourceType: ['album'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0];
        this.doCrop(tempFilePath);
      }
    });
  },

  // 裁剪图片
  doCrop(src) {
    wx.navigateTo({
      url: `/pages/camera/crop/index?src=${encodeURIComponent(src)}`
    });
  },

  error(e) {
    console.log(e.detail);
    if (e.detail.errMsg.includes('auth')) {
      wx.showModal({
        title: '权限提示',
        content: '需要相机权限才能拍照搜题',
        confirmText: '去设置',
        success: (res) => {
          if (res.confirm) {
            wx.openSetting();
          } else {
            wx.navigateBack();
          }
        }
      });
    }
  }
});
