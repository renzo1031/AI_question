const config = require('../../../utils/config.js');
const api = require('../../../utils/api.js');
const { post } = require('../../../utils/request.js');
const markdown = require('../../../utils/markdown.js');

Page({
  data: {
    result: null,
    loading: true,
    imagePath: '',
    subjectText: '',
    typeText: '',
    difficultyText: '',
    difficultyClass: '',
    metaLine: '',
    analysisExpanded: false,
    statusBarHeight: 0,
    navHeight: 0,
    tab: 'analysis',
    showCorrectionModal: false,
    correctionReason: '',
    submittingCorrection: false,
    renderedQuestion: '',
    renderedAnswer: '',
    renderedAnalysis: ''
  },

  onLoad(options) {
    const sysInfo = wx.getWindowInfo();
    const statusBarHeight = sysInfo.statusBarHeight || 0;
    const navHeight = statusBarHeight + 44;
    this.setData({ statusBarHeight, navHeight });

    const imagePath = wx.getStorageSync('searchImagePath');
    const result = wx.getStorageSync('searchResult');

    if (options.from === 'camera' && imagePath && !result) {
      // 从拍照页跳转过来，且有图片但无结果，说明需要进行搜题
      this.setData({ imagePath, loading: true });
      this.processImage(imagePath);
    } else if (result) {
      // 已经有结果（可能是历史记录或已经搜完）
      this.renderResult(result, imagePath);
    } else {
      wx.showToast({
        title: '未找到搜题结果',
        icon: 'none'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  // 处理图片（压缩 -> 上传并搜题）
  processImage(tempFilePath) {
    // 压缩图片
    wx.compressImage({
      src: tempFilePath,
      quality: 80,
      success: (res) => {
        this.uploadAndSearch(res.tempFilePath);
      },
      fail: () => {
        // 压缩失败则使用原图
        this.uploadAndSearch(tempFilePath);
      }
    });
  },

  uploadAndSearch(filePath) {
    // 获取 Token
    const token = wx.getStorageSync(config.tokenKey);
    const header = {};
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    // 上传文件
    wx.uploadFile({
      url: config.baseUrl + api.ai.search,
      filePath: filePath,
      name: 'file', // 后端接收文件的字段名
      header: header,
      formData: {}, 
      success: (res) => {
        console.log('上传结果', res);
        
        try {
          // wx.uploadFile 返回的 data 是字符串，需要 parse
          // 修复可能存在的编码问题 (UTF-8被误认为ISO-8859-1)
          let rawData = res.data;
          try {
            rawData = decodeURIComponent(escape(rawData));
          } catch (ignore) {
            // 如果已经是正确编码，escape后可能包含%u，decodeURIComponent会报错，此时忽略错误使用原字符串
          }

          const data = JSON.parse(rawData);
          
          if (res.statusCode >= 200 && res.statusCode < 300 && data.code === 0) {
            const resultData = data.data;
            // 获取原始图片路径（未压缩的）用于保存历史
            const originalPath = this.data.imagePath || filePath;
            
            this.persistHistory(resultData, originalPath, (savedPath) => {
              wx.setStorageSync('searchResult', resultData);
              if (savedPath) {
                 wx.setStorageSync('searchImagePath', savedPath);
                 this.setData({ imagePath: savedPath });
              }
              this.renderResult(resultData, savedPath || originalPath);
            });
          } else {
            console.error('搜题失败', data);
            this.handleError(data.message || '识别失败');
          }
        } catch (e) {
          console.error('解析响应失败', e);
          this.handleError('系统错误');
        }
      },
      fail: (err) => {
        console.error('上传失败', err);
        this.handleError('网络错误');
      }
    });
  },

  handleError(message) {
    this.setData({ loading: false });
    wx.showToast({ title: message, icon: 'none' });
    setTimeout(() => {
      wx.navigateBack();
    }, 1500);
  },

  persistHistory(resultData, tempImagePath, done) {
    const finish = (finalPath) => {
      const history = wx.getStorageSync('searchHistory') || [];
      const list = Array.isArray(history) ? history : [];
      const question = (resultData && resultData.question) || {};
      const record = {
        id: `${Date.now()}_${Math.floor(Math.random() * 1000)}`,
        ts: Date.now(),
        imagePath: finalPath || tempImagePath,
        questionContent: (question.content || '').slice(0, 60),
        subject: question.subject || '',
        type: question.question_type || '',
        difficulty: question.difficulty,
        result: resultData
      };

      const next = [record, ...list].filter((x) => x && x.result && x.imagePath);
      const max = 15;
      const removed = next.slice(max);
      const kept = next.slice(0, max);

      wx.setStorageSync('searchHistory', kept);
      
      removed.forEach((item) => {
        const p = item && item.imagePath;
        if (typeof p === 'string' && (p.startsWith('wxfile://') || p.startsWith('http://tmp/') || p.startsWith('https://tmp/'))) {
          wx.getFileSystemManager().removeSavedFile({
            filePath: p,
            fail: (err) => console.warn('删除历史文件失败', err)
          });
        }
      });

      done(finalPath);
    };

    wx.getFileSystemManager().saveFile({
      tempFilePath: tempImagePath,
      success: (res) => finish(res.savedFilePath),
      fail: (err) => {
        console.warn('保存文件失败', err);
        finish(tempImagePath);
      }
    });
  },

  renderResult(result, imagePath) {
    const question = result.question || {};
    const answer = result.answer || {};
    const subjectText = question.subject || '';
    const typeText = question.question_type || '';
    const difficultyLevel = typeof question.difficulty === 'number' ? question.difficulty : parseInt(question.difficulty, 10);
    const difficultyInfo = this.getDifficultyInfo(difficultyLevel);

    const metaParts = [];
    if (result.question_id !== undefined && result.question_id !== null) metaParts.push(`题目ID ${result.question_id}`);
    if (typeof result.saved === 'boolean') metaParts.push(result.saved ? '已入库' : '未入库');
    if (subjectText) metaParts.push(subjectText);
    if (typeText) metaParts.push(typeText);

    this.setData({
      result: result,
      loading: false,
      imagePath: imagePath || '',
      subjectText,
      typeText,
      difficultyText: difficultyInfo.text,
      difficultyClass: difficultyInfo.className,
      metaLine: metaParts.join(' · '),
      renderedQuestion: markdown.parse(question.content || ''),
      renderedAnswer: markdown.parse(answer.content || ''),
      renderedAnalysis: markdown.parse(answer.analysis || '')
    });
    
    // 如果是临时文件，可能已经在 onLoad 初始加载时被处理过，这里不再清除 searchImagePath，
    // 以便用户在当前页刷新时还能看到图片（虽然小程序Page没有刷新，但保持状态一致性较好）
  },

  getDifficultyInfo(level) {
    if (level >= 4) return { text: '困难', className: 'pill-hard' };
    if (level === 3) return { text: '中等', className: 'pill-medium' };
    return { text: '简单', className: 'pill-easy' };
  },

  goBack() {
    wx.navigateBack();
  },

  previewImage() {
    if (this.data.imagePath) {
      wx.previewImage({
        urls: [this.data.imagePath]
      });
    }
  },

  copyQuestion() {
    const text = this.data.result.question.content;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '题目已复制', icon: 'none' })
    });
  },

  copyAnswer() {
    const text = this.data.result.answer.content;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '答案已复制', icon: 'none' })
    });
  },

  switchTab(e) {
    this.setData({
      tab: e.currentTarget.dataset.tab
    });
  },

  goToCamera() {
    wx.redirectTo({
      url: '/pages/camera/index'
    });
  },

  openCorrectionModal() {
    this.setData({ showCorrectionModal: true });
  },

  closeCorrectionModal() {
    this.setData({ showCorrectionModal: false, correctionReason: '' });
  },

  stopProp() {},

  onReasonInput(e) {
    this.setData({ correctionReason: e.detail.value });
  },

  submitCorrection() {
    if (!this.data.correctionReason.trim()) {
      wx.showToast({ title: '请输入纠错内容', icon: 'none' });
      return;
    }

    this.setData({ submittingCorrection: true });

    post(api.ai.correction, {
      question_id: this.data.result.question_id,
      reason: this.data.correctionReason
    }).then(() => {
      wx.showToast({ title: '反馈成功', icon: 'success' });
      this.closeCorrectionModal();
    }).catch(err => {
      console.error(err);
      // request.js 已经处理了错误提示，这里只需要重置状态
    }).finally(() => {
      this.setData({ submittingCorrection: false });
    });
  }
});
