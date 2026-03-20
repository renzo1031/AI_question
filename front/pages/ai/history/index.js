const request = require('../../../utils/request.js');
const api = require('../../../utils/api.js');
const util = require('../../../utils/util.js');

Page({
  data: {
    conversations: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onShow() {
    this.setData({
      conversations: [],
      page: 1,
      hasMore: true
    });
    this.loadData();
  },

  async loadData() {
    if (this.data.loading || !this.data.hasMore) return;

    this.setData({ loading: true });

    try {
      const res = await request.get(api.ai.conversations, {
        page: this.data.page,
        page_size: this.data.pageSize
      });

      const list = res.items || [];
      
      // 格式化时间
      list.forEach(item => {
        if (item.updated_at) {
          item.updated_at_formatted = util.formatTime(new Date(item.updated_at));
        } else {
          item.updated_at_formatted = '';
        }
      });

      this.setData({
        conversations: this.data.conversations.concat(list),
        page: this.data.page + 1,
        hasMore: list.length === this.data.pageSize
      });
    } catch (err) {
      console.error('加载历史记录失败', err);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  onReachBottom() {
    this.loadData();
  },

  goToChat(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/ai/chat?conversation_id=${id}`
    });
  }
});
