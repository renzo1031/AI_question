const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const KNOWLEDGE_DATA = require('../../utils/knowledge_data.js');
const markdown = require('../../utils/markdown.js');

Page({
  data: {
    list: [],
    total: 0,
    page: 1,
    pageSize: 10,
    hasMore: true,
    loadingMore: false,
    isRefreshing: false,
    keyword: '',
    navHeight: 0,
    statusBarHeight: 0,
    
    // 筛选数据
    grades: [],
    subjects: [],
    chapters: [],
    difficulties: ['全部', '入门 (1-2)', '基础 (3)', '进阶 (4)', '困难 (5)'],
    subjectIcons: {
      '语文': '📚',
      '数学': '📐',
      '英语': '🔤',
      '物理': '🧪',
      '化学': '⚗️',
      '生物': '🍃',
      '历史': '🏺',
      '地理': '🌍',
      '政治': '⚖️',
      '全部': '🔍'
    },
    
    // 选中状态 (索引)
    gradeIndex: 0,
    subjectIndex: 0,
    chapterIndex: 0,
    difficultyIndex: 0,
    
    // 实际选中的值
    filterGrade: '',
    filterSubject: '',
    filterChapter: '',
    filterDifficulty: null,
    
    // 页面滚动状态
    isScrolled: false
  },

  // 页面滚动监听
  onPageScroll(e) {
    const scrollTop = e.scrollTop;
    if (scrollTop > 20 && !this.data.isScrolled) {
      this.setData({ isScrolled: true });
    } else if (scrollTop <= 20 && this.data.isScrolled) {
      this.setData({ isScrolled: false });
    }
  },

  onLoad() {
    this.calcNavBarHeight();
    this.initFilters();
    this.loadList();
  },

  calcNavBarHeight() {
    const systemInfo = wx.getWindowInfo();
    const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
    const navBarHeight = (menuButtonInfo.top - systemInfo.statusBarHeight) * 2 + menuButtonInfo.height;
    const totalHeaderHeight = systemInfo.statusBarHeight + navBarHeight;
    
    this.setData({
      navHeight: totalHeaderHeight,
      statusBarHeight: systemInfo.statusBarHeight
    });
  },

  initFilters() {
    const grades = ['全部', ...Object.keys(KNOWLEDGE_DATA)];
    this.setData({
      grades,
      subjects: ['全部'],
      chapters: ['全部']
    });
  },

  // 年级选择 (点击)
  onGradeSelect(e) {
    const index = e.currentTarget.dataset.index;
    const grade = this.data.grades[index];
    
    let subjects = ['全部'];
    if (index > 0 && KNOWLEDGE_DATA[grade]) {
      subjects = ['全部', ...Object.keys(KNOWLEDGE_DATA[grade])];
    }

    this.setData({
      gradeIndex: index,
      filterGrade: index === 0 ? '' : grade,
      subjects,
      subjectIndex: 0,
      filterSubject: '',
      chapters: ['全部'],
      chapterIndex: 0,
      filterChapter: ''
    });
    
    this.refreshData();
  },

  // 学科选择 (点击)
  onSubjectSelect(e) {
    const index = e.currentTarget.dataset.index;
    const subject = this.data.subjects[index];
    const grade = this.data.filterGrade;
    
    let chapters = ['全部'];
    if (index > 0 && grade && KNOWLEDGE_DATA[grade] && KNOWLEDGE_DATA[grade][subject]) {
      chapters = ['全部', ...KNOWLEDGE_DATA[grade][subject]];
    }

    this.setData({
      subjectIndex: index,
      filterSubject: index === 0 ? '' : subject,
      chapters,
      chapterIndex: 0,
      filterChapter: ''
    });
    
    this.refreshData();
  },

  // 年级改变 (Picker保留，以防万一)
  onGradeChange(e) {
    const index = e.detail.value;
    this.onGradeSelect({ currentTarget: { dataset: { index } } });
  },

  // 学科改变 (Picker保留)
  onSubjectChange(e) {
    const index = e.detail.value;
    this.onSubjectSelect({ currentTarget: { dataset: { index } } });
  },

  // 章节改变
  onChapterChange(e) {
    const index = e.detail.value;
    const chapter = this.data.chapters[index];
    
    this.setData({
      chapterIndex: index,
      filterChapter: index === 0 ? '' : chapter
    });
    
    this.refreshData();
  },

  // 难度改变
  onDifficultyChange(e) {
    const index = e.detail.value;
    // 映射: 0->null, 1->1, 2->3, 3->4, 4->5 (简化处理，或者传具体值)
    // 实际上API可能支持 range 或者 exact。这里假设传 level
    let diff = null;
    if (index === 1) diff = 1;
    if (index === 2) diff = 3;
    if (index === 3) diff = 4;
    if (index === 4) diff = 5;

    this.setData({
      difficultyIndex: index,
      filterDifficulty: diff
    });
    
    this.refreshData();
  },

  onShow() {
    // 每次显示不强制刷新，除非有标记
  },

  async refreshData() {
    this.setData({ page: 1, hasMore: true });
    await this.loadList();
  },

  // 页面下拉刷新
  async onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true });
    await this.loadList();
    wx.stopPullDownRefresh();
  },

  // 页面上拉触底
  onReachBottom() {
    this.loadMore();
  },

  async loadList() {
    try {
      const { page, pageSize, keyword, filterGrade, filterSubject, filterChapter, filterDifficulty } = this.data;
      
      const params = {
        page,
        page_size: pageSize,
        keyword
      };
      
      if (filterGrade) params.grade = filterGrade;
      if (filterSubject) params.subject = filterSubject;
      if (filterChapter) params.chapter = filterChapter;
      if (filterDifficulty) params.difficulty = filterDifficulty;

      const res = await request.get(api.wrongBook.list, params);

      // 兼容处理：判断返回的是完整对象还是纯数组
      let resList = [];
      let total = 0;

      if (res && res.data && Array.isArray(res.data)) {
        resList = res.data;
        total = res.page_info ? res.page_info.total : resList.length;
      } else if (Array.isArray(res)) {
        resList = res;
        total = res.length;
      }

      // 处理列表数据，格式化时间等
      const formattedList = resList.map(item => {
        // 处理时间显示
        let timeStr = '';
        if (item.last_answer_at) {
          const date = new Date(item.last_answer_at);
          timeStr = `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
        }
        
        return {
          ...item,
          displayTime: timeStr,
          renderedContent: markdown.parse((item.question && item.question.content) || '')
        };
      });

      const newList = page === 1 ? formattedList : this.data.list.concat(formattedList);
      
      this.setData({
        list: newList,
        total: total,
        hasMore: newList.length < total,
        loadingMore: false
      });
    } catch (err) {
      console.error('加载错题列表失败', err);
      this.setData({ loadingMore: false, isRefreshing: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  onRefresh() {
    this.refreshData();
  },

  loadMore() {
    if (!this.data.hasMore || this.data.loadingMore) return;
    this.setData({
      page: this.data.page + 1,
      loadingMore: true
    });
    this.loadList();
  },

  onSearch(e) {
    this.setData({
      keyword: e.detail.value
    });
    this.refreshData();
  },

  // 切换到练习页
  switchToPractice() {
    wx.switchTab({
      url: '/pages/practice/index'
    });
  },

  // 生成错题练习
  async generatePractice() {
    if (this.data.list.length === 0) {
      wx.showToast({ title: '当前没有错题可练', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '生成练习中...' });
    try {
      const { filterGrade, filterSubject, filterChapter, filterDifficulty } = this.data;
      
      // 构造请求参数
      const params = {
        count: 10,
        subject: filterSubject || '数学' // API要求必填Subject，如果没有选，可能需要提示或者默认
      };

      if (!filterSubject) {
        // 如果没选学科，尝试取列表第一个的学科，或者提示用户
        if (this.data.list.length > 0 && this.data.list[0].subject_name) {
          params.subject = this.data.list[0].subject_name;
        } else {
           wx.hideLoading();
           wx.showToast({ title: '请先选择一个学科', icon: 'none' });
           return;
        }
      }

      if (filterGrade) params.grade = filterGrade;
      if (filterChapter) params.chapter = filterChapter;
      if (filterDifficulty) params.difficulty = filterDifficulty;

      const res = await request.post(api.wrongBook.practice, params);
      
      wx.hideLoading();

      if (res && res.length > 0) {
        wx.navigateTo({
          url: '/pages/practice/do',
          success: (res2) => {
            res2.eventChannel.emit('acceptDataFromOpenerPage', {
              questions: res
            });
          }
        });
      } else {
        wx.showToast({ title: '没有生成相关题目', icon: 'none' });
      }

    } catch (err) {
      console.error(err);
      wx.hideLoading();
      wx.showToast({ title: '生成失败', icon: 'none' });
    }
  },

  viewDetail(e) {
    const id = e.currentTarget.dataset.id;
    const mistake = this.data.list.find(item => item.question.id === id);
    
    if (mistake) {
      wx.navigateTo({
        url: '/pages/mistake/detail/detail',
        success: (res) => {
          res.eventChannel.emit('acceptDataFromOpenerPage', {
            mistake: mistake
          });
        }
      });
    }
  }
});
