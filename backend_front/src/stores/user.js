import { defineStore } from 'pinia';
import { login, register, logout, loginByVerificationCode, getCurrentAdmin, refreshToken } from '../api/auth';
import { getUserDetail, updateUser } from '../api/user';

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: JSON.parse(localStorage.getItem('userInfo')) || null,
    // 下次刷新 token 的超时器 id
    refreshTimer: null,
    // 记录服务端返回的过期时间戳（毫秒），仅用于调试或展示
    tokenExpireAt: null
  }),
  actions: {
    /**
     * 启动 / 重启 Token 刷新定时器
     * @param {number} expiresIn 后端返回的有效期（秒）
     * 规则：如果有 expires_in，则在过期前 1 分钟刷新；
     *      没有则使用一个保守的默认值。
     */
    startTokenRefresh(expiresIn) {
      // 先清理旧的 timer，避免重复
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer);
        this.refreshTimer = null;
      }

      // 如果当前没有登录用户，不需要刷新
      if (!this.userInfo) return;

      // 默认：15 分钟有效期，提前 1 分钟刷新
      let effectiveExpiresIn = 15 * 60; // 秒
      if (typeof expiresIn === 'number' && expiresIn > 0) {
        effectiveExpiresIn = expiresIn;
      }

      // 记录预计过期时间，仅用于调试/展示
      this.tokenExpireAt = Date.now() + effectiveExpiresIn * 1000;

      // 刷新提前量：1 分钟（60 秒）
      const aheadSeconds = 60;
      let delay = (effectiveExpiresIn - aheadSeconds) * 1000;
      // 避免出现负数或过短的时间，设一个最小间隔（至少 30 秒）
      const minDelay = 30 * 1000;
      if (isNaN(delay) || delay <= 0) {
        delay = minDelay;
      } else if (delay < minDelay) {
        delay = minDelay;
      }

      this.refreshTimer = setTimeout(async () => {
        try {
          const res = await refreshToken();
          const nextExpiresIn = res?.data?.expires_in;
          // 成功后使用新的 expires_in 继续安排下一次刷新（递归式调度）
          this.startTokenRefresh(nextExpiresIn);
        } catch (error) {
          // 刷新失败的跳转与清理由 axios 拦截器统一处理
          // 这里只做静默捕获，避免未处理的 Promise 报错
          console.error('auto refresh token failed', error);
        }
      }, delay);
    },

    stopTokenRefresh() {
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer);
        this.refreshTimer = null;
      }
      this.tokenExpireAt = null;
    },

    async login(account, password) {
      try {
        const response = await login({ account, password });
        if (response.code === 0) {
          // If response data is null or missing user info, fetch it separately
          if (response.data && response.data.user) {
            this.userInfo = response.data.user;
          } else {
            const userRes = await getCurrentAdmin();
            if (userRes.code === 0) {
              this.userInfo = userRes.data;
            }
          }
          
          if (this.userInfo) {
            localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
          }
          // Set a token marker for router guard
          localStorage.setItem('token', 'session-cookie');
          // 启动无感刷新，优先使用后端返回的 expires_in
          const expiresIn = response?.data?.expires_in;
          this.startTokenRefresh(expiresIn);
          return true;
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        throw error;
      }
    },

    async loginByCode(account, verify_code) {
      try {
        const response = await loginByVerificationCode({ account, verify_code });
        if (response.code === 0) {
          // If response data is null or missing user info, fetch it separately
          if (response.data && response.data.user) {
            this.userInfo = response.data.user;
          } else {
            const userRes = await getCurrentAdmin();
            if (userRes.code === 0) {
              this.userInfo = userRes.data;
            }
          }

          if (this.userInfo) {
            localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
          }
          // Set a token marker for router guard
          localStorage.setItem('token', 'session-cookie');
          // 启动无感刷新，优先使用后端返回的 expires_in
          const expiresIn = response?.data?.expires_in;
          this.startTokenRefresh(expiresIn);
          return true;
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        throw error;
      }
    },

    async register(data) {
      try {
        const response = await register(data);
        if (response.code === 0) {
          return true;
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        throw error;
      }
    },

    async logout() {
      try {
        const res = await logout();
        return res;
      } catch (error) {
        console.error(error);
      } finally {
        this.stopTokenRefresh();
        this.userInfo = null;
        localStorage.removeItem('userInfo');
        localStorage.removeItem('token');
      }
    },

    async getUserInfo() {
      try {
        const res = await getCurrentAdmin();
        if (res.code === 0) {
          this.userInfo = res.data;
          localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
          // 应用刷新后如果本地已有登录态但还没启动定时器，这里补一手，
          // 但此时通常拿不到 expires_in，所以走默认策略
          if (!this.refreshTimer) {
            this.startTokenRefresh();
          }
        }
      } catch (error) {
        console.error(error);
      }
    },

    async updateUserInfo(data) {
      if (!this.userInfo || !this.userInfo.id) return;
      try {
        const res = await updateUser(this.userInfo.id, data);
        if (res.code === 0) {
          this.userInfo = { ...this.userInfo, ...res.data };
          localStorage.setItem('userInfo', JSON.stringify(this.userInfo));
        } else {
          throw new Error(res.message);
        }
      } catch (error) {
        throw error;
      }
    }
  }
});
