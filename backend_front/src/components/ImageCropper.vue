<template>
  <a-modal
    :open="visible"
    title="裁剪图片"
    ok-text="确定裁剪"
    cancel-text="取消"
    @ok="handleConfirm"
    @cancel="emit('update:visible', false)"
    :confirmLoading="processing"
    width="800px"
    :destroyOnClose="true"
    :maskClosable="false"
  >
    <div
      ref="wrapperRef"
      class="icp-wrapper"
      :style="{ width: WRAP_W + 'px', height: WRAP_H + 'px' }"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
    >
      <!-- 背景暗色遮罩 -->
      <div class="icp-mask" />

      <!-- 原始图片 -->
      <img
        ref="imgRef"
        :src="imageSrc"
        class="icp-img"
        :style="imgStyle"
        @load="onImgLoad"
        draggable="false"
      />

      <!-- 裁剪框（固定 5:4 比例，可缩放） -->
      <div
        v-if="ready"
        class="icp-box"
        :style="boxStyle"
        @mousedown.stop="startMove($event)"
      >
        <!-- 三分法辅助线 -->
        <div class="icp-grid icp-grid-h1" />
        <div class="icp-grid icp-grid-h2" />
        <div class="icp-grid icp-grid-v1" />
        <div class="icp-grid icp-grid-v2" />

        <!-- 4 个角落缩放手柄（保持 5:4 比例） -->
        <div
          v-for="h in HANDLES"
          :key="h"
          :class="['icp-handle', `icp-handle-${h}`]"
          @mousedown.stop="startResize(h, $event)"
        />
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="icp-toolbar">
      <a-space>
        <a-button size="small" @click="doScale(0.15)">
          <zoom-in-outlined /> 放大
        </a-button>
        <a-button size="small" @click="doScale(-0.15)">
          <zoom-out-outlined /> 缩小
        </a-button>
        <a-button size="small" @click="initDisplay">
          <reload-outlined /> 重置
        </a-button>
      </a-space>
      <span v-if="ready" class="icp-size-hint">
        裁剪尺寸：{{ cropNatW }} × {{ cropNatH }} px
      </span>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ZoomInOutlined, ZoomOutOutlined, ReloadOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  visible: Boolean,
  imageSrc: String,
})

const emit = defineEmits(['update:visible', 'confirm'])

const WRAP_W = 720
const WRAP_H = 380
// 固定裁剪比例 5:4
const ASPECT = 5 / 4
// 最小裁剪宽度（高度按比例自动算）
const MIN_BOX = 40
// 只保留四个角手柄，方便做固定比例缩放
const HANDLES = ['nw', 'ne', 'se', 'sw']

const wrapperRef = ref(null)
const imgRef = ref(null)
const processing = ref(false)
const ready = ref(false)

// 原始图片尺寸
const nat = reactive({ w: 0, h: 0 })
// 显示区域内图片的位置和尺寸
const disp = reactive({ x: 0, y: 0, w: 0, h: 0 })
// 当前缩放比例
const zoom = ref(1)
// 裁剪框（相对于 wrapper 的坐标）
const box = reactive({ x: 0, y: 0, w: 0, h: 0 })

const imgStyle = computed(() => ({
  position: 'absolute',
  left: `${disp.x}px`,
  top: `${disp.y}px`,
  width: `${disp.w}px`,
  height: `${disp.h}px`,
  userSelect: 'none',
  pointerEvents: 'none',
}))

const boxStyle = computed(() => ({
  left: `${box.x}px`,
  top: `${box.y}px`,
  width: `${box.w}px`,
  height: `${box.h}px`,
}))

// 将裁剪框坐标换算为原图坐标
const cropNatW = computed(() => Math.round((box.w / disp.w) * nat.w))
const cropNatH = computed(() => Math.round((box.h / disp.h) * nat.h))

const onImgLoad = () => {
  const img = imgRef.value
  nat.w = img.naturalWidth
  nat.h = img.naturalHeight
  initDisplay()
}

