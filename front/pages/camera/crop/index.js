Page({
  data: {
    src: "",
    statusBarHeight: 0,
    navHeight: 0,
    sideWidth: 0,
    stageH: 0,
    areaW: 0,
    areaH: 0,
    imgW: 0,
    imgH: 0,
    ratio: 1,
    cropX: 0,
    cropY: 0,
    cropW: 0,
    cropH: 0,
    touching: false,
    touchType: "",
    handle: "",
    startClientX: 0,
    startClientY: 0,
    startCropX: 0,
    startCropY: 0,
    startCropW: 0,
    startCropH: 0,
    canvasW: 1,
    canvasH: 1,
    busy: false
  },

  onLoad(query) {
    const sysInfo = wx.getWindowInfo();
    const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
    const statusBarHeight = sysInfo.statusBarHeight || 0;
    const navBarHeight = (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height;
    const navHeight = statusBarHeight + navBarHeight;
    const sideWidth = Math.max(88, Math.round(sysInfo.windowWidth - menuButtonInfo.left));

    const src = query && query.src ? decodeURIComponent(query.src) : "";

    this.setData({
      src,
      statusBarHeight,
      navHeight,
      sideWidth
    });

    if (!src) {
      wx.showToast({ title: "图片无效", icon: "none" });
      setTimeout(() => wx.navigateBack(), 800);
      return;
    }

    const bottomBarH = 160;
    const stageH = Math.max(240, sysInfo.windowHeight - navHeight - bottomBarH);
    this.setData({ stageH });

    wx.getImageInfo({
      src,
      success: (info) => {
        const maxW = sysInfo.windowWidth;
        const maxH = stageH;
        const imgW = info.width || maxW;
        const imgH = info.height || maxH;

        let areaW = maxW;
        let areaH = Math.round((areaW * imgH) / imgW);
        if (areaH > maxH) {
          areaH = maxH;
          areaW = Math.round((areaH * imgW) / imgH);
        }

        const minSize = Math.min(240, Math.round(areaW * 0.4));
        const cropW = Math.max(minSize, Math.round(areaW * 0.86));
        const cropH = Math.max(minSize, Math.round(Math.min(areaH * 0.5, areaW * 0.62)));
        const cropX = Math.round((areaW - cropW) / 2);
        const cropY = Math.round((areaH - cropH) / 2);

        this.setData({
          imgW,
          imgH,
          areaW,
          areaH,
          ratio: imgW / areaW,
          cropX,
          cropY,
          cropW,
          cropH
        });
      },
      fail: () => {
        wx.showToast({ title: "读取图片失败", icon: "none" });
        setTimeout(() => wx.navigateBack(), 1200);
      }
    });
  },

  cancel() {
    const channel = this.getOpenerEventChannel && this.getOpenerEventChannel();
    if (channel && channel.emit) channel.emit("canceled", {});
    wx.navigateBack();
  },

  onBoxTouchStart(e) {
    if (this.data.busy) return;
    const touch = e && e.touches && e.touches[0];
    if (!touch) return;
    this.setData({
      touching: true,
      touchType: "move",
      handle: "",
      startClientX: touch.clientX,
      startClientY: touch.clientY,
      startCropX: this.data.cropX,
      startCropY: this.data.cropY,
      startCropW: this.data.cropW,
      startCropH: this.data.cropH
    });
  },

  onBoxTouchMove(e) {
    if (!this.data.touching || this.data.touchType !== "move") return;
    const touch = e && e.touches && e.touches[0];
    if (!touch) return;
    const dx = touch.clientX - this.data.startClientX;
    const dy = touch.clientY - this.data.startClientY;
    const maxX = Math.max(0, this.data.areaW - this.data.cropW);
    const maxY = Math.max(0, this.data.areaH - this.data.cropH);
    const nextX = Math.min(maxX, Math.max(0, Math.round(this.data.startCropX + dx)));
    const nextY = Math.min(maxY, Math.max(0, Math.round(this.data.startCropY + dy)));
    this.setData({ cropX: nextX, cropY: nextY });
  },

  onHandleTouchStart(e) {
    if (this.data.busy) return;
    const touch = e && e.touches && e.touches[0];
    if (!touch) return;
    const handle = e && e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.h;
    if (!handle) return;
    this.setData({
      touching: true,
      touchType: "resize",
      handle,
      startClientX: touch.clientX,
      startClientY: touch.clientY,
      startCropX: this.data.cropX,
      startCropY: this.data.cropY,
      startCropW: this.data.cropW,
      startCropH: this.data.cropH
    });
  },

  onHandleTouchMove(e) {
    if (!this.data.touching || this.data.touchType !== "resize") return;
    const touch = e && e.touches && e.touches[0];
    if (!touch) return;
    const dx = touch.clientX - this.data.startClientX;
    const dy = touch.clientY - this.data.startClientY;
    const handle = this.data.handle;
    const minSize = 40;

    let x = this.data.startCropX;
    let y = this.data.startCropY;
    let w = this.data.startCropW;
    let h = this.data.startCropH;

    if (handle === "nw") {
      x = this.data.startCropX + dx;
      y = this.data.startCropY + dy;
      w = this.data.startCropW - dx;
      h = this.data.startCropH - dy;
    } else if (handle === "ne") {
      y = this.data.startCropY + dy;
      w = this.data.startCropW + dx;
      h = this.data.startCropH - dy;
    } else if (handle === "sw") {
      x = this.data.startCropX + dx;
      w = this.data.startCropW - dx;
      h = this.data.startCropH + dy;
    } else if (handle === "se") {
      w = this.data.startCropW + dx;
      h = this.data.startCropH + dy;
    } else if (handle === "n") {
      y = this.data.startCropY + dy;
      h = this.data.startCropH - dy;
    } else if (handle === "s") {
      h = this.data.startCropH + dy;
    } else if (handle === "w") {
      x = this.data.startCropX + dx;
      w = this.data.startCropW - dx;
    } else if (handle === "e") {
      w = this.data.startCropW + dx;
    }

    if (w < minSize) {
      const d = minSize - w;
      w = minSize;
      if (handle === "nw" || handle === "sw" || handle === "w") x -= d;
    }
    if (h < minSize) {
      const d = minSize - h;
      h = minSize;
      if (handle === "nw" || handle === "ne" || handle === "n") y -= d;
    }

    if (x < 0) {
      const d = -x;
      x = 0;
      if (handle === "nw" || handle === "sw" || handle === "w") w -= d;
    }
    if (y < 0) {
      const d = -y;
      y = 0;
      if (handle === "nw" || handle === "ne" || handle === "n") h -= d;
    }

    if (x + w > this.data.areaW) {
      const overflow = x + w - this.data.areaW;
      if (handle === "ne" || handle === "se" || handle === "e") w -= overflow;
      if (handle === "nw" || handle === "sw" || handle === "w") {
        x -= overflow;
        if (x < 0) x = 0;
      }
    }
    if (y + h > this.data.areaH) {
      const overflow = y + h - this.data.areaH;
      if (handle === "sw" || handle === "se" || handle === "s") h -= overflow;
      if (handle === "nw" || handle === "ne" || handle === "n") {
        y -= overflow;
        if (y < 0) y = 0;
      }
    }

    w = Math.max(minSize, Math.min(w, this.data.areaW));
    h = Math.max(minSize, Math.min(h, this.data.areaH));
    x = Math.min(this.data.areaW - w, Math.max(0, Math.round(x)));
    y = Math.min(this.data.areaH - h, Math.max(0, Math.round(y)));

    this.setData({
      cropX: x,
      cropY: y,
      cropW: Math.round(w),
      cropH: Math.round(h)
    });
  },

  onTouchEnd() {
    if (!this.data.touching) return;
    this.setData({ touching: false, touchType: "", handle: "" });
  },

  confirm() {
    if (this.data.busy) return;
    if (!this.data.src || !this.data.areaW || !this.data.areaH) return;

    const ratio = this.data.ratio || 1;
    const sx = Math.max(0, Math.round(this.data.cropX * ratio));
    const sy = Math.max(0, Math.round(this.data.cropY * ratio));
    const sw = Math.max(1, Math.round(this.data.cropW * ratio));
    const sh = Math.max(1, Math.round(this.data.cropH * ratio));

    const outputMax = 1400;
    const outScale = Math.min(1, outputMax / Math.max(sw, sh));
    const outW = Math.max(1, Math.round(sw * outScale));
    const outH = Math.max(1, Math.round(sh * outScale));

    this.setData({ busy: true, canvasW: outW, canvasH: outH });
    wx.showLoading({ title: "裁剪中..." });

    // 使用 Canvas 2D 接口
    const query = wx.createSelectorQuery().in(this);
    query.select('#cropCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res[0] || !res[0].node) {
          this.setData({ busy: false });
          wx.hideLoading();
          wx.showToast({ title: "Canvas初始化失败", icon: "none" });
          return;
        }

        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');
        const dpr = wx.getWindowInfo().pixelRatio || 1;

        // 设置画布物理尺寸
        canvas.width = outW * dpr;
        canvas.height = outH * dpr;
        ctx.scale(dpr, dpr);

        // 创建图片对象加载图片
        const img = canvas.createImage();
        img.src = this.data.src;
        img.onload = () => {
          ctx.clearRect(0, 0, outW, outH);
          ctx.drawImage(img, sx, sy, sw, sh, 0, 0, outW, outH);

          wx.canvasToTempFilePath({
            canvas: canvas,
            width: outW,
            height: outH,
            destWidth: outW,
            destHeight: outH,
            fileType: 'jpg',
            quality: 0.9,
            success: (res) => {
              wx.hideLoading();
              const path = res.tempFilePath;
              this.returnPath(path);
            },
            fail: (err) => {
              console.error(err);
              wx.hideLoading();
              this.setData({ busy: false });
              wx.showToast({ title: "导出图片失败", icon: "none" });
            }
          });
        };

        img.onerror = (err) => {
          console.error(err);
          wx.hideLoading();
          this.setData({ busy: false });
          wx.showToast({ title: "加载图片失败", icon: "none" });
        };
      });
  },

  preview() {
    const url = this.data.src;
    if (!url) return;
    wx.previewImage({ urls: [url], current: url });
  },

  returnPath(path) {
    if (path) {
      wx.setStorageSync('searchImagePath', path);
      wx.setStorageSync('search_pending', true);
      wx.removeStorageSync('searchResult');
    }
    wx.navigateBack();
  }
});
