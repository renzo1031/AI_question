<template>
  <div class="system-config-container">
    <a-card :bordered="false">
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="email" tab="邮件配置">
          <a-spin :spinning="emailLoading">
            <a-form
              :model="emailForm"
              :label-col="{ span: 6 }"
              :wrapper-col="{ span: 12 }"
              ref="emailFormRef"
            >
              <a-form-item label="SMTP服务器" name="smtp_host" :rules="[{ required: true, message: '请输入SMTP服务器地址' }]">
                <a-input v-model:value="emailForm.smtp_host" placeholder="例如: smtp.example.com" />
              </a-form-item>
              
              <a-form-item label="SMTP端口" name="smtp_port" :rules="[{ required: true, message: '请输入SMTP端口' }]">
                <a-input-number v-model:value="emailForm.smtp_port" :min="1" :max="65535" style="width: 100%" />
              </a-form-item>

              <a-form-item label="SMTP用户名" name="smtp_user" :rules="[{ required: true, message: '请输入SMTP用户名' }]">
                <a-input v-model:value="emailForm.smtp_user" />
              </a-form-item>

              <a-form-item label="SMTP密码" name="smtp_password" :rules="[{ required: true, message: '请输入SMTP密码' }]">
                <a-input-password v-model:value="emailForm.smtp_password" />
              </a-form-item>

              <a-form-item label="发件人邮箱" name="smtp_from" :rules="[{ required: true, type: 'email', message: '请输入有效的发件人邮箱' }]">
                <a-input v-model:value="emailForm.smtp_from" />
              </a-form-item>

              <a-form-item label="使用TLS" name="smtp_use_tls">
                <a-switch v-model:checked="emailForm.smtp_use_tls" />
              </a-form-item>

              <a-form-item label="启用邮件服务" name="is_enabled">
                <a-switch v-model:checked="emailForm.is_enabled" />
              </a-form-item>

              <a-form-item :wrapper-col="{ offset: 6, span: 12 }">
                <a-button type="primary" @click="handleSaveEmail" :loading="saveEmailLoading">保存配置</a-button>
                <a-button style="margin-left: 10px" @click="showTestEmailModal">发送测试邮件</a-button>
              </a-form-item>
            </a-form>
          </a-spin>
        </a-tab-pane>
        
        <a-tab-pane key="sms" tab="短信配置">
          <a-spin :spinning="smsLoading">
            <a-form
              :model="smsForm"
              :label-col="{ span: 6 }"
              :wrapper-col="{ span: 12 }"
              ref="smsFormRef"
            >
              <a-form-item label="服务提供商" name="provider" :rules="[{ required: true, message: '请选择服务提供商' }]">
              <a-radio-group v-model:value="smsForm.provider">
                <a-radio value="aliyun">阿里云</a-radio>
                <a-radio value="tencent">腾讯云</a-radio>
              </a-radio-group>
            </a-form-item>

            <template v-if="smsForm.provider === 'aliyun'">
                <a-form-item label="AccessKey ID" name="aliyun_access_key_id" :rules="[{ required: true, message: '请输入AccessKey ID' }]">
                  <a-input v-model:value="smsForm.aliyun_access_key_id" />
                </a-form-item>
                
                <a-form-item label="AccessKey Secret" name="aliyun_access_key_secret" :rules="[{ required: true, message: '请输入AccessKey Secret' }]">
                  <a-input-password v-model:value="smsForm.aliyun_access_key_secret" />
                </a-form-item>

                <a-form-item label="短信签名" name="aliyun_sms_sign_name" :rules="[{ required: true, message: '请输入短信签名' }]">
                  <a-input v-model:value="smsForm.aliyun_sms_sign_name" />
                </a-form-item>

                <a-form-item label="短信模板Code" name="aliyun_sms_template_code" :rules="[{ required: true, message: '请输入短信模板Code' }]">
                  <a-input v-model:value="smsForm.aliyun_sms_template_code" placeholder="例如: SMS_123456789" />
                </a-form-item>

                <a-form-item label="地域 (Region)" name="aliyun_sms_region">
                  <a-input v-model:value="smsForm.aliyun_sms_region" placeholder="默认: cn-hangzhou" />
                </a-form-item>
              </template>

              <template v-if="smsForm.provider === 'tencent'">
              <a-form-item label="SecretId" name="tencent_secret_id" :rules="[{ required: true, message: '请输入SecretId' }]">
                <a-input v-model:value="smsForm.tencent_secret_id" />
              </a-form-item>
              
              <a-form-item label="SecretKey" name="tencent_secret_key" :rules="[{ required: true, message: '请输入SecretKey' }]">
                <a-input-password v-model:value="smsForm.tencent_secret_key" />
              </a-form-item>

              <a-form-item label="SDK AppID" name="tencent_sms_app_id" :rules="[{ required: true, message: '请输入SDK AppID' }]">
                <a-input v-model:value="smsForm.tencent_sms_app_id" />
              </a-form-item>

              <a-form-item label="短信签名" name="tencent_sms_sign_name" :rules="[{ required: true, message: '请输入短信签名' }]">
                <a-input v-model:value="smsForm.tencent_sms_sign_name" />
              </a-form-item>

              <a-form-item label="短信模板ID" name="tencent_sms_template_id" :rules="[{ required: true, message: '请输入短信模板ID' }]">
                <a-input v-model:value="smsForm.tencent_sms_template_id" placeholder="例如: 123456" />
              </a-form-item>
              
              <a-form-item label="地域 (Region)" name="tencent_sms_region">
                <a-input v-model:value="smsForm.tencent_sms_region" placeholder="默认: ap-guangzhou" />
              </a-form-item>
            </template>

              <a-form-item label="启用短信服务" name="is_enabled">
                <a-switch v-model:checked="smsForm.is_enabled" />
              </a-form-item>

              <a-form-item :wrapper-col="{ offset: 6, span: 12 }">
                <a-button type="primary" @click="handleSaveSms" :loading="saveSmsLoading">保存配置</a-button>
                <a-button style="margin-left: 10px" @click="showTestSmsModal">发送测试短信</a-button>
              </a-form-item>
            </a-form>
          </a-spin>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- Test Email Modal -->
    <a-modal
      v-model:open="testEmailVisible"
      title="发送测试邮件"
      @ok="handleTestEmail"
      :confirmLoading="testEmailLoading"
    >
      <a-form :model="testEmailForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="收件人邮箱" required>
          <a-input v-model:value="testEmailForm.to_email" />
        </a-form-item>
        <a-form-item label="邮件主题">
          <a-input v-model:value="testEmailForm.subject" />
        </a-form-item>
        <a-form-item label="邮件内容">
          <a-textarea v-model:value="testEmailForm.content" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Test SMS Modal -->
    <a-modal
      v-model:open="testSmsVisible"
      title="发送测试短信"
      @ok="handleTestSms"
      :confirmLoading="testSmsLoading"
    >
      <a-form :model="testSmsForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="手机号" required>
          <a-input v-model:value="testSmsForm.phone" />
        </a-form-item>
        <a-form-item label="验证码">
          <a-input v-model:value="testSmsForm.code" placeholder="默认: 123456" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { 
  getEmailConfig, updateEmailConfig, testEmailConfig,
  getSmsConfig, updateSmsConfig, testSmsConfig 
} from '../api/systemConfig';

