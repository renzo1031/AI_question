<template>
  <div class="login-container">
    <canvas ref="canvasRef" class="login-bg-canvas"></canvas>
    <div class="login-content">
      <div class="login-left">
        <div class="login-left-mask">
          <div class="login-slogan">
            <div class="slogan-title">AI Question Admin</div>
            <div class="slogan-desc">基于 Vue3 + Ant Design Vue 的现代化管理后台</div>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="login-form-wrapper">
          <div class="login-header">
            <div class="login-logo">
              <img src="../assets/logo.svg" alt="logo" />
              <span>管理后台</span>
            </div>
            <p class="login-desc">欢迎回来，请登录您的账号</p>
          </div>
          
          <a-tabs v-model:activeKey="activeKey" centered style="margin-bottom: 24px;">
            <a-tab-pane key="account" tab="账号密码登录" />
            <a-tab-pane key="mobile" tab="验证码登录" />
          </a-tabs>

          <a-form
            :model="activeKey === 'account' ? formState : mobileFormState"
            name="basic"
            :label-col="{ span: 0 }"
            :wrapper-col="{ span: 24 }"
            autocomplete="off"
            @finish="onFinish"
            @finishFailed="onFinishFailed"
            class="login-form"
          >
            <div v-if="activeKey === 'account'">
              <a-form-item
                name="account"
                :rules="[{ required: true, message: '请输入账号!' }]"
              >
                <a-input v-model:value="formState.account" placeholder="手机号/邮箱" size="large">
                  <template #prefix>
                    <UserOutlined class="icon-color" />
                  </template>
                </a-input>
              </a-form-item>

              <a-form-item
                name="password"
                :rules="[{ required: true, message: '请输入密码!' }]"
              >
                <a-input-password v-model:value="formState.password" placeholder="密码" size="large">
                  <template #prefix>
                    <LockOutlined class="icon-color" />
                  </template>
                </a-input-password>
              </a-form-item>
            </div>

            <div v-if="activeKey === 'mobile'">
              <a-form-item
                name="account"
                :rules="[{ required: true, message: '请输入手机号或邮箱!' }]"
              >
                <a-input v-model:value="mobileFormState.account" placeholder="手机号/邮箱" size="large">
                  <template #prefix>
                    <MobileOutlined class="icon-color" />
                  </template>
                </a-input>
              </a-form-item>

              <a-form-item
                name="verify_code"
                :rules="[{ required: true, message: '请输入验证码!' }]"
              >
                <div style="display: flex; gap: 8px;">
                  <a-input v-model:value="mobileFormState.verify_code" placeholder="验证码" size="large">
                    <template #prefix>
                      <SafetyOutlined class="icon-color" />
                    </template>
                  </a-input>
                  <a-button 
                    size="large" 
                    :disabled="!!countdown || sending" 
                    :loading="sending"
                    @click="handleSendCode"
                  >
                    {{ countdown ? `${countdown}s` : '获取验证码' }}
                  </a-button>
                </div>
              </a-form-item>
            </div>

            <div class="login-options">
              <a-checkbox v-model:checked="formState.remember">记住我</a-checkbox>
              <a class="forgot-password">忘记密码？</a>
            </div>

            <a-form-item>
              <a-button type="primary" html-type="submit" block size="large" :loading="loading" class="submit-btn">
                登录
              </a-button>
            </a-form-item>
            
            <div class="form-footer">
              还没有账号？ <router-link to="/register">立即注册</router-link>
            </div>
          </a-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onUnmounted, onMounted, watch } from 'vue';
import { UserOutlined, LockOutlined, MobileOutlined, SafetyOutlined } from '@ant-design/icons-vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { sendVerificationCode } from '../api/auth';

const canvasRef = ref(null);
let animationFrameId = null;

