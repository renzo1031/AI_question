const KNOWLEDGE_DATA = {
  '一年级': {
    '语文': ['第一单元 识字(一)', '第二单元 汉语拼音', '第三单元 课文(一)', '第四单元 识字(二)', '第五单元 课文(二)', '第六单元 课文(三)', '第七单元 课文(四)', '第八单元 课文(五)'],
    '数学': ['第一单元 准备课', '第二单元 位置', '第三单元 1~5的认识和加减法', '第四单元 认识图形(一)', '第五单元 6~10的认识和加减法', '第六单元 11~20各数的认识', '第七单元 认识钟表', '第八单元 20以内的进位加法']
  },
  '二年级': {
    '语文': ['第一单元 课文(一)', '第二单元 识字', '第三单元 课文(二)', '第四单元 课文(三)', '第五单元 课文(四)', '第六单元 课文(五)', '第七单元 课文(六)', '第八单元 课文(七)'],
    '数学': ['第一单元 长度单位', '第二单元 100以内的加法和减法(二)', '第三单元 角的初步认识', '第四单元 表内乘法(一)', '第五单元 观察物体(一)', '第六单元 表内乘法(二)', '第七单元 认识时间', '第八单元 数学广角']
  },
  '三年级': {
    '语文': ['第一单元 学校生活', '第二单元 金秋时节', '第三单元 童话世界', '第四单元 预测策略', '第五单元 观察与发现', '第六单元 祖国河山', '第七单元 大自然', '第八单元 美好品质'],
    '数学': ['第一单元 时、分、秒', '第二单元 万以内的加法和减法(一)', '第三单元 测量', '第四单元 万以内的加法和减法(二)', '第五单元 倍的认识', '第六单元 多位数乘一位数', '第七单元 长方形和正方形', '第八单元 分数的初步认识', '第九单元 数学广角'],
    '英语': ['Unit 1 Hello!', 'Unit 2 Colours', 'Unit 3 Look at me!', 'Unit 4 We love animals', 'Unit 5 Let\'s eat!', 'Unit 6 Happy birthday!']
  },
  '四年级': {
    '语文': ['第一单元 自然奇观', '第二单元 提问策略', '第三单元 观察日记', '第四单元 神话故事', '第五单元 生活万花筒', '第六单元 成长故事', '第七单元 家国情怀', '第八单元 历史故事'],
    '数学': ['第一单元 大数的认识', '第二单元 公顷和平方千米', '第三单元 角的度量', '第四单元 三位数乘两位数', '第五单元 平行四边形和梯形', '第六单元 除数是两位数的除法', '第七单元 条形统计图', '第八单元 数学广角'],
    '英语': ['Unit 1 My classroom', 'Unit 2 My schoolbag', 'Unit 3 My friends', 'Unit 4 My home', 'Unit 5 Dinner\'s ready', 'Unit 6 Meet my family!']
  },
  '五年级': {
    '语文': ['第一单元 万物有灵', '第二单元 阅读速度', '第三单元 民间故事', '第四单元 爱国情怀', '第五单元 说明文', '第六单元 父母之爱', '第七单元 自然之趣', '第八单元 读书明智'],
    '数学': ['第一单元 小数乘法', '第二单元 位置', '第三单元 小数除法', '第四单元 可能性', '第五单元 简易方程', '第六单元 多边形的面积', '第七单元 数学广角'],
    '英语': ['Unit 1 What\'s he like?', 'Unit 2 My week', 'Unit 3 What would you like?', 'Unit 4 We can do it!', 'Unit 5 There is a big bed', 'Unit 6 In a nature park']
  },
  '六年级': {
    '语文': ['第一单元 触摸自然', '第二单元 革命岁月', '第三单元 阅读策略', '第四单元 小说环境', '第五单元 文章中心', '第六单元 艺术之美', '第七单元 艺术之旅', '第八单元 鲁迅'],
    '数学': ['第一单元 分数乘法', '第二单元 位置与方向(二)', '第三单元 分数除法', '第四单元 比', '第五单元 圆', '第六单元 百分数(一)', '第七单元 扇形统计图', '第八单元 数学广角'],
    '英语': ['Unit 1 How can I get there?', 'Unit 2 Ways to go to school', 'Unit 3 My weekend plan', 'Unit 4 I have a pen pal', 'Unit 5 What does he do?', 'Unit 6 How do you feel?']
  },
  '七年级': {
    '语文': ['第一单元 四时之景', '第二单元 亲情之爱', '第三单元 学习生活', '第四单元 人生之舟', '第五单元 动物与人', '第六单元 想象之翼'],
    '数学': ['第一章 有理数', '第二章 整式的加减', '第三章 一元一次方程', '第四章 几何图形初步'],
    '英语': ['Unit 1 My name\'s Gina', 'Unit 2 This is my sister', 'Unit 3 Is this your pencil?', 'Unit 4 Where\'s my schoolbag?', 'Unit 5 Do you have a soccer ball?', 'Unit 6 Do you like bananas?', 'Unit 7 How much are these socks?', 'Unit 8 When is your birthday?', 'Unit 9 My favorite subject is science'],
    '生物': ['第一单元 生物和生物圈', '第二单元 生物体的结构层次', '第三单元 生物圈中的绿色植物'],
    '历史': ['第一单元 史前时期：中国境内人类的活动', '第二单元 夏商周时期：早期国家与社会变革', '第三单元 秦汉时期：统一多民族国家的建立和巩固', '第四单元 三国两晋南北朝时期：政权分立与民族交融'],
    '地理': ['第一章 地球和地图', '第二章 陆地和海洋', '第三章 天气与气候', '第四章 居民与聚落', '第五章 发展与合作'],
    '政治': ['第一单元 成长的节拍', '第二单元 友谊的天空', '第三单元 师长情谊', '第四单元 生命的思考']
  },
  '八年级': {
    '语文': ['第一单元 变化与成长', '第二单元 传记与回忆', '第三单元 山川之美', '第四单元 情感哲理', '第五单元 说明事物', '第六单元 吟咏情性'],
    '数学': ['第十一章 三角形', '第十二章 全等三角形', '第十三章 轴对称', '第十四章 整式的乘法与因式分解', '第十五章 分式'],
    '英语': ['Unit 1 Where did you go on vacation?', 'Unit 2 How often do you exercise?', 'Unit 3 I\'m more outgoing than my sister.', 'Unit 4 What\'s the best movie theater?', 'Unit 5 Do you want to watch a game show?', 'Unit 6 I\'m going to study computer science.', 'Unit 7 Will people have robots?', 'Unit 8 How do you make a banana milk shake?', 'Unit 9 Can you come to my party?', 'Unit 10 If you go to the party, you\'ll have a great time!'],
    '物理': ['第七章 力', '第八章 运动和力', '第九章 压强', '第十章 浮力', '第十一章 功和机械能', '第十二章 简单机械'],
    '生物': ['第四单元 生物圈中的人', '第五单元 生物圈中的其他生物', '第六单元 生物的多样性及其保护'],
    '历史': ['第一单元 隋唐时期：繁荣与开放的时代', '第二单元 辽宋夏金元时期：民族关系发展和社会变化', '第三单元 明清时期：统一多民族国家的巩固与发展'],
    '地理': ['第五章 中国的地理差异', '第六章 北方地区', '第七章 南方地区', '第八章 西北地区', '第九章 青藏地区', '第十章 中国在世界中'],
    '政治': ['第一单元 走进社会生活', '第二单元 遵守社会规则', '第三单元 勇担社会责任', '第四单元 维护国家利益']
  },
  '九年级': {
    '语文': ['第一单元 自然之音', '第二单元 砥砺思想', '第三单元 游目骋怀', '第四单元 小说人生', '第五单元 哲理之思', '第六单元 历史的回声'],
    '数学': ['第二十一章 一元二次方程', '第二十二章 二次函数', '第二十三章 旋转', '第二十四章 圆', '第二十五章 概率初步'],
    '英语': ['Unit 1 How can we become good learners?', 'Unit 2 I think that mooncakes are delicious!', 'Unit 3 Could you please tell me where the restrooms are?', 'Unit 4 I used to be afraid of the dark.', 'Unit 5 What are the shirts made of?', 'Unit 6 When was it invented?', 'Unit 7 Teenagers should be allowed to choose their own clothes.', 'Unit 8 It must belong to Carla.', 'Unit 9 I like music that I can dance to.', 'Unit 10 You\'re supposed to shake hands.', 'Unit 11 Sad movies make me cry.', 'Unit 12 Life is full of the unexpected.', 'Unit 13 We\'re trying to save the earth!', 'Unit 14 I remember meeting all of you in Grade 7.'],
    '物理': ['第十三章 内能', '第十四章 内能的利用', '第十五章 电流和电路', '第十六章 电压 电阻', '第十七章 欧姆定律', '第十八章 电功率', '第十九章 生活用电', '第二十章 电与磁', '第二十一章 信息的传递', '第二十二章 能源与可持续发展'],
    '化学': ['第八单元 金属和金属材料', '第九单元 溶液', '第十单元 酸和碱', '第十一单元 盐 化肥', '第十二单元 化学与生活'],
    '历史': ['第一单元 古代亚非文明', '第二单元 古代欧洲文明', '第三单元 封建时代的欧洲', '第四单元 封建时代的亚洲国家', '第五单元 走向近代', '第六单元 资本主义制度的初步确立', '第七单元 工业革命和国际共产主义运动的兴起'],
    '政治': ['第一单元 富强与创新', '第二单元 民主与法治', '第三单元 文明与家园', '第四单元 和谐与梦想']
  }
};

module.exports = KNOWLEDGE_DATA;
