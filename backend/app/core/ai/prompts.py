"""
AI解题Prompt模板
定义用于AI解题的提示词模板，确保输出严格JSON格式
"""
import json
from typing import Optional


def build_solve_question_prompt(
    question: str,
    context: Optional[str] = None
) -> str:
    """
    构建AI解题Prompt
    
    要求：
    1. 输出严格JSON格式，不允许自然语言
    2. 必须包含所有必需字段
    3. 选择题必须包含options
    4. 必须可被json.loads解析
    
    Args:
        question: 题目文本
        context: 上下文信息（可选）
        
    Returns:
        构建好的Prompt字符串
    """
    # 构建示例JSON（用于参考格式）
    example_json = {
        "question_type": "选择题",
        "subject": "数学",
        "grade": "一年级",
        "knowledge_point": "10以内加法",
        "difficulty": 3,
        "answer": "A",
        "analysis": "根据题意分析...",
        "options": [
            {"option_key": "A", "option_text": "选项A的内容"},
            {"option_key": "B", "option_text": "选项B的内容"}
        ]
    }
    example_json_str = json.dumps(example_json, ensure_ascii=False, indent=2)
    
    prompt = """你是一个专业的题目解析系统。请分析题目并输出一个有效的JSON对象。

【严格约束 - 必须遵守】
1. 输出必须是纯JSON格式，不允许有任何自然语言、解释、说明等额外文本
2. JSON必须可以被Python的json.loads()直接解析，不能有任何前缀或后缀
3. 所有字段必须存在，不能缺失任何字段
4. 所有字符串字段不能为空字符串
5. difficulty必须是1-5之间的整数
6. options必须是数组格式，即使为空也要是[]

【输出JSON格式】
{
  "question_type": "题目类型（字符串，如：选择题、填空题、解答题、判断题等）",
  "subject": "科目（字符串，如：数学、语文、英语、物理、化学等）",
  "grade": "年级（字符串，如：一年级、二年级、七年级、高一等，根据题目难度推断）",
  "knowledge_point": "知识点（字符串，如：10以内加法、一元一次方程、函数等，根据题目内容推断）",
  "difficulty": 难度等级（整数1-5，1最简单，5最难）,
  "answer": "标准答案（字符串，选择题填选项标识如A/B/C/D，其他题型填具体答案）",
  "analysis": "详细解题步骤和思路分析（字符串，不能为空）",
  "options": [
    {"option_key": "A", "option_text": "选项A的完整内容"},
    {"option_key": "B", "option_text": "选项B的完整内容"}
  ]
}

【字段详细说明】
1. question_type（必填）：
   - 类型：字符串
   - 取值：选择题、填空题、解答题、判断题、计算题、证明题等
   - 兜底：如果无法确定，使用"未知类型"

2. subject（必填）：
   - 类型：字符串
   - 取值：数学、语文、英语、物理、化学、生物、历史、地理、政治等
   - 兜底：如果无法确定，根据题目内容推测或使用"综合"

3. grade（必填）：
   - 类型：字符串
   - 取值：一年级、二年级、三年级、四年级、五年级、六年级、七年级、八年级、九年级、高一、高二、高三等
   - 根据题目难度和内容推断年级
   - 兜底：如果无法确定，使用"未知年级"

4. knowledge_point（必填）：
   - 类型：字符串
   - 取值：根据题目内容推断具体知识点，如"10以内加法"、"一元一次方程"、"函数"等
   - 要求：尽量具体、准确
   - 兜底：如果无法确定，使用"综合知识"

5. difficulty（必填）：
   - 类型：整数
   - 取值范围：1-5（1最简单，5最难）
   - 兜底：如果无法确定，使用3（中等难度）

6. answer（必填）：
   - 类型：字符串
   - 选择题：填入正确选项的标识（如"A"、"B"、"C"、"D"或"1"、"2"、"3"、"4"）
   - 填空题：填入具体答案
   - 解答题：填入最终答案
   - 判断题：填入"正确"或"错误"
   - 兜底：如果无法确定，使用"无法确定"

7. analysis（必填）：
   - 类型：字符串
   - 内容：详细的解题步骤、思路分析、关键知识点等
   - 不能为空字符串
   - 兜底：如果无法确定，使用"题目信息不足，无法提供详细解析"

8. options（必填）：
   - 类型：数组
   - 选择题：必须包含所有选项，每个选项包含option_key和option_text
   - 非选择题：必须为空数组[]
   - 格式：[{"option_key": "A", "option_text": "选项内容"}, ...]
   - 兜底：如果无法确定，使用空数组[]

【选择题识别规则】
如果题目中包含选项标识（如A、B、C、D或1、2、3、4等），必须：
1. 识别所有选项并完整填入options数组
2. option_key使用选项标识（A/B/C/D或1/2/3/4等）
3. option_text填入选项的完整内容
4. answer填入正确选项的option_key

【非选择题处理】
- 填空题：options=[]，answer填具体答案
- 解答题：options=[]，answer填最终答案，analysis填详细步骤
- 判断题：options=[]，answer填"正确"或"错误"
- 计算题：options=[]，answer填计算结果，analysis填计算过程

【输出示例格式】
"""
    
    prompt += example_json_str
    prompt += """

【题目内容】
"""
    
    # 添加题目内容
    prompt += f"{question}\n\n"
    
    # 添加上下文信息（如果有）
    if context:
        prompt += f"【上下文信息】\n{context}\n\n"
    
    # 最终强调
    prompt += """【最终要求】
1. 只输出JSON对象，不要有任何其他文字、说明、解释
2. JSON必须是有效的，可以直接被json.loads()解析
3. 严格按照上述格式输出，不要添加任何额外字段
4. 确保所有字段都存在且格式正确

【重要提示】
如果 AI 输出不符合 JSON 格式，请你自动修正并重新输出，直到符合要求为止。
请确保输出的 JSON 可以被 Python 的 json.loads() 直接解析，没有任何语法错误。

现在请分析题目并直接输出JSON（不要有任何其他文字）："""
    
    return prompt


