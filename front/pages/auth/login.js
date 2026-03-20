const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const config = require('../../utils/config.js');

Page({
  data: {
    loginType: 'password', // password or code
    account: '',
    password: '',
    code: '',
    loading: false,
    counting: false,
    count: 60,
    timer: null,
    agreed: false,
    showPassword: false // 控制密码显示/隐藏
  },

  onLoad(options) {
    // 检查是否已有 Token，有则直接跳转首页
    const token = wx.getStorageSync(config.tokenKey);
    if (token) {
      wx.switchTab({
        url: '/pages/home/index'
      });
    }
  },

  onUnload() {
    if (this.data.timer) {
      clearInterval(this.data.timer);
    }
  },

  switchLoginType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      loginType: type,
      password: '',
      code: ''
    });
  },

  onAccountInput(e) {
    this.setData({ account: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  // 切换密码显示/隐藏
  togglePasswordVisibility() {
    this.setData({
      showPassword: !this.data.showPassword
    });
  },

  onCodeInput(e) {
    this.setData({ code: e.detail.value });
  },

  onAgreementChange(e) {
    this.setData({ agreed: e.detail.value.includes('agreed') });
  },

  showUserAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '这里是用户协议的详细内容...',
      showCancel: false
    });
  },

  showPrivacyPolicy() {
    wx.showModal({
      title: '隐私政策',
      content: '这里是隐私政策的详细内容...',
      showCancel: false
    });
  },

  // 发送验证码
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
        scene: 'login'
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

  // 登录
  async handleLogin() {
    if (!this.data.agreed) {
      wx.showModal({
        title: '提示',
        content: '请阅读并同意用户协议和隐私政策',
        confirmText: '同意',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.setData({ agreed: true });
            this.handleLogin();
          }
        }
      });
      return;
    }

    const { loginType, account, password, code } = this.data;

    if (!account) {
      wx.showToast({ title: '请输入手机号/邮箱', icon: 'none' });
      return;
    }

    if (loginType === 'password' && !password) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }

    if (loginType === 'code' && !code) {
      wx.showToast({ title: '请输入验证码', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      let res;
      if (loginType === 'password') {
        res = await request.post(api.auth.login, { account, password });
      } else {
        res = await request.post(api.auth.loginCode, { 
          target: account, 
          verify_code: code 
        });
      }

      // 登录成功，保存 Token
      // 兼容新的返回格式：直接返回 tokens，没有 user 对象
      const access_token = res.access_token || (res.tokens && res.tokens.access_token);
      const refresh_token = res.refresh_token || (res.tokens && res.tokens.refresh_token);
      const accessExpireAt = res.accessExpireAt || (res.tokens && res.tokens.accessExpireAt);
      const user = res.user;

      if (access_token) {
        wx.setStorageSync(config.tokenKey, access_token);
        if (refresh_token) {
          wx.setStorageSync(config.refreshTokenKey, refresh_token);
        }
        if (accessExpireAt) {
          wx.setStorageSync(config.tokenExpireKey, accessExpireAt);
        }
        
        // 如果返回中包含 user，直接保存；否则请求用户信息
        if (user) {
          wx.setStorageSync(config.userKey, user);
          this.loginSuccess();
        } else {
          try {
            const userInfo = await request.get(api.user.me);
            wx.setStorageSync(config.userKey, userInfo);
            this.loginSuccess();
          } catch (err) {
            console.error('获取用户信息失败', err);
            // 即使获取用户信息失败，也允许进入首页，可能会在首页再次尝试获取
            this.loginSuccess();
          }
        }
      } else {
        throw new Error('登录返回数据异常');
      }

    } catch (err) {
      console.error(err);
      // request.js 已经处理了 toast 提示
    } finally {
      this.setData({ loading: false });
    }
  },

  loginSuccess() {
    wx.showToast({ title: '登录成功', icon: 'success' });
    setTimeout(() => {
      wx.switchTab({
        url: '/pages/home/index'
      });
    }, 1500);
  },

  goToRegister() {
    wx.navigateTo({
      url: '/pages/auth/register'
    });
  },

  goToForgotPassword() {
    wx.navigateTo({
      url: '/pages/auth/forgot-password'
    });
  }
});
