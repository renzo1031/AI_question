const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const config = require('../../utils/config.js');

Page({
  data: {
    registerType: 'phone', // phone or email
    phone: '',
    email: '',
    code: '',
    password: '',
    confirmPassword: '',
    nickname: '',
    loading: false,
    counting: false,
    count: 60,
    timer: null,
    showPassword: false, // 控制密码显示/隐藏
    showConfirmPassword: false // 控制确认密码显示/隐藏
  },

  onUnload() {
    if (this.data.timer) {
      clearInterval(this.data.timer);
    }
  },

  switchRegisterType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      registerType: type,
      phone: '',
      email: '',
      code: '',
      password: ''
    });
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value });
  },

  onEmailInput(e) {
    this.setData({ email: e.detail.value });
  },

  onCodeInput(e) {
    this.setData({ code: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  onConfirmPasswordInput(e) {
    this.setData({ confirmPassword: e.detail.value });
  },

  // 切换密码显示/隐藏
  togglePasswordVisibility() {
    this.setData({
      showPassword: !this.data.showPassword
    });
  },

  // 切换确认密码显示/隐藏
  toggleConfirmPasswordVisibility() {
    this.setData({
      showConfirmPassword: !this.data.showConfirmPassword
    });
  },

  onNicknameInput(e) {
    this.setData({ nickname: e.detail.value });
  },

  // 发送验证码
  async sendCode() {
    if (this.data.counting) return;

    const { registerType, phone, email } = this.data;
    const account = registerType === 'phone' ? phone : email;

    if (!account) {
      wx.showToast({ title: `请输入${registerType === 'phone' ? '手机号' : '邮箱'}`, icon: 'none' });
      return;
    }

    try {
      this.setData({ counting: true });
      await request.post(api.auth.sendCode, {
        target: account,
        scene: 'register'
      });
      
      wx.showToast({ title: '验证码已发送', icon: 'success' });
      
      // 倒计时
      this.data.timer = setInterval(() => {
        if (this.data.count > 0) {
          this.setData({ count: this.data.count - 1 });
        } else {
          clearInterval(this.data.timer);
          this.setData({
            counting: false,
            count: 60,
            timer: null
          });
        }
      }, 1000);
    } catch (err) {
      this.setData({ counting: false });
    }
  },

  // 注册
  async handleRegister() {
    const { registerType, phone, email, code, password, confirmPassword, nickname } = this.data;
    const account = registerType === 'phone' ? phone : email;

    if (!account) {
      wx.showToast({ title: `请输入${registerType === 'phone' ? '手机号' : '邮箱'}`, icon: 'none' });
      return;
    }

    if (!code) {
      wx.showToast({ title: '请输入验证码', icon: 'none' });
      return;
    }

    if (!password || password.length < 6) {
      wx.showToast({ title: '密码长度至少6位', icon: 'none' });
      return;
    }

    if (password !== confirmPassword) {
      wx.showToast({ title: '两次输入的密码不一致', icon: 'none' });
      return;
    }

    if (!nickname) {
      wx.showToast({ title: '请输入昵称', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      let res;
      if (registerType === 'phone') {
        res = await request.post(api.auth.registerPhone, { phone, code, password, nickname });
      } else {
        // 适配新的 email 注册参数：verify_code
        res = await request.post(api.auth.registerEmail, { 
          email, 
          verify_code: code, 
          password, 
          nickname 
        });
      }

      // 注册成功，提示并返回登录页
      wx.showToast({ title: '注册成功，请登录', icon: 'success' });
      
      setTimeout(() => {
        this.goToLogin();
      }, 1500);

    } catch (err) {
      console.error('注册失败', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  goToLogin() {
    wx.navigateBack();
  }
});