const initDisplay = () => {
  const scaleW = WRAP_W / nat.w
  const scaleH = WRAP_H / nat.h
  const s = Math.min(scaleW, scaleH, 1)
  zoom.value = s

  disp.w = Math.round(nat.w * s)
  disp.h = Math.round(nat.h * s)
  disp.x = Math.round((WRAP_W - disp.w) / 2)
  disp.y = Math.round((WRAP_H - disp.h) / 2)

  // 在当前图片区域内，取最大 5:4 的矩形作为裁剪框，并居中
  const byHeightW = disp.h * ASPECT
  const byWidthH = disp.w / ASPECT

  if (byHeightW <= disp.w) {
    // 以高度为基准
    box.w = Math.round(byHeightW)
    box.h = disp.h
  } else {
    // 以宽度为基准
    box.w = disp.w
    box.h = Math.round(byWidthH)
  }

  box.x = Math.round(disp.x + (disp.w - box.w) / 2)
  box.y = Math.round(disp.y + (disp.h - box.h) / 2)

  ready.value = true
}

const doScale = (delta) => {
  const newZoom = Math.max(0.05, Math.min(5, zoom.value + delta))
  const ratio = newZoom / zoom.value
  zoom.value = newZoom

  const oldW = disp.w
  const oldH = disp.h
  disp.w = Math.round(nat.w * newZoom)
  disp.h = Math.round(nat.h * newZoom)
  disp.x = Math.round(disp.x - (disp.w - oldW) / 2)
  disp.y = Math.round(disp.y - (disp.h - oldH) / 2)

  // 同比缩放裁剪框，保持 5:4 比例
  const cx = box.x + box.w / 2
  const cy = box.y + box.h / 2
  let newW = Math.round(box.w * ratio)
  let newH = Math.round(newW / ASPECT)

  // 尽量保持中心点不变
  box.w = newW
  box.h = newH
  box.x = Math.round(cx - box.w / 2)
  box.y = Math.round(cy - box.h / 2)

  clampBox()
}

// 将裁剪框限制在图片范围内（宽高不超过图片，保持 5:4）
const clampBox = () => {
  // 若裁剪框比图片大，整体按比例缩小
  if (box.w > disp.w || box.h > disp.h) {
    const scale = Math.min(disp.w / box.w, disp.h / box.h)
    box.w = Math.max(MIN_BOX, Math.round(box.w * scale))
    box.h = Math.round(box.w / ASPECT)
  }

  if (box.x < disp.x) box.x = disp.x
  if (box.y < disp.y) box.y = disp.y
  if (box.x + box.w > disp.x + disp.w) {
    box.x = disp.x + disp.w - box.w
  }
  if (box.y + box.h > disp.y + disp.h) {
    box.y = disp.y + disp.h - box.h
  }
}

// 拖拽 / 缩放状态
let drag = null

