const parse = (text) => {
  if (!text) return '';

  // 0. 提取公式并用占位符替代
  const mathBlocks = [];
  const mathInlines = [];

  // 标准化：将 \[ \] 转换为 $$ $$, 将 \( \) 转换为 $ $
  text = text.replace(/\\\[([\s\S]+?)\\\]/g, '$$$$$1$$$$');
  text = text.replace(/\\\(([\s\S]+?)\\\)/g, '$$$1$$');

  // 匹配块级公式 $$...$$
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (match, content) => {
    mathBlocks.push(content.trim());
    return `__MATH_BLOCK_${mathBlocks.length - 1}__`;
  });

  // 匹配行内公式 $...$ (非贪婪匹配，要求不以空白开头)
  // 排除 \$ 转义的情况
  text = text.replace(/(?<!\\)\$([^\s$][^$]*?)(?<!\\)\$/g, (match, content) => {
    mathInlines.push(content.trim());
    return `__MATH_INLINE_${mathInlines.length - 1}__`;
  });

  // 特殊处理：检测裸 LaTeX (在已提取公式之后处理剩余文本)
   // 我们寻找从 \ 开头或包含 _ { / ^ { 到最近的中文字符之前的片段 (允许空格和数学中常用的全角符号)
    const latexCommands = ['left', 'right', 'sum', 'frac', 'sqrt', 'alpha', 'beta', 'gamma', 'delta', 'theta', 'pi', 'int', 'limit', 'infty', 'times', 'div', 'pm', 'mp', 'le', 'ge', 'ne', 'approx', 'equiv', 'partial', 'nabla', 'forall', 'exists', 'neg', 'lor', 'land', 'in', 'ni', 'subset', 'supset', 'cup', 'cap', 'vec', 'dot', 'hat', 'bar', 'tilde', 'underline', 'overline', 'text', 'mathbf', 'mathcal', 'mathbb', 'mathrm', 'begin', 'end'];
    const nakedRegex = new RegExp(`(\\\\(${latexCommands.join('|')})|[_\\^]\\s*\\{[^}]+\\})[ -~，（）]+?(?=[\\u4e00-\u9fa5]|$)`, 'g');
  
  text = text.replace(nakedRegex, (match) => {
    mathInlines.push(match.trim());
    return `__MATH_INLINE_${mathInlines.length - 1}__`;
  });

  let lines = text.split('\n');
  let html = '';
  
  lines.forEach(line => {
    // 1. XSS 防护 (基本转义)
    line = line.replace(/&/g, "&amp;")
               .replace(/</g, "&lt;")
               .replace(/>/g, "&gt;");
               
    // 2. 行内样式处理
    // 加粗 **text**
    line = line.replace(/\*\*(.+?)\*\*/g, '<b style="color: #000;">$1</b>');
    // 斜体 *text*
    line = line.replace(/\*(.+?)\*/g, '<i>$1</i>');
    // 行内代码 `text`
    line = line.replace(/`(.+?)`/g, '<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #d63384;">$1</code>');

    // 3. 行级元素处理
    const trimmed = line.trim();
    
    // 标题
    if (trimmed.startsWith('# ')) {
      html += `<h1 style="font-size: 18px; font-weight: bold; margin: 12px 0 8px 0; color: #000;">${line.slice(2)}</h1>`;
    } else if (trimmed.startsWith('## ')) {
      html += `<h2 style="font-size: 16px; font-weight: bold; margin: 10px 0 6px 0; color: #000;">${line.slice(3)}</h2>`;
    } else if (trimmed.startsWith('### ')) {
      html += `<h3 style="font-size: 15px; font-weight: bold; margin: 8px 0 4px 0; color: #000;">${line.slice(4)}</h3>`;
    } 
    // 引用
    else if (trimmed.startsWith('> ')) {
      html += `<blockquote style="border-left: 3px solid #007aff; padding: 4px 0 4px 10px; color: #666; margin: 4px 0; background-color: #f5f7fa; border-radius: 0 4px 4px 0;">${line.slice(2)}</blockquote>`;
    }
    // 无序列表
    else if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
       html += `<div style="margin-bottom: 4px; padding-left: 10px; display: flex;"><span style="margin-right: 6px;">•</span><span>${line.replace(/^[\-\•]\s/, '')}</span></div>`;
    }
    // 有序列表 (简单的数字开头的)
    else if (/^\d+\.\s/.test(trimmed)) {
       const match = trimmed.match(/^(\d+\.)\s(.*)/);
       if (match) {
         html += `<div style="margin-bottom: 4px; padding-left: 10px; display: flex;"><span style="margin-right: 6px; font-weight: bold;">${match[1]}</span><span>${match[2]}</span></div>`;
       } else {
         html += `<div style="margin-bottom: 4px;">${line}</div>`;
       }
    }
    // 分割线
    else if (trimmed === '---' || trimmed === '***') {
      html += `<hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;" />`;
    }
    // 普通文本
    else {
      if (trimmed === '') {
        html += '<div style="height: 6px;"></div>'; // 段落间距
      } else {
        html += `<div style="min-height: 20px; word-break: break-all;">${line}</div>`;
      }
    }
  });
  
  // 4. 还原公式为图片
  // 块级公式
  html = html.replace(/__MATH_BLOCK_(\d+)__/g, (match, index) => {
    let tex = mathBlocks[index];
    // 清洗 LaTeX：将全角符号替换为半角，以便 CodeCogs 识别
    tex = tex.replace(/，/g, ',').replace(/（/g, '(').replace(/）/g, ')').replace(/：/g, ':').replace(/；/g, ';');
    const encoded = encodeURIComponent(tex);
    // 使用 CodeCogs 渲染，加 \large 增大一点
    return `<div style="margin: 10px 0; overflow-x: auto; text-align: center;">
              <img class="math-tex-block" src="https://latex.codecogs.com/svg.latex?\\large&space;${encoded}" style="max-width: 100%; height: auto; display: inline-block;" />
            </div>`;
  });
  
  // 行内公式
  html = html.replace(/__MATH_INLINE_(\d+)__/g, (match, index) => {
    let tex = mathInlines[index];
    // 清洗 LaTeX
    tex = tex.replace(/，/g, ',').replace(/（/g, '(').replace(/）/g, ')').replace(/：/g, ':').replace(/；/g, ';');
    const encoded = encodeURIComponent(tex);
    return `<img class="math-tex-inline" src="https://latex.codecogs.com/svg.latex?${encoded}" style="height: 1.2em; vertical-align: middle; margin: 0 2px; display: inline-block;" />`;
  });
  
  return `<div style="line-height: 1.6; font-size: 15px; color: #333; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;">${html}</div>`;
}

module.exports = { parse };
