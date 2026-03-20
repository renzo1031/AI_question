const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const KNOWLEDGE_DATA = require('../../utils/knowledge_data.js');

const GRADES = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三'];
const SUBJECTS = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治'];
const SUBJECT_ICONS = {
  '语文': '📖', '数学': '📐', '英语': '🔤', 
  '物理': '⚡', '化学': '🧪', '生物': '🧬', 
  '历史': '🏺', '地理': '🌍', '政治': '⚖️'
};
const DIFFICULTY_DESC = ['入门', '基础', '进阶', '困难', '挑战'];
// 难度映射：10级制 -> 5级描述
// 1-2: 入门, 3-4: 基础, 5-6: 进阶, 7-8: 困难, 9-10: 挑战
const getDifficultyDesc = (level) => {
  if (level <= 2) return '入门';
  if (level <= 4) return '基础';
  if (level <= 6) return '进阶';
  if (level <= 8) return '困难';
  return '挑战';
};

// 年级名称映射（前端显示 -> 数据Key）
const GRADE_KEY_MAP = {
  '初一': '七年级',
  '初二': '八年级',
  '初三': '九年级'
};

Page({
  data: {
    navBarHeight: 0,
    
    // 选项数据
    grades: GRADES,
    subjects: [], // 动态生成
    subjectIcons: SUBJECT_ICONS,
    subjectDescs: {
      '语文': '提升阅读理解和写作能力',
      '数学': '培养逻辑思维和计算能力',
      '英语': '增强语言表达和交流能力',
      '物理': '探索自然规律和科学原理',
      '化学': '了解物质变化和化学反应',
      '生物': '认识生命现象和生物世界',
      '历史': '学习人类文明发展历程',
      '地理': '掌握地理知识和环境意识',
      '政治': '培养公民意识和社会责任感'
    },
    knowledgePoints: [], // 根据年级和学科动态变化
    questionTypes: ['任意', '选择题', '填空题', '判断题'],
    difficultyDesc: '基础',
    
    // 选中状态索引
    gradeIndex: 0, // 默认选中一年级
    subjectIndex: 0, // 默认选中第一个学科
    kpIndex: -1,
    qtIndex: 0,
    
    // 其他设置
    count: 10,
    difficulty: 3, // 默认为 3 (基础)
    
    // 新增数据
    totalQuestions: 156,
    accuracyRate: 85,
    streakDays: 7,
    recommendation: '根据你的学习进度，建议重点练习数学函数和几何图形相关题目，这将有助于提升你的逻辑思维能力。',
    
    // 加载状态
    loading: false,
    isScrolled: false,
    loading: false,
    isScrolled: false
  },

  onLoad(options) {
    this.calcNavBarHeight();
    
    // 初始化默认数据
    this.updateSubjects();
  },

  onPageScroll(e) {
    const scrollTop = e.scrollTop;
    const isScrolled = scrollTop > 10;
    if (isScrolled !== this.data.isScrolled) {
      this.setData({ isScrolled });
    }
  },

  onShow() {
    // 页面显示时不需要额外操作
  },

  calcNavBarHeight() {
    const systemInfo = wx.getWindowInfo();
    const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
    const navBarHeight = (menuButtonInfo.top - systemInfo.statusBarHeight) * 2 + menuButtonInfo.height + systemInfo.statusBarHeight;
    this.setData({
      navBarHeight: navBarHeight
    });
  },

  // 选择年级（点击标签）
  onGradeSelect(e) {
    const index = e.currentTarget.dataset.index;
    if (index === this.data.gradeIndex) return;
    
    this.setData({ 
      gradeIndex: index
    }, () => {
      this.updateSubjects();
    });
  },

  // 选择学科（点击网格）
  onSubjectSelect(e) {
    const index = e.currentTarget.dataset.index;
    if (index === this.data.subjectIndex) return;
    
    this.setData({ 
      subjectIndex: index,
      kpIndex: -1 // 重置章节选择
    }, () => {
      this.updateKnowledgePoints();
    });
  },

  // 选择章节（Picker）
  onKpChange(e) {
    this.setData({ kpIndex: parseInt(e.detail.value) });
  },
  
  // 选择题型（点击标签）
  onQtSelect(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({ qtIndex: index });
  },

  // 调整难度（Slider）
  onDifficultyChange(e) {
    const val = e.detail.value;
    this.setData({ 
      difficulty: val,
      difficultyDesc: getDifficultyDesc(val)
    });
  },

  // 调整题目数量（Stepper）
  onCountChange(e) {
    const type = e.currentTarget.dataset.type;
    let newCount = this.data.count;
    if (type === 'minus' && newCount > 5) {
      newCount -= 5;
    } else if (type === 'add' && newCount < 50) {
      newCount += 5;
    }
    this.setData({ count: newCount });
  },

  // 更新学科列表
  updateSubjects() {
    const { grades, gradeIndex } = this.data;
    const selectedGrade = grades[gradeIndex];
    // 映射年级名称到数据Key
    const dataKey = GRADE_KEY_MAP[selectedGrade] || selectedGrade;
    
    // 获取该年级下的所有学科
    const gradeData = KNOWLEDGE_DATA[dataKey] || {};
    let subjects = Object.keys(gradeData);
    
    // 确保有默认学科（防止空数据）
    if (subjects.length === 0) {
      subjects = ['语文', '数学']; // 默认显示语数
    }
    
    // 默认选中第一个学科
    this.setData({
      subjects: subjects,
      subjectIndex: 0,
      kpIndex: -1
    }, () => {
      this.updateKnowledgePoints();
    });
  },

  // 更新章节数据
  updateKnowledgePoints() {
    const { grades, subjects, gradeIndex, subjectIndex } = this.data;
    if (gradeIndex < 0 || subjectIndex < 0) return;

    const selectedGrade = grades[gradeIndex];
    // 映射年级名称到数据Key
    const dataKey = GRADE_KEY_MAP[selectedGrade] || selectedGrade;
    const subject = subjects[subjectIndex];
    
    // 获取章节数据
    const gradeData = KNOWLEDGE_DATA[dataKey] || {};
    const chapters = gradeData[subject] || [];
    
    this.setData({
      knowledgePoints: chapters
    });
  },
  
  // startPractice 保留原样，但不需要再次检查 index < 0，因为有默认值
  async startPractice() {
    const { grades, subjects, knowledgePoints, questionTypes, gradeIndex, subjectIndex, kpIndex, qtIndex, count, difficulty } = this.data;

    if (gradeIndex < 0) {
      wx.showToast({ title: '请选择年级', icon: 'none' });
      return;
    }
    if (subjectIndex < 0) {
      wx.showToast({ title: '请选择学科', icon: 'none' });
      return;
    }
    
    const selectedGrade = grades[gradeIndex];
    const selectedSubject = subjects[subjectIndex];
    const selectedKp = kpIndex >= 0 ? knowledgePoints[kpIndex] : null;
    const selectedQt = qtIndex > 0 ? questionTypes[qtIndex] : null; // 0 is '任意'

    wx.showLoading({ title: '生成题目中...' });
    
    try {
      const payload = {
        subject: selectedSubject,
        grade: selectedGrade,
        chapter: selectedKp, // 选中的章节
        knowledge_point: null,
        question_type: selectedQt,
        count: count,
        difficulty: difficulty
      };

      console.log('Generating practice with:', payload);

      const questions = await request.post(api.practice.generate, payload);
      
      wx.hideLoading();
      
      if (questions && questions.length > 0) {
        wx.navigateTo({
          url: '/pages/practice/do',
          success: (res) => {
            res.eventChannel.emit('acceptDataFromOpenerPage', { questions });
          }
        });
      } else {
         wx.showToast({
          title: '未生成题目',
          icon: 'none'
        });
      }
    } catch (err) {
      wx.hideLoading();
      console.error(err);
      wx.showToast({
        title: '生成失败，请重试',
        icon: 'none'
      });
    }
  },

  onPullDownRefresh() {
    wx.stopPullDownRefresh();
  },

  continuePractice(e) {
    wx.showToast({
      title: '暂不支持继续练习',
      icon: 'none'
    });
  },

  // 新增方法 - 应用AI推荐
  applyRecommendation() {
    const { recommendation } = this.data;
    
    // 根据推荐内容智能设置参数
    if (recommendation.includes('数学')) {
      const mathIndex = this.data.subjects.findIndex(s => s === '数学');
      if (mathIndex >= 0) {
        this.setData({ subjectIndex: mathIndex });
        this.updateKnowledgePoints();
      }
    }
    
    if (recommendation.includes('函数') || recommendation.includes('几何')) {
      this.setData({ difficulty: 5 }); // 设置为进阶难度
      this.setData({ difficultyDesc: getDifficultyDesc(5) });
    }
    
    wx.showToast({ title: '已应用AI推荐', icon: 'success' });
  },

  // 新增方法 - 跳过推荐
  skipRecommendation() {
    wx.showToast({ title: '已跳过推荐', icon: 'none' });
  },

  // 新增方法 - 快速设置
  usePresetSettings() {
    // 智能推荐设置
    this.setData({
      difficulty: 4,
      difficultyDesc: getDifficultyDesc(4),
      count: 15,
      qtIndex: 0 // 任意题型
    });
    
    wx.showToast({ title: '已应用快速设置', icon: 'success' });
  },

  // 新增方法 - 快速复习
  quickReview() {
    wx.navigateTo({
      url: '/pages/practice/do?mode=review'
    });
  },

  // 新增方法 - 查看练习记录
  viewHistory() {
    wx.navigateTo({
      url: '/pages/practice/history'
    });
  },

  // 新增方法 - 页面滚动监听
  onPageScroll(e) {
    const scrollTop = e.scrollTop;
    const isScrolled = scrollTop > 50;
    
    if (this.data.isScrolled !== isScrolled) {
      this.setData({ isScrolled });
    }
  },

  // 新增方法 - 更新统计数据
  async updateStats() {
    try {
      // 这里可以调用API获取真实数据
      const stats = await request.get(api.practice.stats);
      
      if (stats) {
        this.setData({
          totalQuestions: stats.total || 0,
          accuracyRate: stats.accuracy || 0,
          streakDays: stats.streak || 0
        });
      }
    } catch (error) {
      console.log('获取统计数据失败:', error);
    }
  },

  // 新增方法 - 获取AI推荐
  async getAIRecommendation() {
    try {
      const { subjects, subjectIndex, grades, gradeIndex } = this.data;
      
      const payload = {
        subject: subjects[subjectIndex],
        grade: grades[gradeIndex]
      };
      
      const recommendation = await request.post(api.practice.recommendation, payload);
      
      if (recommendation) {
        this.setData({ recommendation: recommendation.content });
      }
    } catch (error) {
      console.log('获取AI推荐失败:', error);
    }
  }
});
