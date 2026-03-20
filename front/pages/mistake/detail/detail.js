const request = require('../../../utils/request.js');
const api = require('../../../utils/api.js');
const markdown = require('../../../utils/markdown.js');

Page({
  data: {
    mistake: null,
    loading: false,
    aiResult: '',
    error: '',
    aiProvider: 'deepseek', // 默认使用 deepseek
    renderedQuestion: '',
    renderedAnswer: '',
    renderedAnalysis: ''
  },

  onLoad(options) {
    const eventChannel = this.getOpenerEventChannel();
    if (eventChannel && eventChannel.on) {
      eventChannel.on('acceptDataFromOpenerPage', (data) => {
        const mistake = data.mistake;
        this.setData({
          mistake: mistake,
          renderedQuestion: markdown.parse((mistake && mistake.question && mistake.question.content) || '')
        }, () => {
          this.solveQuestion();
        });
      });
    }
  },

  async solveQuestion() {
    const { mistake, aiProvider } = this.data;
    if (!mistake || !mistake.question) return;

    this.setData({
      loading: true,
      error: '',
      aiResult: null
    });

    try {
      const res = await request.post(api.ai.solveText, {
        question_text: mistake.question.content,
        ai_provider: aiProvider
      });

      if (res && res.answer) {
        const answer = res.answer;
        // 如果有选项，也进行渲染
        if (answer.options && answer.options.length > 0) {
          answer.options = answer.options.map(opt => ({
            ...opt,
            renderedContent: markdown.parse(opt.content || '')
          }));
        }

        this.setData({
          aiResult: answer,
          renderedAnswer: markdown.parse(answer.content || ''),
          renderedAnalysis: markdown.parse(answer.analysis || ''),
          loading: false
        });
      } else {
        throw new Error('未能获取到解析内容');
      }
    } catch (err) {
      console.error('AI 解题失败', err);
      this.setData({
        loading: false,
        error: err.message || '获取解析失败，请稍后重试'
      });
    }
  }
});