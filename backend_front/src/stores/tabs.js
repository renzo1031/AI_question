import { defineStore } from 'pinia';
import router from '../router';

export const useTabsStore = defineStore('tabs', {
  state: () => ({
    tabsList: [
      { title: '首页', path: '/', name: 'home' }
    ],
    activeKey: '/'
  }),
  actions: {
    // 添加标签页
    addTab(route) {
      const isExist = this.tabsList.some(item => item.path === route.path);
      if (!isExist && route.meta.title) {
        this.tabsList.push({
          title: route.meta.title,
          path: route.path,
          name: route.name
        });
      }
      this.activeKey = route.path;
    },
    // 移除标签页
    removeTab(targetKey) {
      // 首页不能关闭
      if (targetKey === '/') return;
      
      const index = this.tabsList.findIndex(item => item.path === targetKey);
      if (index !== -1) {
        this.tabsList.splice(index, 1);
        // 如果关闭的是当前激活的 tab，则跳转到最后一个 tab
        if (this.activeKey === targetKey) {
          const nextTab = this.tabsList[this.tabsList.length - 1];
          this.activeKey = nextTab.path;
          router.push(nextTab.path);
        }
      }
    },
    // 设置当前激活的 tab
    setActiveTab(path) {
      this.activeKey = path;
    }
  }
});