const initCanvas = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  const particles = [];
  const particleCount = 100; // 粒子数量

  // 鼠标交互对象
  let mouse = {
    x: null,
    y: null,
    radius: 150
  };

  const handleResize = () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  };

  const handleMouseMove = (event) => {
    mouse.x = event.clientX;
    mouse.y = event.clientY;
  };

  const handleMouseOut = () => {
    mouse.x = null;
    mouse.y = null;
  };

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 1;
      this.vy = (Math.random() - 0.5) * 1;
      this.size = Math.random() * 2 + 1;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // 鼠标互动：排斥效果
      if (mouse.x != null) {
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < mouse.radius) {
            const forceDirectionX = dx / distance;
            const forceDirectionY = dy / distance;
            const force = (mouse.radius - distance) / mouse.radius;
            const directionX = forceDirectionX * force * 5;
            const directionY = forceDirectionY * force * 5;

            this.x -= directionX;
            this.y -= directionY;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(24, 144, 255, 0.3)';
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  const animate = () => {
    ctx.clearRect(0, 0, width, height);

    // 绘制连线
    for (let i = 0; i < particles.length; i++) {
      const p1 = particles[i];
      p1.update();
      p1.draw();

      // 粒子与粒子之间的连线
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 150) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(24, 144, 255, ${0.2 * (1 - distance / 150)})`;
          ctx.lineWidth = 1;
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }

      // 粒子与鼠标之间的连线
      if (mouse.x != null) {
        let dx = mouse.x - p1.x;
        let dy = mouse.y - p1.y;
        let distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < mouse.radius) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(24, 144, 255, ${0.4 * (1 - distance / mouse.radius)})`;
            ctx.lineWidth = 1;
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(mouse.x, mouse.y);
            ctx.stroke();
        }
      }
    }

    animationFrameId = requestAnimationFrame(animate);
  };

  animate();

  window.addEventListener('resize', handleResize);
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('mouseout', handleMouseOut);

  // 清理函数
  const cleanup = () => {
    window.removeEventListener('resize', handleResize);
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('mouseout', handleMouseOut);
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
  };
  
  return cleanup;
};

let cleanupCanvas = null;

onMounted(() => {
  cleanupCanvas = initCanvas();
});

onUnmounted(() => {
  if (cleanupCanvas) {
    cleanupCanvas();
  }
});

const activeKey = ref('account');
const formState = reactive({
  account: '',
  password: '',
  remember: true
});

const mobileFormState = reactive({
  account: '',
  verify_code: ''
});

// 监听 tab 切换，同步账号/手机号字段
watch(activeKey, (newVal) => {
  if (newVal === 'mobile') {
    mobileFormState.account = formState.account;
  } else {
    formState.account = mobileFormState.account;
  }
});

const loading = ref(false);
const sending = ref(false);
const countdown = ref(0);
let timer = null;

const userStore = useUserStore();
const router = useRouter();

const handleSendCode = async () => {
  if (!mobileFormState.account) {
    message.warning('请输入手机号或邮箱');
    return;
  }
  
  sending.value = true;
  try {
    const res = await sendVerificationCode({
      target: mobileFormState.account,
      scene: 'login'
    });
    
    if (res.code === 0) {
      message.success('验证码已发送');
      countdown.value = 60;
      timer = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
          clearInterval(timer);
          timer = null;
        }
      }, 1000);
    } else {
      message.error(res.message || '发送失败');
    }
  } catch (error) {
    message.error(error.message || '发送失败');
  } finally {
    sending.value = false;
  }
};

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

const onFinish = async (values) => {
  loading.value = true;
  try {
    if (activeKey.value === 'account') {
      await userStore.login(values.account, values.password);
    } else {
      await userStore.loginByCode(values.account, values.verify_code);
    }
    message.success('登录成功');
    router.push('/');
  } catch (error) {
    message.error(error.message || '登录失败');
  } finally {
    loading.value = false;
  }
};

const onFinishFailed = (errorInfo) => {
  console.log('Failed:', errorInfo);
};
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  /* background-image: url('https://gw.alipayobjects.com/zos/rmsportal/TVYTbAXWheQpRcWDaDMu.svg'); */
  /* background-repeat: no-repeat; */
  /* background-position: center 110px; */
  /* background-size: 100%; */
  position: relative;
  overflow: hidden;
}

.login-bg-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.login-content {
  display: flex;
  width: 1000px;
  height: 600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.login-left {
  flex: 1;
  position: relative;
  background-image: url('https://img1.wallspic.com/previews/8/2/6/9/3/139628/139628-bi_ji_ben-zuo_zhe-yue_du-mu-ben_shu-x750.jpg');
  background-size: cover;
  background-position: center;
}

.login-left-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(22, 119, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  padding: 40px;
}

.login-slogan {
  text-align: center;
}

.slogan-title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 16px;
  letter-spacing: 2px;
}

.slogan-desc {
  font-size: 16px;
  opacity: 0.8;
}

.login-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.login-form-wrapper {
  width: 100%;
  max-width: 360px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.login-logo img {
  height: 44px;
  margin-right: 16px;
}

.login-logo span {
  font-size: 24px;
  color: #333;
  font-weight: 600;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
}

.login-desc {
  color: #8c8c8c;
  font-size: 14px;
}

.icon-color {
  color: #bfbfbf;
}

.login-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.forgot-password {
  color: #1677ff;
  cursor: pointer;
}

.submit-btn {
  height: 40px;
  font-size: 16px;
}

.form-footer {
  text-align: center;
  color: #8c8c8c;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .login-content {
    width: 90%;
    height: auto;
    flex-direction: column;
  }
  
  .login-left {
    display: none;
  }
  
  .login-right {
    padding: 40px 20px;
  }
}
</style>