const activeTab = ref('email');

// Email State
const emailLoading = ref(false);
const saveEmailLoading = ref(false);
const emailFormRef = ref(null);
const emailForm = reactive({
  smtp_host: '',
  smtp_port: 465,
  smtp_user: '',
  smtp_password: '',
  smtp_from: '',
  smtp_use_tls: true,
  is_enabled: false
});

// SMS State
const smsLoading = ref(false);
const saveSmsLoading = ref(false);
const smsFormRef = ref(null);
const smsForm = reactive({
  provider: 'aliyun', // 'aliyun' or 'tencent'
  // Aliyun
  aliyun_access_key_id: '',
  aliyun_access_key_secret: '',
  aliyun_sms_sign_name: '',
  aliyun_sms_template_code: '',
  aliyun_sms_region: 'cn-hangzhou',
  // Tencent
  tencent_secret_id: '',
  tencent_secret_key: '',
  tencent_sms_app_id: '',
  tencent_sms_sign_name: '',
  tencent_sms_template_id: '',
  tencent_sms_region: 'ap-guangzhou',
  // Common
  is_enabled: false
});

// Test Email State
const testEmailVisible = ref(false);
const testEmailLoading = ref(false);
const testEmailForm = reactive({
  to_email: '',
  subject: '测试邮件',
  content: '这是一封测试邮件，用于验证邮件配置是否正确。'
});

// Test SMS State
const testSmsVisible = ref(false);
const testSmsLoading = ref(false);
const testSmsForm = reactive({
  phone: '',
  code: '123456'
});

// ============ Email Functions ============

const fetchEmailConfig = async () => {
  emailLoading.value = true;
  try {
    const res = await getEmailConfig();
    if (res.data) {
      Object.assign(emailForm, res.data);
    }
  } catch (error) {
    console.error(error);
  } finally {
    emailLoading.value = false;
  }
};

const handleSaveEmail = async () => {
  try {
    await emailFormRef.value.validate();
    saveEmailLoading.value = true;
    await updateEmailConfig(emailForm);
    message.success('邮件配置已保存');
  } catch (error) {
    console.error(error);
  } finally {
    saveEmailLoading.value = false;
  }
};

const showTestEmailModal = () => {
  testEmailVisible.value = true;
};

const handleTestEmail = async () => {
  if (!testEmailForm.to_email) {
    message.warning('请输入收件人邮箱');
    return;
  }
  testEmailLoading.value = true;
  try {
    await testEmailConfig(testEmailForm);
    message.success('测试邮件发送成功，请查收');
    testEmailVisible.value = false;
  } catch (error) {
    console.error(error);
    message.error('发送失败，请检查配置或日志');
  } finally {
    testEmailLoading.value = false;
  }
};

// ============ SMS Functions ============

const fetchSmsConfig = async () => {
  smsLoading.value = true;
  try {
    const res = await getSmsConfig();
    if (res.data) {
      Object.assign(smsForm, res.data);
    }
  } catch (error) {
    console.error(error);
  } finally {
    smsLoading.value = false;
  }
};

const handleSaveSms = async () => {
  try {
    await smsFormRef.value.validate();
    saveSmsLoading.value = true;
    await updateSmsConfig(smsForm);
    message.success('短信配置已保存');
  } catch (error) {
    console.error(error);
  } finally {
    saveSmsLoading.value = false;
  }
};

const showTestSmsModal = () => {
  testSmsVisible.value = true;
};

const handleTestSms = async () => {
  if (!testSmsForm.phone) {
    message.warning('请输入手机号');
    return;
  }
  testSmsLoading.value = true;
  try {
    await testSmsConfig(testSmsForm);
    message.success('测试短信发送成功');
    testSmsVisible.value = false;
  } catch (error) {
    console.error(error);
    message.error('发送失败，请检查配置或日志');
  } finally {
    testSmsLoading.value = false;
  }
};

onMounted(() => {
  fetchEmailConfig();
  fetchSmsConfig();
});
</script>

<style scoped>
.system-config-container {
  min-height: 100%;
}
</style>
