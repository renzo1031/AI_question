const request = require('../../utils/request.js');
const api = require('../../utils/api.js');

Page({
  data: {
    subjectId: '',
    subject: null,
    knowledgeTree: []
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ subjectId: options.id });
      this.loadData(options.id);
    } else {
      wx.showToast({ title: '参数错误', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
    }
  },

  async loadData(id) {
    wx.showLoading({ title: '加载中' });
    try {
      // 这里的接口是假设的，需要确认 api.js 中的定义
      // 假设 detail 返回学科基本信息，knowledgeTree 返回树结构
      const [subjectRes, treeRes] = await Promise.all([
        request.get(api.subject.detail(id)),
        request.get(api.subject.knowledgeTree(id))
      ]);

      // 处理树结构，添加 expanded 属性
      const knowledgeTree = (treeRes.list || []).map(chapter => ({
        ...chapter,
        expanded: false, // 默认折叠
        children: (chapter.children || []).map(point => ({
          ...point,
          mastery: point.mastery || 0
        }))
      }));

      this.setData({
        subject: subjectRes,
        knowledgeTree
      });
    } catch (err) {
      console.error('加载学科详情失败', err);
      // wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  toggleChapter(e) {
    const index = e.currentTarget.dataset.index;
    const key = `knowledgeTree[${index}].expanded`;
    this.setData({
      [key]: !this.data.knowledgeTree[index].expanded
    });
  },

  async startSubjectPractice() {
    this.createPractice({
      subject_id: this.data.subjectId,
      title: `${this.data.subject.name} - 综合练习`
    });
  },

  startPointPractice(e) {
    const { id, name } = e.currentTarget.dataset;
    this.createPractice({
      knowledge_point_id: id,
      title: `${name} - 专项练习`
    });
  },

  async createPractice(params) {
    wx.showLoading({ title: '创建练习中' });
    try {
      const res = await request.post(api.practice.create, {
        count: 10,
        ...params
      });
      
      if (res.id) {
        wx.navigateTo({
          url: `/pages/practice/do?id=${res.id}`
        });
      }
    } catch (err) {
      wx.showToast({ title: '创建失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  }
});