def build_generate_questions_prompt(
    subject: str,
    grade: Optional[str] = None,
    chapter: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[int] = None,
    count: int = 10
) -> str:
    """
    构建AI出题Prompt
    
    要求：
    1. 输出严格JSON数组格式，不允许自然语言
    2. 每道题必须包含所有必需字段
    3. tags 必须包含年级、章节、知识点
    4. 必须可被json.loads解析
    
    Args:
        subject: 学科
        grade: 年级（可选）
        chapter: 章节（可选）
        knowledge_point: 知识点（可选）
        question_type: 题目类型（可选）
        difficulty: 难度等级（可选）
        count: 题目数量
        
    Returns:
        构建好的Prompt字符串
    """
    # 构建示例JSON数组（用于参考格式）
    example_questions = [
        {
            "content": "计算: 2 + 3 = ?（选择题需要将题干和选项分开）",
            "question_type": "选择题",
            "subject": "数学",
            "grade": "一年级",
            "knowledge_point": "10以内加法",
            "difficulty": 1,
            "answer": "A",
            "analysis": "根据题意，2 + 3 = 5，所以答案是A。",
            "options": [
                {"option_key": "A", "option_text": "5"},
                {"option_key": "B", "option_text": "4"},
                {"option_key": "C", "option_text": "6"},
                {"option_key": "D", "option_text": "3"}
            ],
            "tags": ["一年级", "第一章", "10以内加法"]
        },
        {
            "content": "计算: 15 - 8 = ___",
            "question_type": "填空题",
            "subject": "数学",
            "grade": "二年级",
            "knowledge_point": "两位数减法",
            "difficulty": 2,
            "answer": "7",
            "analysis": "15 - 8 = 7，可以用减法竭式计算。",
            "options": [],
            "tags": ["二年级", "第二章", "两位数减法"]
        }
    ]
    example_json_str = json.dumps(example_questions, ensure_ascii=False, indent=2)
    
    # 确定学段（根据年级推断）
    education_level = "中小学"
    if grade:
        if "一" in grade or "二" in grade or "三" in grade or "四" in grade or "五" in grade or "六" in grade:
            education_level = "小学"
        elif "七" in grade or "八" in grade or "九" in grade:
            education_level = "初中"
        elif "高一" in grade or "高二" in grade or "高三" in grade or "十" in grade:
            education_level = "高中"
    
    prompt = f"""你是{education_level}{subject}老师，擅长根据教学要求出题。

【严格约束 - 必须遵守】
1. 输出必须是纯JSON数组格式，不允许有任何自然语言、解释、说明等额外文本
2. JSON数组必须可以被Python的json.loads()直接解析，不能有任何前缀或后缀
3. 数组中的每个对象必须包含所有必需字段，不能缺失任何字段
4. 所有字符串字段不能为空字符串
5. difficulty必须是1-5之间的整数
6. tags必须是数组格式，必须包含三个元素：年级、章节、知识点（按顺序）
7. 严格按条件出题，不能偏离要求

【输出JSON数组格式】
[
  {{
    "content": "题目内容（字符串，选择题只包含题干不包含选项，非选择题包含完整题目）",
    "question_type": "题目类型（字符串，如：选择题、填空题、解答题、判断题等）",
    "subject": "科目（字符串，必须与参数subject一致）",
    "grade": "年级（字符串，必须与参数grade一致，如：一年级、七年级、高一等）",
    "knowledge_point": "知识点（字符串，必须与参数knowledge_point一致）",
    "difficulty": 难度等级（整数1-5，1最简单，5最难）,
    "answer": "标准答案（字符串，选择题填选项标识如A/B/C/D，其他题型填具体答案）",
    "analysis": "详细解题步骤和思路分析（字符串，不能为空）",
    "options": [
      {{"option_key": "A", "option_text": "选项A内容"}},
      {{"option_key": "B", "option_text": "选项B内容"}}
    ],
    "tags": ["年级", "章节", "知识点"]
  }},
  ...
]

【字段详细说明】
1. content（必填）：
   - 类型：字符串
   - 选择题：只包含题干内容，不包含选项（选项放在options字段中）
   - 非选择题：包含题目的完整内容
   - 要求：题目必须完整、清晰、准确

2. question_type（必填）：
   - 类型：字符串
   - 取值：选择题、填空题、解答题、判断题、计算题、证明题等
   - 如果指定了question_type参数，必须严格匹配

3. subject（必填）：
   - 类型：字符串
   - 必须与参数subject完全一致
   - 取值：数学、语文、英语、物理、化学、生物、历史、地理、政治等

4. grade（必填）：
   - 类型：字符串
   - 必须与参数grade完全一致（如果提供了grade）
   - 取值：一年级、二年级、三年级、四年级、五年级、六年级、七年级、八年级、九年级、高一、高二、高三等
   - 如果未提供grade参数，根据题目难度合理推断

5. knowledge_point（必填）：
   - 类型：字符串
   - 必须与参数knowledge_point完全一致（如果提供了knowledge_point）
   - 取值：根据题目内容确定具体知识点，如"10以内加法"、"一元一次方程"、"函数"等
   - 如果未提供knowledge_point参数，根据题目内容合理推断

6. difficulty（必填）：
   - 类型：整数
   - 取值范围：1-5（1最简单，5最难）
   - 如果指定了difficulty参数，必须严格匹配
   - 如果未指定，根据题目难度合理设置

7. answer（必填）：
   - 类型：字符串
   - 选择题：填入正确选项的标识（如"A"、"B"、"C"、"D"）
   - 填空题：填入具体答案
   - 解答题：填入最终答案
   - 判断题：填入"正确"或"错误"

8. analysis（必填）：
   - 类型：字符串
   - 内容：详细的解题步骤、思路分析、关键知识点等
   - 不能为空字符串

9. options（必填）：
   - 类型：数组
   - 选择题：必须包含所有选项，每个选项包含option_key和option_text
   - 非选择题：必须为空数组[]
   - 格式：[{{"option_key": "A", "option_text": "选项内容"}}, ...]
   - 示例：[{{"option_key": "A", "option_text": "5"}}, {{"option_key": "B", "option_text": "4"}}]

10. tags（必填）：
   - 类型：数组
   - 必须包含三个元素，按顺序：["年级", "章节", "知识点"]
   - 年级：必须与参数grade完全匹配（如果提供了grade），否则根据题目内容合理推断
   - 章节：必须与参数chapter完全匹配（如果提供了chapter），否则根据题目内容合理推断
   - 知识点：必须与参数knowledge_point完全匹配（如果提供了knowledge_point），否则根据题目内容合理推断
   - 示例：["七年级", "第一章", "一元一次方程"]

【出题要求】
"""
    
    # 添加出题条件
    prompt += f"学科：{subject}\n"
    if grade:
        prompt += f"年级：{grade}\n"
    if chapter:
        prompt += f"章节：{chapter}\n"
    if knowledge_point:
        prompt += f"知识点：{knowledge_point}\n"
    if question_type:
        prompt += f"题目类型：{question_type}\n"
    if difficulty:
        prompt += f"难度等级：{difficulty}\n"
    prompt += f"题目数量：{count}\n\n"
    
    prompt += """【选择题处理 - 重要】
如果题目类型是选择题：
1. content字段：只包含题干内容，不包含选项
2. options字段：必须包含所有选项，格式为[{{"option_key": "A", "option_text": "选项内容"}}, ...]
3. answer字段：填入正确选项的option_key（如"A"、"B"等）

示例：
{{
  "content": "计算: 2 + 3 = ?",
  "question_type": "选择题",
  "options": [
    {{"option_key": "A", "option_text": "5"}},
    {{"option_key": "B", "option_text": "4"}},
    {{"option_key": "C", "option_text": "6"}},
    {{"option_key": "D", "option_text": "3"}}
  ],
  "answer": "A"
}}

【非选择题处理】
如果题目类型不是选择题：
1. content字段：包含题目的完整内容
2. options字段：必须为空数组[]
3. answer字段：填入具体答案

【输出示例格式】
"""
    
    prompt += example_json_str
    prompt += """

【最终要求】
1. 只输出JSON数组，不要有任何其他文字、说明、解释（禁止输出多余文本）
2. JSON数组必须是有效的，可以直接被json.loads()解析
3. 严格按照上述格式输出，不要添加任何额外字段
4. 确保数组中的每个对象都包含所有必需字段：content, question_type, subject, grade, knowledge_point, difficulty, answer, analysis, options, tags
5. 数组长度必须等于题目数量要求
6. options字段：选择题必须包含选项数组，非选择题必须为[]
7. tags数组必须包含三个元素：年级、章节、知识点（按顺序）

【重要提示 - 格式自动修正】
如果 AI 输出不符合 JSON 格式，请你自动修正并重新输出，直到符合要求为止。
请确保输出的 JSON 数组可以被 Python 的 json.loads() 直接解析，没有任何语法错误。
如果格式错误，必须自动修正。

现在请根据要求出题并直接输出JSON数组（不要有任何其他文字）："""
    
    return prompt

