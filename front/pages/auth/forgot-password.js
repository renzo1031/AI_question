const request = require('../../utils/request.js');
const api = require('../../utils/api.js');

Page({
  data: {
    account: '',
    code: '',
    password: '',
    confirmPassword: '',
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

  onAccountInput(e) {
    this.setData({ account: e.detail.value });
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

  async sendCode() {
    if (this.data.counting) return;
    if (!this.data.account) {
      wx.showToast({ title: '请输入手机号/邮箱', icon: 'none' });
      return;
    }

    try {
      this.setData({ counting: true });
      await request.post(api.auth.sendCode, {
        target: this.data.account,
        scene: 'reset_password'
      });
      
      wx.showToast({ title: '验证码已发送', icon: 'success' });
      
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

  async handleReset() {
    const { account, code, password, confirmPassword } = this.data;

    if (!account || !code || !password || !confirmPassword) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' });
      return;
    }

    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码输入不一致', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      await request.post(api.auth.resetPassword, {
        account,
        code,
        new_password: password
      });

      wx.showToast({ title: '密码重置成功', icon: 'success' });
      
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);

    } catch (err) {
      console.error(err);
      this.setData({ loading: false });
    }
  },

  goToLogin() {
    wx.navigateBack();
  }
});
