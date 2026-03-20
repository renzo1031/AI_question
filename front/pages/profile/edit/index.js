const request = require('../../../utils/request.js');
const api = require('../../../utils/api.js');
const config = require('../../../utils/config.js');

Page({
  data: {
    formData: {
      nickname: '',
      avatar: '',
      gender: '', // male, female, secret
      birthday: '',
      phone: '',
      email: '',
      created_at: ''
    },
    genders: [
      { value: 'male', label: '男' },
      { value: 'female', label: '女' },
      { value: 'unknown', label: '未知' }
    ],
    genderIndex: -1,
    today: new Date().toISOString().split('T')[0],
    loading: false
  },

  onLoad() {
    this.loadUserInfo();
  },

  async loadUserInfo() {
    try {
      const res = await request.get(api.user.me);
      if (res) {
        // 处理性别回显
        let genderIndex = -1;
        if (res.gender) {
          genderIndex = this.data.genders.findIndex(g => g.value === res.gender);
        }

        // 处理生日格式 (如果是 ISO 格式，只取日期部分)
        let birthday = '';
        if (res.birthday) {
          birthday = res.birthday.split('T')[0];
        }

        // 处理注册时间格式
        let created_at = '';
        if (res.created_at) {
          created_at = res.created_at.replace('T', ' ').substring(0, 19);
        }

        this.setData({
          formData: {
            nickname: res.nickname || '',
            avatar: res.avatar || '',
            gender: res.gender || '',
            birthday: birthday,
            phone: res.phone || '',
            email: res.email || '',
            created_at: created_at
          },
          genderIndex
        });
      }
    } catch (err) {
      console.error('获取用户信息失败', err);
      wx.showToast({
        title: '获取信息失败',
        icon: 'none'
      });
    }
  },

  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({
      [`formData.${field}`]: value
    });
  },

  handleGenderChange(e) {
    const index = e.detail.value;
    const gender = this.data.genders[index].value;
    this.setData({
      genderIndex: index,
      'formData.gender': gender
    });
  },

  handleBirthdayChange(e) {
    const value = e.detail.value;
    this.setData({
      'formData.birthday': value
    });
  },

  chooseAvatar() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        this.uploadAvatar(tempFilePath);
      }
    });
  },

  uploadAvatar(filePath) {
    if (!config.cos.bucket) {
      wx.showToast({ title: '未配置存储桶', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '上传中...' });

    const cos = new COS({
      getAuthorization: function (options, callback) {
        request.get(api.upload.sts).then(res => {
          const data = res.data || res;
          const credentials = data.credentials || {};
          callback({
            TmpSecretId: credentials.tmpSecretId,
            TmpSecretKey: credentials.tmpSecretKey,
            XCosSecurityToken: credentials.sessionToken,
            StartTime: data.startTime,
            ExpiredTime: data.expiredTime,
          });
        }).catch(err => {
          console.error('获取STS失败', err);
          callback({});
        });
      }
    });

    const ext = filePath.split('.').pop() || 'jpg';
    const key = `avatars/${Date.now()}-${Math.floor(Math.random() * 1000)}.${ext}`;

    cos.postObject({
      Bucket: config.cos.bucket,
      Region: config.cos.region,
      Key: key,
      FilePath: filePath,
    }, (err, data) => {
      wx.hideLoading();
      if (err) {
        console.error('上传头像失败', err);
        wx.showToast({ title: '上传失败', icon: 'none' });
        return;
      }
      
      // data.Location 为不带协议头的 URL
      const avatarUrl = 'https://' + data.Location;
      this.setData({
        'formData.avatar': avatarUrl
      });
      wx.showToast({ title: '上传成功', icon: 'success' });
    });
  },

  async handleSave() {
    if (this.data.loading) return;

    const { nickname, gender, birthday, avatar } = this.data.formData;
    
    if (!nickname.trim()) {
      wx.showToast({
        title: '昵称不能为空',
        icon: 'none'
      });
      return;
    }

    this.setData({ loading: true });

    try {
      const updateData = {
        nickname,
        gender,
        birthday,
        avatar
      };

      await request.put(api.user.updateMe, updateData);
      
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      });

      // 更新上一页（个人中心）的数据
      const pages = getCurrentPages();
      const prevPage = pages[pages.length - 2];
      if (prevPage && prevPage.getUserInfo) {
        prevPage.getUserInfo();
      }

      setTimeout(() => {
        wx.navigateBack();
      }, 1500);

    } catch (err) {
      console.error('更新用户信息失败', err);
      wx.showToast({
        title: '保存失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  }
});