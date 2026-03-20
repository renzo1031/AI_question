<template>
  <a-config-provider
    :theme="{
      token: {
        colorPrimary: '#1677FF',
        colorSuccess: '#52C41A',
        colorWarning: '#FAAD14',
        colorError: '#FF4D4F',
        colorInfo: '#1677FF',
        colorText: '#333333',
        colorTextSecondary: '#8C8C8C',
        colorTextDisabled: '#BFBFBF',
        colorBgLayout: '#F5F7FA',
        colorBgContainer: '#FFFFFF',
        colorBorder: '#E5E6EB',
      },
    }"
  >
    <router-view />
  </a-config-provider>
</template>

<script setup>
import { theme } from 'ant-design-vue';
</script>

<style>
#app {
  height: 100vh;
}
</style>
