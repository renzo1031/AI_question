from pathlib import Path


OUT_DIR = Path(r"C:\Users\renzhong\Desktop\Code\AI_question\docs\images\ch05")


BG = "#f8fafc"
CARD = "#ffffff"
BORDER = "#1f2937"
PRIMARY = "#0f766e"
SECONDARY = "#1d4ed8"
ACCENT = "#b45309"
TEXT = "#0f172a"
MUTED = "#475569"
GRID = "#cbd5e1"


def wrap_text(text: str, width: int) -> list[str]:
    lines = []
    current = ""
    for ch in text:
        if ch == "\n":
            lines.append(current)
            current = ""
            continue
        current += ch
        if len(current) >= width:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines or [text]


def text_block(x: int, y: int, text: str, size: int = 20, fill: str = TEXT, bold: bool = False, anchor: str = "middle") -> str:
    weight = "700" if bold else "400"
    lines = text.split("\n")
    tspan = []
    for idx, line in enumerate(lines):
        dy = "0" if idx == 0 else "1.3em"
        tspan.append(
            f'<tspan x="{x}" dy="{dy}">{line}</tspan>'
        )
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'font-family="Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif" '
        f'font-weight="{weight}" fill="{fill}">{"".join(tspan)}</text>'
    )


def rect(x: int, y: int, w: int, h: int, title: str, subtitle: str = "", fill: str = CARD, stroke: str = BORDER) -> str:
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" ry="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
        text_block(x + w // 2, y + 36, title, size=22, fill=TEXT, bold=True),
    ]
    if subtitle:
        wrapped = wrap_text(subtitle, 18)
        parts.append(text_block(x + w // 2, y + 68, "\n".join(wrapped), size=16, fill=MUTED))
    return "\n".join(parts)


def container(x: int, y: int, w: int, h: int, title: str, stroke: str) -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" ry="24" fill="none" stroke="{stroke}" stroke-width="3" stroke-dasharray="10 8"/>',
            text_block(x + 20, y + 34, title, size=22, fill=stroke, bold=True, anchor="start"),
        ]
    )


