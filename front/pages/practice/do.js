const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const markdown = require('../../utils/markdown.js');

Page({
  data: {
    currentIndex: 0,
    questions: [],
    timeString: '00:00:00',
    seconds: 0,
    timer: null,
    showCard: false,
    showResult: false,
    loading: true,
    submitting: false
  },

  onLoad(options) {
    const eventChannel = this.getOpenerEventChannel();
    // 监听 acceptDataFromOpenerPage 事件，获取上一页面通过 eventChannel 传送到当前页面的数据
    eventChannel.on('acceptDataFromOpenerPage', (data) => {
      if (data && data.questions) {
        this.initQuestions(data.questions);
      }
    });
  },

  onUnload() {
    this.stopTimer();
  },

  initQuestions(rawQuestions) {
    // 处理题目数据，添加选中状态
    const questions = rawQuestions.map(q => {
      // 规范化题型
      let type = 'unknown';
      let content = q.content;
      let options = q.options || [];

      if (q.question_type === '选择题') {
        type = 'single'; // 默认为单选
        
        // 如果没有选项，尝试从题目内容中解析
        if (!options || options.length === 0) {
          const parsed = this.parseOptions(content);
          if (parsed.options.length > 0) {
            options = parsed.options;
            content = parsed.content;
          }
        }
      }
      else if (q.question_type === '判断题') type = 'boolean';
      else if (q.question_type === '填空题') type = 'fill';
      
      // 如果是选择题但没有选项，且是单选，可能需要特殊处理，或者暂且留空
      // 如果是判断题，手动构造选项（如果为空）
      // let options = q.options || []; // Removed, defined above
      if (type === 'boolean' && options.length === 0) {
        // 判断题UI特殊处理，或者构造标准选项
      }

      return {
        ...q,
        content: content, // 使用可能被清洗过的内容
        renderedContent: markdown.parse(content || ''),
        type: type, // 内部使用的类型标识
        type_text: q.question_type || '未知题型',
        user_answer: '', // 用户答案
        is_correct: false,
        analysis: '',
        correct_answer: '',
        options: options.map(opt => ({
          ...opt,
          selected: false,
          renderedContent: markdown.parse(opt.content || '')
        }))
      };
    });

    this.setData({
      questions,
      loading: false
    });
    
    this.startTimer(0);
  },

  // 解析题目内容中的选项 (A. xxx B. xxx)
  parseOptions(content) {
    let options = [];
    let cleanContent = content;

    // 匹配模式：A. 或 A、 或 (A) 或 A．
    // 正则解释：
    // (?:^|\n|\s)  : 匹配行首、换行或空格（确保不是单词中间的A）
    // ([A-E])      : 捕获 A-E
    // [\.、．\s]   : 匹配分隔符（点、顿号、全角点、空格）
    const splitRegex = /(?:^|\n|\s)([A-E])[\.、．\s]/g;
    
    // 查找第一个匹配项（通常是 A.）
    const matchA = content.match(/(?:^|\n|\s)A[\.、．\s]/);
    
    if (matchA) {
      const startIdx = matchA.index;
      // 截取选项部分字符串（从A开始到结尾）
      const optionsStr = content.substring(startIdx);
      // 更新 content (去掉选项部分)
      cleanContent = content.substring(0, startIdx).trim();

      // 在 optionsStr 中查找所有选项
      let match;
      let found = [];
      while ((match = splitRegex.exec(optionsStr)) !== null) {
        // 过滤掉非预期顺序的匹配（简单起见，暂不过滤，假设AI输出格式较好）
        found.push({
          key: match[1],
          index: match.index,
          fullMatch: match[0]
        });
      }

      // 根据位置截取内容
      for (let i = 0; i < found.length; i++) {
        const current = found[i];
        const next = found[i+1];
        
        // 内容开始位置
        const contentStart = current.index + current.fullMatch.length;
        
        let optContent = '';
        if (next) {
          optContent = optionsStr.substring(contentStart, next.index);
        } else {
          optContent = optionsStr.substring(contentStart);
        }
        
        options.push({
          key: current.key,
          content: optContent.trim()
        });
      }
    }

    return { options, content: cleanContent };
  },

  getTypeText(type) {
    // 这里的 type 已经是中文或者我们在 initQuestions 里处理过的了
    // 实际上我们在 initQuestions 直接使用了 q.question_type
    return type;
  },

  startTimer(initialSeconds = 0) {
    this.setData({ seconds: initialSeconds });
    this.formatTime(initialSeconds);
    
    this.data.timer = setInterval(() => {
      const seconds = this.data.seconds + 1;
      this.setData({ seconds });
      this.formatTime(seconds);
    }, 1000);
  },

  stopTimer() {
    if (this.data.timer) {
      clearInterval(this.data.timer);
      this.data.timer = null;
    }
  },

  formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    
    const pad = n => n < 10 ? `0${n}` : n;
    this.setData({
      timeString: `${pad(h)}:${pad(m)}:${pad(s)}`
    });
  },

  onSwiperChange(e) {
    if (e.detail.source === 'touch' || e.detail.source === 'autoplay') {
      this.setData({ currentIndex: e.detail.current });
    }
  },

  prevQuestion() {
    if (this.data.currentIndex > 0) {
      this.setData({ currentIndex: this.data.currentIndex - 1 });
    }
  },

  nextOrSubmit() {
    if (this.data.currentIndex < this.data.questions.length - 1) {
      this.setData({ currentIndex: this.data.currentIndex + 1 });
    } else {
      this.submitAll();
    }
  },

  // 填空题输入
  onInputAnswer(e) {
    if (this.data.showResult) return;
    const { qidx } = e.currentTarget.dataset;
    const value = e.detail.value;
    
    this.setData({
      [`questions[${qidx}].user_answer`]: value
    });
  },

  // 判断题选择
  selectBoolean(e) {
    if (this.data.showResult) return;
    const { qidx, value } = e.currentTarget.dataset;
    const questions = this.data.questions;
    const question = questions[qidx];
    
    // 如果已经选了，再次点击同一个取消？或者直接覆盖。这里直接覆盖。
    this.setData({
      [`questions[${qidx}].user_answer`]: value
    });
    
    // 自动下一题
    if (this.data.currentIndex < this.data.questions.length - 1) {
       setTimeout(() => {
         this.setData({ currentIndex: this.data.currentIndex + 1 });
       }, 300);
    }
  },

  selectOption(e) {
    if (this.data.showResult) return; // 已提交不可修改

    const { qidx, oidx } = e.currentTarget.dataset;
    const questions = this.data.questions;
    const question = questions[qidx];
    const option = question.options[oidx];

    if (question.type === 'single' || question.type === 'boolean') {
      // 单选/判断：互斥
      question.options.forEach((opt, idx) => {
        opt.selected = idx === oidx;
      });
      question.user_answer = option.key;
    } else if (question.type === 'multiple') {
      // 多选
      option.selected = !option.selected;
      // 收集所有选中的key，排序
      const selectedKeys = question.options
        .filter(opt => opt.selected)
        .map(opt => opt.key)
        .sort();
      question.user_answer = selectedKeys.join('');
    }

    this.setData({
      [`questions[${qidx}]`]: question
    });
    
    // 自动下一题（仅单选/判断）
    if ((question.type === 'single' || question.type === 'boolean') && this.data.currentIndex < this.data.questions.length - 1) {
       setTimeout(() => {
         this.setData({ currentIndex: this.data.currentIndex + 1 });
       }, 300);
    }
  },

  async submitAll() {
    const that = this;
    wx.showModal({
      title: '提示',
      content: '确认提交试卷吗？',
      success: async (res) => {
        if (res.confirm) {
          that.doSubmit();
        }
      }
    });
  },

  async doSubmit() {
    this.setData({ submitting: true });
    wx.showLoading({ title: '判卷中...' });
    this.stopTimer();

    const questions = this.data.questions;
    const promises = questions.map(q => {
      // 如果没有作答，也需要校验（获取正确答案）
      const answer = q.user_answer || ''; 
      // 注意：这里可能需要根据后端要求处理空答案，假设后端接受空字符串
      
      return request.post(api.practice.answer(q.id), { answer })
        .then(res => ({
          id: q.id,
          is_correct: res.is_correct,
          correct_answer: res.correct_answer,
          analysis: res.analysis
        }))
        .catch(err => ({
          id: q.id,
          error: true
        }));
    });

    try {
      const results = await Promise.all(promises);
      
      // 更新题目状态
      const newQuestions = questions.map(q => {
        const result = results.find(r => r.id === q.id);
        if (result && !result.error) {
          return {
            ...q,
            is_correct: result.is_correct,
            correct_answer: result.correct_answer,
            analysis: result.analysis,
            renderedAnalysis: markdown.parse(result.analysis || '暂无解析')
          };
        }
        return q;
      });

      this.setData({
        questions: newQuestions,
        showResult: true,
        submitting: false
      });
      
      wx.hideLoading();
      
      // 计算分数等（可选）
      const correctCount = newQuestions.filter(q => q.is_correct).length;
      wx.showToast({
        title: `得分: ${correctCount} / ${newQuestions.length}`,
        icon: 'none',
        duration: 3000
      });

    } catch (err) {
      console.error('提交失败', err);
      wx.hideLoading();
      wx.showToast({ title: '提交出错，请重试', icon: 'none' });
      this.setData({ submitting: false });
    }
  },

  toggleCard() {
    this.setData({ showCard: !this.data.showCard });
  },
  
  stopProp() {},

  jumpToQuestion(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({ 
      currentIndex: index,
      showCard: false 
    });
  },

  goBack() {
    wx.navigateBack();
  }
});