const getCoords = (e) => {
  const rect = wrapperRef.value.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

const startMove = (e) => {
  const { x, y } = getCoords(e)
  drag = { type: 'move', startX: x, startY: y, startBox: { ...box } }
}

const startResize = (handle, e) => {
  const { x, y } = getCoords(e)
  drag = { type: 'resize', handle, startX: x, startY: y, startBox: { ...box } }
}

const onMouseMove = (e) => {
  if (!drag) return
  const { x, y } = getCoords(e)
  const dx = x - drag.startX
  const dy = y - drag.startY
  const sb = drag.startBox

  if (drag.type === 'move') {
    box.x = sb.x + dx
    box.y = sb.y + dy
    clampBox()
    return
  }

  if (drag.type === 'resize') {
    const h = drag.handle
    const fromEast = h.includes('e')
    const fromSouth = h.includes('s')

    // 统一成“向外拉”的增量（右 / 下 为正）
    const sx = fromEast ? dx : -dx
    const sy = fromSouth ? dy : -dy
    // 取更大的那个，避免比例错位
    let delta = Math.max(sx, sy)

    let newW = sb.w + delta
    if (newW < MIN_BOX) newW = MIN_BOX
    let newH = Math.round(newW / ASPECT)

    // 计算新位置：根据手柄方向吸附另一侧
    let nx = sb.x
    let ny = sb.y

    if (!fromEast) {
      // 从左侧缩放，右侧保持不动
      nx = sb.x + (sb.w - newW)
    }
    if (!fromSouth) {
      // 从上侧缩放，下侧保持不动
      ny = sb.y + (sb.h - newH)
    }

    // 限制在图片范围内：左 / 上
    if (nx < disp.x) {
      const over = disp.x - nx
      newW -= over
      if (newW < MIN_BOX) newW = MIN_BOX
      newH = Math.round(newW / ASPECT)
      nx = disp.x
      if (!fromSouth) {
        ny = sb.y + (sb.h - newH)
      }
    }

    if (ny < disp.y) {
      const over = disp.y - ny
      newH -= over
      if (newH < MIN_BOX / ASPECT) newH = MIN_BOX / ASPECT
      newW = Math.round(newH * ASPECT)
      ny = disp.y
      if (!fromEast) {
        nx = sb.x + (sb.w - newW)
      }
    }

    // 限制在图片范围内：右 / 下
    if (nx + newW > disp.x + disp.w) {
      const over = nx + newW - (disp.x + disp.w)
      newW -= over
      if (newW < MIN_BOX) newW = MIN_BOX
      newH = Math.round(newW / ASPECT)
      if (!fromSouth) {
        ny = sb.y + (sb.h - newH)
      }
    }

    if (ny + newH > disp.y + disp.h) {
      const over = ny + newH - (disp.y + disp.h)
      newH -= over
      if (newH < MIN_BOX / ASPECT) newH = MIN_BOX / ASPECT
      newW = Math.round(newH * ASPECT)
      if (!fromEast) {
        nx = sb.x + (sb.w - newW)
      }
    }

    box.x = nx
    box.y = ny
    box.w = newW
    box.h = newH
  }
}

const onMouseUp = () => { drag = null }

const handleConfirm = () => {
  processing.value = true

  const scaleX = nat.w / disp.w
  const scaleY = nat.h / disp.h

  const srcX = Math.max(0, Math.round((box.x - disp.x) * scaleX))
  const srcY = Math.max(0, Math.round((box.y - disp.y) * scaleY))
  const srcW = Math.min(nat.w - srcX, Math.round(box.w * scaleX))
  const srcH = Math.min(nat.h - srcY, Math.round(box.h * scaleY))

  const canvas = document.createElement('canvas')
  canvas.width = srcW
  canvas.height = srcH
  const ctx = canvas.getContext('2d')

  const img = new Image()
  img.onload = () => {
    ctx.drawImage(img, srcX, srcY, srcW, srcH, 0, 0, srcW, srcH)
    canvas.toBlob(
      (blob) => {
        emit('confirm', blob)
        emit('update:visible', false)
        processing.value = false
      },
      'image/jpeg',
      0.92,
    )
  }
  img.src = props.imageSrc
}

watch(
  () => props.imageSrc,
  () => { ready.value = false },
)
</script>

<style scoped>
.icp-wrapper {
  position: relative;
  overflow: hidden;
  background: #1a1a1a;
  cursor: crosshair;
  user-select: none;
}

.icp-mask {
  position: absolute;
  inset: 0;
  background: transparent;
  z-index: 1;
}

.icp-img {
  z-index: 2;
}

/* 裁剪框：用 box-shadow 实现四周暗色遮罩 */
.icp-box {
  position: absolute;
  z-index: 3;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.55);
  border: 1.5px solid rgba(255, 255, 255, 0.9);
  cursor: move;
}

/* 三分法辅助线 */
.icp-grid {
  position: absolute;
  background: transparent;
  pointer-events: none;
}
.icp-grid-h1 { top: 33.33%; left: 0; right: 0; height: 1px; border-top: 1px dashed rgba(255, 255, 255, 0.4); }
.icp-grid-h2 { top: 66.66%; left: 0; right: 0; height: 1px; border-top: 1px dashed rgba(255, 255, 255, 0.4); }
.icp-grid-v1 { left: 33.33%; top: 0; bottom: 0; width: 1px; border-left: 1px dashed rgba(255, 255, 255, 0.4); }
.icp-grid-v2 { left: 66.66%; top: 0; bottom: 0; width: 1px; border-left: 1px dashed rgba(255, 255, 255, 0.4); }

/* 8个手柄 */
.icp-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #fff;
  border: 1.5px solid #1677ff;
  border-radius: 1px;
}
.icp-handle-nw { top: -5px; left: -5px; cursor: nw-resize; }
.icp-handle-n  { top: -5px; left: calc(50% - 5px); cursor: n-resize; }
.icp-handle-ne { top: -5px; right: -5px; cursor: ne-resize; }
.icp-handle-e  { top: calc(50% - 5px); right: -5px; cursor: e-resize; }
.icp-handle-se { bottom: -5px; right: -5px; cursor: se-resize; }
.icp-handle-s  { bottom: -5px; left: calc(50% - 5px); cursor: s-resize; }
.icp-handle-sw { bottom: -5px; left: -5px; cursor: sw-resize; }
.icp-handle-w  { top: calc(50% - 5px); left: -5px; cursor: w-resize; }

/* 工具栏 */
.icp-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0 4px;
}

.icp-size-hint {
  font-size: 12px;
  color: #999;
}
</style>