def arrow(x1: int, y1: int, x2: int, y2: int, label: str = "", color: str = BORDER, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="10 8"' if dashed else ""
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3" marker-end="url(#arrow)"{dash}/>'
    if not label:
        return line
    lx = (x1 + x2) // 2
    ly = (y1 + y2) // 2 - 10
    label_bg = f'<rect x="{lx - 62}" y="{ly - 18}" width="124" height="28" rx="10" fill="{BG}" stroke="none"/>'
    return "\n".join([line, label_bg, text_block(lx, ly + 2, label, size=15, fill=color, bold=True)])


def svg_shell(title: str, body: str, width: int = 1600, height: int = 900) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{BORDER}" />
    </marker>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#eff6ff" />
      <stop offset="55%" stop-color="#f8fafc" />
      <stop offset="100%" stop-color="#ecfeff" />
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bgGrad)"/>
  <rect x="20" y="20" width="{width-40}" height="{height-40}" rx="26" fill="{BG}" stroke="{GRID}" stroke-width="2"/>
  {text_block(width // 2, 58, title, size=30, fill=TEXT, bold=True)}
  {body}
</svg>
"""


def write(name: str, content: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(content, encoding="utf-8")


def fig_5_1() -> None:
    body = "\n".join(
        [
            container(60, 110, 680, 710, "学生端功能域", PRIMARY),
            container(860, 110, 680, 710, "管理端功能域", SECONDARY),
            rect(110, 190, 230, 120, "注册登录", "验证码校验\nJWT+刷新令牌", fill="#ecfeff", stroke=PRIMARY),
            rect(395, 190, 230, 120, "在线练习", "题库优先\nAI补题", fill="#f0fdf4", stroke=PRIMARY),
            rect(110, 390, 230, 120, "错题本", "错题记录\n错题再练", fill="#fff7ed", stroke=ACCENT),
            rect(395, 390, 230, 120, "学习分析", "概览统计\n薄弱点识别", fill="#fefce8", stroke=ACCENT),
            rect(250, 590, 230, 120, "拍照搜题 + AI解题", "OCR识别\n缓存去重入库", fill="#eff6ff", stroke=SECONDARY),
            rect(910, 190, 230, 120, "用户管理", "检索、禁用、\n重置密码", fill="#eff6ff", stroke=SECONDARY),
            rect(1195, 190, 230, 120, "题库管理", "题目维护\n标签管理", fill="#eef2ff", stroke=SECONDARY),
            rect(910, 390, 230, 120, "知识点管理", "年级、学科、\n知识点三级维护", fill="#ecfeff", stroke=PRIMARY),
            rect(1195, 390, 230, 120, "公告管理", "启停控制\n时间窗口", fill="#fff7ed", stroke=ACCENT),
            rect(650, 320, 300, 180, "统一业务中台", "FastAPI接口层\nService业务编排\nRepository数据访问", fill="#ffffff", stroke=BORDER),
            rect(650, 570, 300, 140, "基础支撑", "PostgreSQL  +  Redis  +  多模型管理", fill="#ffffff", stroke=BORDER),
            arrow(340, 250, 650, 360, "业务调用"),
            arrow(625, 250, 650, 360, "题目编排"),
            arrow(340, 450, 650, 420, "学习数据"),
            arrow(625, 450, 650, 420, "统计反馈"),
            arrow(480, 650, 650, 650, "搜题入库"),
            arrow(950, 360, 1140, 250, "后台操作"),
            arrow(1140, 250, 1195, 250, ""),
            arrow(950, 450, 1140, 450, "配置维护"),
            arrow(1140, 450, 1195, 450, ""),
            arrow(800, 500, 800, 570, "数据落库"),
        ]
    )
    write("fig5-1-overview.svg", svg_shell("图5-1 系统功能实现总览图", body))


def fig_5_2() -> None:
    body = "\n".join(
        [
            rect(90, 280, 200, 120, "用户提交注册/登录", "手机号、邮箱、密码\n或验证码", fill="#ecfeff", stroke=PRIMARY),
            rect(360, 280, 220, 120, "验证码服务", "Redis校验有效期\n频率与日限额", fill="#fff7ed", stroke=ACCENT),
            rect(650, 280, 220, 120, "用户服务", "检查账号状态\n校验密码/验证码", fill="#eff6ff", stroke=SECONDARY),
            rect(940, 280, 220, 120, "数据层", "users表\n更新登录时间", fill="#f8fafc", stroke=BORDER),
            rect(1230, 280, 240, 120, "Token签发与返回", "JWT载荷生成\nSM4加密后返回", fill="#f0fdf4", stroke=PRIMARY),
            rect(650, 520, 220, 110, "刷新/退出/重置密码", "RefreshToken校验\n黑名单控制", fill="#fefce8", stroke=ACCENT),
            arrow(290, 340, 360, 340, "发送/校验"),
            arrow(580, 340, 650, 340, "通过后继续"),
            arrow(870, 340, 940, 340, "查询/更新"),
            arrow(1160, 340, 1230, 340, "签发响应"),
            arrow(760, 400, 760, 520, "认证维护"),
            text_block(800, 170, "手机号注册、邮箱注册、密码登录、验证码登录共用统一认证服务", size=20, fill=MUTED, bold=False),
        ]
    )
    write("fig5-2-auth-flow.svg", svg_shell("图5-2 学生端注册与登录流程图", body))


def fig_5_3() -> None:
    body = "\n".join(
        [
            rect(120, 180, 240, 120, "在线练习提交答案", "学生完成作答", fill="#ecfeff", stroke=PRIMARY),
            rect(440, 180, 240, 120, "判题服务", "按题型比较答案\n得到正误结果", fill="#eff6ff", stroke=SECONDARY),
            rect(760, 180, 240, 120, "答题记录写入", "更新status、wrong_count\nlast_answer_at", fill="#fff7ed", stroke=ACCENT),
            rect(1080, 180, 300, 120, "user_questions错题沉淀", "保留错误次数与最近作答信息", fill="#fefce8", stroke=ACCENT),
            rect(260, 470, 260, 120, "错题本列表查询", "按学科、年级、章节\n知识点、难度筛选", fill="#f0fdf4", stroke=PRIMARY),
            rect(650, 470, 260, 120, "错题再练出题", "优先抽取错题\n不足时回退题库", fill="#eef2ff", stroke=SECONDARY),
            rect(1040, 470, 260, 120, "AI补题", "仍不足时生成新题\n并再次入库", fill="#ffffff", stroke=BORDER),
            arrow(360, 240, 440, 240, "提交答案"),
            arrow(680, 240, 760, 240, "判题结果"),
            arrow(1000, 240, 1080, 240, "沉淀错题"),
            arrow(1230, 300, 1170, 470, "错题查询"),
            arrow(520, 530, 650, 530, "生成复习集"),
            arrow(910, 530, 1040, 530, "数量不足"),
            arrow(1170, 470, 910, 470, "补齐后返回", dashed=True),
        ]
    )
    write("fig5-3-wrongbook-flow.svg", svg_shell("图5-3 错题本生成与错题再练流程图", body))


def fig_5_4() -> None:
    body = "\n".join(
        [
            rect(80, 320, 220, 120, "学生上传题目图片", "URL / Base64 / 文件上传", fill="#ecfeff", stroke=PRIMARY),
            rect(360, 320, 220, 120, "图片预处理", "清理Base64前缀\n二进制解码", fill="#f8fafc", stroke=BORDER),
            rect(640, 320, 240, 120, "阿里云OCR识别", "asyncio.to_thread\n避免阻塞主循环", fill="#eff6ff", stroke=SECONDARY),
            rect(940, 320, 240, 120, "识别结果整理", "content、figure、width\nheight、wordsInfo", fill="#fff7ed", stroke=ACCENT),
            rect(1240, 320, 260, 120, "AI解题与自动入库", "进入统一搜题服务\n返回 question_id", fill="#f0fdf4", stroke=PRIMARY),
            arrow(300, 380, 360, 380, "输入"),
            arrow(580, 380, 640, 380, "调用OCR"),
            arrow(880, 380, 940, 380, "结构化结果"),
            arrow(1180, 380, 1240, 380, "继续解题"),
            text_block(800, 180, "拍照搜题链路将图片输入转为结构化题干，再进入AI求解与题库沉淀流程", size=20, fill=MUTED),
        ]
    )
    write("fig5-4-photo-ocr-flow.svg", svg_shell("图5-4 拍照搜题与OCR识别流程图", body))


def fig_5_5() -> None:
    body = "\n".join(
        [
            rect(120, 260, 220, 120, "管理员登录", "Session Cookie\nRedis会话", fill="#eff6ff", stroke=SECONDARY),
            rect(420, 260, 240, 120, "用户列表与检索", "关键词、状态、注册时间\n最后登录时间筛选", fill="#ecfeff", stroke=PRIMARY),
            rect(740, 160, 240, 120, "用户详情查看", "基础信息\n学习数据入口", fill="#f8fafc", stroke=BORDER),
            rect(740, 360, 240, 120, "状态控制", "启用 / 禁用\n记录禁用原因", fill="#fff7ed", stroke=ACCENT),
            rect(1060, 160, 240, 120, "密码重置", "异常账号恢复\n忘记密码处理", fill="#fefce8", stroke=ACCENT),
            rect(1060, 360, 300, 120, "学习数据查看", "概览、能力分析、\n进步反馈后台查看", fill="#f0fdf4", stroke=PRIMARY),
            arrow(340, 320, 420, 320, "鉴权后访问"),
            arrow(660, 300, 740, 220, "查看详情"),
            arrow(660, 340, 740, 420, "状态管理"),
            arrow(980, 220, 1060, 220, "重置密码"),
            arrow(980, 420, 1060, 420, "查看学习表现"),
        ]
    )
    write("fig5-5-admin-user-flow.svg", svg_shell("图5-5 管理端用户管理流程图", body))


def fig_5_6() -> None:
    body = "\n".join(
        [
            rect(100, 300, 240, 120, "管理员编辑公告", "标题、内容、时间窗口\n排序与启用状态", fill="#eff6ff", stroke=SECONDARY),
            rect(420, 300, 240, 120, "公告服务校验", "start_at <= end_at\n字段合法性检查", fill="#ecfeff", stroke=PRIMARY),
            rect(740, 300, 240, 120, "announcements表", "保存创建人、更新人\n生效与失效时间", fill="#f8fafc", stroke=BORDER),
            rect(1060, 300, 240, 120, "启停与排序控制", "后台可单独启用/停用", fill="#fff7ed", stroke=ACCENT),
            rect(1380, 300, 160, 120, "前台读取", "仅返回当前有效公告", fill="#f0fdf4", stroke=PRIMARY),
            arrow(340, 360, 420, 360, "提交"),
            arrow(660, 360, 740, 360, "校验通过"),
            arrow(980, 360, 1060, 360, "状态维护"),
            arrow(1300, 360, 1380, 360, "展示"),
            text_block(800, 190, "公告只有在“已启用”且处于时间窗口内时，才会被学生端公开接口返回", size=20, fill=MUTED),
        ]
    )
    write("fig5-6-announcement-flow.svg", svg_shell("图5-6 公告发布与生效流程图", body))


def main() -> None:
    fig_5_1()
    fig_5_2()
    fig_5_3()
    fig_5_4()
    fig_5_5()
    fig_5_6()


if __name__ == "__main__":
    main()
