const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const config = require('../../utils/config.js');
const markdown = require('../../utils/markdown.js');

Page({
  data: {
    messages: [],
    inputValue: '',
    loading: false,
    userInfo: null,
    scrollIntoView: '',
    conversationId: null,
    
    // AI 服务商
    providers: [],
    currentProvider: null,
    
    // 具体的模型
    allModelOptions: [], // [{ id, name, providerId, providerName }]
    currentModel: null,
    currentModelName: '',

    // UI状态
    showTools: false,
    
    // 当前上下文的 question_id，用于 hint/similar
    currentQuestionId: null
  },

  onLoad(options) {
    this.initUser();
    this.loadProviders();
    
    // 欢迎语
    this.addMessage('ai', '你好呀！我是你的AI学习助手。我可以帮你解题，或者讲解知识点。');

    // 处理传入参数
    if (options.conversation_id) {
      this.setData({ conversationId: options.conversation_id });
      this.loadHistory(options.conversation_id);
    } else if (options.question_id) {
      // 从题目详情页进来
      this.setData({ currentQuestionId: options.question_id });
      this.askQuestion(options.question_id, options.type || 'explain');
    }
  },

  onUnload() {
    if (this.streamTimer) {
      clearInterval(this.streamTimer);
      this.streamTimer = null;
    }
  },

  initUser() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({ userInfo });
    }
  },

  async loadProviders() {
    try {
      const res = await request.get(api.ai.providers);
      if (res && res.length > 0) {
        // 构建扁平化模型选项
        const allModelOptions = [];
        res.forEach(p => {
          if (p.models && p.models.length) {
            p.models.forEach(m => {
              allModelOptions.push({
                id: m,
                name: `${p.name} · ${m}`, // 组合名称
                providerId: p.id,
                providerName: p.name
              });
            });
          }
        });

        // 默认选中逻辑
        if (allModelOptions.length > 0) {
          // 1. 找默认服务商
          let defaultProvider = res.find(p => p.is_default) || res.find(p => p.is_available) || res[0];
          // 2. 找该服务商的默认模型
          let defaultModel = defaultProvider ? defaultProvider.default_model : null;
          // 3. 对应到 options
          let currentOption = null;
          if (defaultProvider && defaultModel) {
            currentOption = allModelOptions.find(o => o.providerId === defaultProvider.id && o.id === defaultModel);
          }
          if (!currentOption) {
            currentOption = allModelOptions[0];
          }
          
          if (currentOption) {
            this.setData({ 
              providers: res,
              allModelOptions,
              currentProvider: res.find(p => p.id === currentOption.providerId),
              currentModel: currentOption.id,
              currentModelName: currentOption.name
            });
          }
        } else {
           // 没有任何模型，仅保存 providers
           this.setData({ providers: res });
        }
      }
    } catch (err) {
      console.error('获取AI服务商失败', err);
    }
  },

  async loadHistory(id) {
    wx.showLoading({ title: '加载历史...' });
    try {
      const res = await request.get(api.ai.conversationDetail(id));
      
      if (res && res.messages) {
        // 转换消息格式
        const historyMsgs = res.messages.map(m => ({
          id: m.id || Math.random().toString(36), // 确保有ID
          role: m.role, // 'user' or 'assistant'
          content: m.content,
          htmlContent: markdown.parse(m.content), // 预处理历史消息 Markdown
          question_id: res.question_id // 关联的题目ID
        }));
        
        // 保留欢迎语，追加历史
        this.setData({
          messages: [this.data.messages[0], ...historyMsgs],
          currentQuestionId: res.question_id
        });
        this.scrollToBottom();
      }
    } catch (err) {
      console.error('加载历史失败', err);
      this.addMessage('ai', '加载历史记录失败');
    } finally {
      wx.hideLoading();
    }
  },

  // 切换模型
  onModelChange(e) {
    const index = e.detail.value;
    const options = this.data.allModelOptions;
    
    if (!options || !options[index]) return;
    
    const selected = options[index];
    const providerObj = this.data.providers.find(p => p.id === selected.providerId);
    
    this.setData({ 
      currentProvider: providerObj,
      currentModel: selected.id,
      currentModelName: selected.name,
      currentModelIndex: index
    });
    
    // 调用接口保存偏好
    try {
      request.put(api.ai.provider, { provider: selected.providerId });
    } catch (err) {
      console.error('切换服务商偏好保存失败', err);
    }
  },

  showProviderSheet() {
    // 兼容保留，但不再使用
    const options = this.data.allModelOptions;
    if (!options || !options.length) {
       this.loadProviders();
       return;
    }
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  toggleTools() {
    this.setData({ showTools: !this.data.showTools });
    if (this.data.showTools) {
      this.scrollToBottom();
    }
  },
  
  closeTools() {
    if (this.data.showTools) {
      this.setData({ showTools: false });
    }
  },

  selectMode(e) {
    const mode = e.currentTarget.dataset.mode;
    this.setData({ showTools: false });
    
    if (mode === 'explain') {
      this.setData({ inputValue: '请讲解一下这个知识点：' });
    } else if (mode === 'solve') {
      this.setData({ inputValue: '请帮我解这道题：' });
    }
  },

  // 处理快捷操作：提示、相似题
  async handleAction(e) {
    const { type, qid } = e.currentTarget.dataset;
    if (!qid) return;
    
    let text = type === 'hint' ? '给我一点提示' : '出几道相似题看看';
    this.addMessage('user', text);
    this.setData({ loading: true });
    this.scrollToBottom();
    
    try {
      let res;
      const provider = this.data.currentProvider ? this.data.currentProvider.id : null;
      
      if (type === 'hint') {
        res = await request.post(api.ai.hint, { 
          question_id: qid, 
          hint_level: 1,
          provider,
          model: this.data.currentModel
        });
        this.addMessage('ai', res.hint || '暂无提示', qid);
      } else {
        res = await request.post(api.ai.similar, { 
          question_id: qid, 
          count: 3,
          provider,
          model: this.data.currentModel
        });
        this.addMessage('ai', res.similar_questions_text || '暂无相似题', qid);
      }
    } catch (err) {
      this.addMessage('ai', '操作失败，请重试');
    } finally {
      this.setData({ loading: false });
      this.scrollToBottom();
    }
  },

  // 处理流式响应
  streamResponse(options, questionId) {
    const aiMsgId = Date.now();
    // 添加空消息占位
    this.addMessage('ai', '', questionId, aiMsgId);
    
    // 前端缓冲队列
    let pendingText = '';
    let isFinished = false;
    
    // 清除旧的定时器
    if (this.streamTimer) clearInterval(this.streamTimer);

    const flush = () => {
      if (!pendingText) {
        if (isFinished) {
          clearInterval(this.streamTimer);
          this.streamTimer = null;
          this.setData({ loading: false });
          this.scrollToBottom();
        }
        return;
      }

      // 每次取 2 个字符（控制打字速度）
      const chunk = pendingText.slice(0, 2);
      pendingText = pendingText.slice(2);

      const messages = this.data.messages;
      const target = messages.find(m => m.id === aiMsgId);
      if (target) {
        target.content += chunk;
        target.htmlContent = markdown.parse(target.content);
        this.setData({ messages });
      }
    };

    // 启动定时器，每 50ms 渲染一次
    this.streamTimer = setInterval(flush, 50);
    
    const onMessage = (text) => {
      pendingText += text;
    };
    
    const onFinish = () => {
      isFinished = true;
      // 不立即清除定时器，等待 pendingText 消费完
    };
    
    const onMeta = (meta) => {
      if (meta && meta.conversation_id) {
        this.setData({ conversationId: meta.conversation_id });
      }
    };
    
    const onError = (err) => {
      console.error('Stream error', err);
      clearInterval(this.streamTimer);
      this.streamTimer = null;
      const messages = this.data.messages;
      const target = messages.find(m => m.id === aiMsgId);
      if (target) {
        target.content += '\n[网络错误]';
        target.htmlContent = markdown.parse(target.content);
        this.setData({ messages, loading: false });
      }
    };

    request.stream({
      ...options,
      onMessage,
      onFinish,
      onError
    });
  },

  // 直接提问（从外部进入或内部调用）
  async askQuestion(questionId, type) {
    let text = type === 'similar' ? '请帮我出几道类似的题目' : '请帮我讲解一下这道题';
    this.addMessage('user', text);
    this.setData({ loading: true });
    this.scrollToBottom();

    try {
      const provider = this.data.currentProvider ? this.data.currentProvider.id : null;
      let res;
      
      if (type === 'explain') {
        res = await request.post(api.ai.explain, { question_id: questionId, provider, model: this.data.currentModel });
        this.addMessage('ai', res.explanation, questionId);
      } else if (type === 'similar') {
        res = await request.post(api.ai.similar, { question_id: questionId, provider, model: this.data.currentModel });
        this.addMessage('ai', res.similar_questions_text, questionId);
      } else {
        // 使用流式解题
        this.streamResponse({
          url: api.ai.solveStream,
          data: { question_id: questionId, provider, model: this.data.currentModel }
        }, questionId);
        return; // streamResponse handles loading state
      }
      
      if (res && res.conversation_id) {
        this.setData({ conversationId: res.conversation_id });
      }
      
      // 非流式请求完成
      this.setData({ loading: false });
      this.scrollToBottom();

    } catch (err) {
      this.addMessage('ai', '出错了，请稍后再试');
      this.setData({ loading: false });
      this.scrollToBottom();
    }
  },

  async sendMessage() {
    const content = this.data.inputValue.trim();
    if (!content) return;
    
    if (this.data.loading) {
      wx.showToast({ title: 'AI正在思考中...', icon: 'none' });
      return;
    }

    this.setData({ 
      inputValue: '',
      showTools: false
    });
    this.addMessage('user', content);
    this.setData({ loading: true });
    this.scrollToBottom();

    try {
      const provider = this.data.currentProvider ? this.data.currentProvider.id : null;
      let qid = this.data.currentQuestionId;

      if (this.data.conversationId) {
        // 追问 - 流式
        this.streamResponse({
          url: api.ai.conversationMsgStream(this.data.conversationId),
          data: { message: content, provider, model: this.data.currentModel }
        }, qid);
        return;
      } 
      
      // 新会话
      if (content.includes('讲解') || content.includes('知识点')) {
          const res = await request.post(api.ai.explain, { 
            knowledge_point_name: content.replace(/请讲解|讲解|知识点/g, ''),
            provider,
            model: this.data.currentModel
          });
          
          this.addMessage('ai', res.explanation, qid);
          if (res.conversation_id) {
            this.setData({ conversationId: res.conversation_id });
          }
          
          this.setData({ loading: false });
          this.scrollToBottom();
      } else {
          // 默认解题 - 流式
          this.streamResponse({
            url: api.ai.solveStream,
            data: { question_content: content, provider, model: this.data.currentModel }
          }, qid);
          return;
      }

    } catch (err) {
      console.error(err);
      this.addMessage('ai', '网络开小差了，请重试。');
      this.setData({ loading: false });
      this.scrollToBottom();
    }
  },

  addMessage(role, content, questionId = null, id = null) {
    const messages = this.data.messages;
    // AI 和 用户消息都尝试转换格式以支持 LaTeX
    const htmlContent = markdown.parse(content);
    
    messages.push({
      id: id || Date.now(),
      role: role === 'user' ? 'user' : 'assistant', // 统一角色名
      content,
      htmlContent,
      question_id: questionId
    });
    this.setData({ messages });
  },

  scrollToBottom() {
    setTimeout(() => {
      this.setData({
        scrollIntoView: `msg-${this.data.messages.length - 1}`
      });
    }, 100);
  },
  
  goToHistory() {
    wx.navigateTo({
      url: '/pages/ai/history/index'
    });
  }
});
