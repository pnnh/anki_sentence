"""Pattern metadata and validators shared by the grammar/narrative packs."""

import re

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")

PAST_RE = re.compile(
    r"\b(was|were|did|went|came|got|made|took|saw|said|told|had|found|left|gave|bought|"
    r"thought|knew|wanted|needed|liked|worked|booked|ordered|paid|arrived|finished|called|"
    r"asked|looked|tried|started|stopped|changed|moved|opened|closed|lost|met|sent|brought|"
    r"kept|ran|ate|drank|slept|woke|forgot|broke|chose|drove|flew|felt|heard|held|spoke|"
    r"spent|stood|taught|threw|understood|wore|won|wrote|visited|studied|learned|learnt|"
    r"became|began|fell|grew|rode|sat|swam|sang|built|caught|cut|dug|fed|fought|hung|"
    r"hit|hurt|laid|led|lent|lit|meant|rode|rang|rose|shook|shut|slept|sped|spelt|"
    r"stole|stuck|stung|swore|swept|swung|tore|wound|watched|walked|talked|played|cooked|"
    r"cleaned|helped|waited|danced|painted|rested|practiced|shopped|traveled|travelled|"
    r"planned|jogged|hiked|enjoyed|joined|missed|used|turned|posted|replied|shared|hoped)\b",
    re.I,
)
# Any regular -ed verb, minus nouns/adjectives that merely end in "ed".
PAST_ED_RE = re.compile(
    r"\b(?!speed\b|hundred\b|indeed\b|sacred\b|naked\b|wicked\b|wretched\b|hatred\b|"
    r"kindred\b|rugged\b|jagged\b|ragged\b|beloved\b|blessed\b)\w{3,}ed\b",
    re.I,
)
TIME_RE = re.compile(r"\b(yesterday|last|ago|this morning|this afternoon|last night|the day before yesterday|the other day|when i was|in \d{4})\b", re.I)
FREQ_RE = re.compile(
    r"\b(always|usually|often|sometimes|rarely|never|every day|every morning|"
    r"once a week|twice a week|three times a week)\b",
    re.I,
)
CONNECTOR_RE = re.compile(
    r"\b(because|but|so|then|and|although|though|when|while|after|before|later|"
    r"suddenly|finally|until|instead)\b",
    re.I,
)
TAG_RE = re.compile(
    r",\s*(?:right|okay|ok|correct|yes|no)\b|"
    r",\s*(?:isn't|aren't|wasn't|weren't|don't|doesn't|didn't|can't|couldn't|won't|"
    r"wouldn't|haven't|hasn't|shouldn't|mustn't)\s+(?:it|they|you|we|he|she|i)\b|"
    r",\s*(?:is|are|was|were|do|does|did|can|could|will|would|have|has|should)\s+"
    r"(?:it|they|you|we|he|she|i)\b",
    re.I,
)
PASSIVE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+"
    r"((?:always|already|usually|often|never|not|also|still|just|finally|only|really|"
    r"sometimes|soon|recently)\s+){0,3}"
    r"(\w+ed|made|done|given|taken|sent|paid|fixed|cleaned|delivered|charged|refunded|"
    r"updated|included|required|allowed|closed|opened|built|written|held|kept|sold|"
    r"stolen|damaged|lost|broken|locked|checked|replaced|cancelled|canceled|prepared|"
    r"rejected|accepted|cut|read|left)\b",
    re.I,
)
GERUND_RE = re.compile(
    r"\b(?:enjoy|lik|lov|hate|prefer|finish|stop|avoid|mind|suggest|recommend|keep|"
    r"practic|consider|imagin|risk|miss|start|begin|continu|afraid of|good at|"
    r"interested in|tired of|thinking about|thought about|without|instead of|"
    r"looking forward to|worth)\w*\b[^.;]{0,20}\b\w{3,}ing\b|^\s*\w+ing\b",
    re.I,
)
INFINITIVE_RE = re.compile(
    r"\b(?:want|need|hope|plan|decid|try|learn|promis|agree|refus|offer|expect|manag|"
    r"afford|choos|rememb|forget|would like)\w*\s+(?:not\s+)?to\b",
    re.I,
)
MEDIA_RE = re.compile(
    r"\b(movie|movies|film|films|book|books|novel|series|show|season|episode|"
    r"documentary|documentaries|story|plot|ending|actor|actors|actress|soundtrack|"
    r"original|music)\b",
    re.I,
)
OPINION_RE = re.compile(
    r"\b(think|feel|find|thought|felt|found|enjoy|enjoyed|like|liked|loved|prefer|"
    r"disappointed|boring|interesting|good|great|better|worse|best|worst|slow|exciting|"
    r"realistic|worth|mediocre|okay|rushed|abrupt|long|short|cut|skipped|recommend|"
    r"amazing|terrible|weird|funny|sad)\b",
    re.I,
)
RELATION_RE = re.compile(
    r"\b(have|has)\s+\w+|(who|that|whom|whose)|"
    r"(friend|friends|neighbor|neighbors|neighbour|neighbours|colleague|colleagues|"
    r"coworker|coworkers|classmate|classmates|roommate|roommates|sister|sisters|"
    r"brother|brothers|family|mother|father|parents|cousin|cousins|partner|partners)\b",
    re.I,
)


def has_past(text):
    return bool(PAST_RE.search(text) or PAST_ED_RE.search(text))


def expand(text):
    t = text.lower().replace("’", "'")
    t = re.sub(r"\bcan't\b", "can not", t)
    t = re.sub(r"\bcannot\b", "can not", t)
    t = re.sub(r"\bwon't\b", "will not", t)
    t = re.sub(r"\bshan't\b", "shall not", t)
    t = re.sub(r"\b(\w+)n't\b", r"\1 not", t)
    t = re.sub(r"\b(he|she|it)'s(?=\s+going to\b)", r"\1 is", t)
    t = re.sub(r"\b(i|you|we|they)'ve\b", r"\1 have", t)
    t = re.sub(r"\b(he|she|it)'s\b", r"\1 has", t)
    t = re.sub(r"\b(i|you|he|she|it|we|they)'ll\b", r"\1 will", t)
    t = re.sub(r"\bi'm\b", "i am", t)
    t = re.sub(r"\b(you|we|they)'re\b", r"\1 are", t)
    t = re.sub(r"\b(he|she|it|i|you|we|they)'d\b", r"\1 would", t)
    return t


def passes_en(pattern, en):
    t = en.lower().replace("’", "'")
    n = expand(t)
    if pattern == "past_simple":
        return has_past(n) and bool(TIME_RE.search(n))
    if pattern == "past_continuous":
        return bool(re.search(r"\b(was|were)\s+\w+ing\b", n)) and bool(re.search(r"\b(when|while)\b", n))
    if pattern == "present_perfect":
        return bool(re.search(
            r"\b(have|has)\s+(never\s+|ever\s+|already\s+|just\s+|recently\s+|only\s+)?"
            r"(been|got|gotten|done|seen|made|taken|gone|eaten|paid|lost|found|left|finished|"
            r"arrived|booked|ordered|changed|moved|worked|lived|known|had|sent|broken|forgotten|"
            r"received|completed|visited|tried|studied|learned|learnt|kept|written|read|"
            r"cleaned|started|stopped|helped|missed)\b", n))
    if pattern == "going_to":
        return bool(re.search(r"\b(am|is|are)\s+going to\b", n))
    if pattern == "will":
        return bool(re.search(r"\bwill\b", n))
    if pattern == "used_to":
        return bool(re.search(r"\bused to\b", n))
    if pattern == "first_conditional":
        return bool(re.search(r"\bif\b", n)) and bool(re.search(r"\b(will|can|may|might)\b", n)) \
            and not re.search(r"\bwould\b", n)
    if pattern == "second_conditional":
        return bool(re.search(r"\bif\b", n)) and bool(re.search(r"\b(would|could|might)\b", n))
    if pattern == "modals_obligation":
        return bool(re.search(
            r"\b(must|mustn't|have to|has to|had to|should|shouldn't|allowed to|not supposed to)\b", n))
    if pattern == "comparatives":
        return bool(re.search(
            r"\b(\w+er|more|less)\s+than\b|\bas\s+\w+\s+as\b|\bthe\s+\w+est\b|\bbetter\b|\bworse\b", n))
    if pattern == "tag_questions":
        return bool(TAG_RE.search(t))
    if pattern == "relative_clauses":
        return bool(re.search(r"\b(who|which|where|whose|that)\b", n))
    if pattern == "gerund_infinitive":
        return bool(GERUND_RE.search(n)) and bool(INFINITIVE_RE.search(n))
    if pattern == "passive":
        return bool(PASSIVE_RE.search(n))
    if pattern == "reported_speech":
        return bool(re.search(r"\b(said|told|asked)\b", n))
    if pattern == "narrative_daily_routine":
        return bool(FREQ_RE.search(n)) and bool(re.search(r"\b(first|then|after that)\b", n))
    if pattern == "narrative_last_weekend":
        return has_past(n) and bool(CONNECTOR_RE.search(n))
    if pattern == "narrative_childhood":
        return bool(re.search(r"\b(used to|when i was|grew up|as a child)\b", n))
    if pattern == "narrative_future_plans":
        return bool(re.search(r"\b(going to|will|plan to|hope to|want to)\b", n))
    if pattern == "narrative_health_habits":
        return bool(re.search(
            r"\b(used to|recently|now|have started|started|every day|every week|"
            r"once a week|twice a week|haven't|don't)\b", n))
    if pattern == "narrative_work_study_problems":
        return bool(re.search(r"\b(because|so|but|problem|difficult|slow|late|behind)\b", n))
    if pattern == "narrative_travel_story":
        return has_past(n) and bool(CONNECTOR_RE.search(n))
    if pattern == "narrative_movies_books":
        return bool(MEDIA_RE.search(n)) and bool(OPINION_RE.search(n))
    if pattern == "narrative_relationships":
        return bool(re.search(r"\b(have|has)\s+\w+", n)) \
            or bool(re.search(r"\b(who|that|whom|whose)\b", n)) \
            or bool(RELATION_RE.search(n))
    if pattern == "narrative_wishes_regrets":
        return bool(re.search(r"\b(wish|if only|should have|regret)\b", n))
    raise ValueError(f"Unknown pattern: {pattern}")


ZH_CHECKS = {
    "past_simple": r"(昨天|前天|上周|上个月|去年|前年|刚才|那天|当时|小时候|周末|昨晚|上次|那次|第一次|分钟前|小时前|天前|年前|早上|下午|晚上|今年|刚才)",
    "past_continuous": r"(正在|正|在).{0,12}(的时候|时)|突然|这时|(昨天|昨晚|前天|上周|今天|中午|晚上).{0,30}(正在|正|时|的时候)",
    "present_perfect": r"(已经|还没|从没|从来没|刚刚|刚才|一直|到现在|过.{0,6}(次|吗|了)|年了|个月了|住了|去过|看过|做过|吃过|认识|收到)",
    "going_to": r"(打算|准备|计划|想要).{0,12}(下个月|下周|明年|以后|将来|这个周末|这个假期|假期|周末|今年|今晚|明天)|(下个月|下周|明年|以后|将来|这个周末|这个假期|假期|周末|今年|今晚|明天).{0,12}(打算|准备|计划|想要)",
    "will": r"(会|将|要).{0,14}(明天|今晚|下周|下个月|明年|以后|将来|晚点|待会|马上|后天)|(明天|今晚|下周|下个月|明年|以后|将来|后天).{0,14}(会|将|要)",
    "used_to": r"(以前|过去|小时候|曾经|从前|原来)",
    "first_conditional": r"(如果|要是|假如).{0,24}(就|会|可以|得)",
    "second_conditional": r"(如果|要是|假如).{0,24}(就|会|可以)",
    "modals_obligation": r"(必须|得|应该|不能|不可以|不允许|禁止|需要|不用|不必)",
    "comparatives": r"(比|不如|没有.{0,12}(那么|这么|好看|好|热闹|便宜|快|贵|重|轻|省钱)|更|最|一样)",
    "tag_questions": r"(吧|对吧|是不是|好吗|行吗|可以吗|对吗|不是吗)[？?]?$",
    "relative_clauses": r"的[^，。？！]{1,6}|(一个|一位|一只|那个|这位|那位).{0,20}，.{0,20}(他|她|它)",
    "gerund_infinitive": r"(喜欢|爱|讨厌|介意|建议|坚持|练习|避免|考虑|完成|停止|想|打算|决定|希望|开始|学|需要|试着)",
    "passive": r"(被|让|给)|是.{1,24}的[，,。]|(改到|推迟到|安排在|送到|修好|准备好)",
    "reported_speech": r"(说|告诉|问|提醒|让我|叫我)",
    "narrative_daily_routine": r"(通常|一般|平时|每天|常常|总是).{0,30}(先|然后|接着|再|早上|晚上|睡前)",
    "narrative_last_weekend": r"(周末|上周|前天|昨天).{0,50}(虽然|但是|不过|因为|所以|然后|结果|后来|才|还|后|，|,)",
    "narrative_childhood": r"(小时候|童年|以前|那时候|那年|我在.{0,10}长大)",
    "narrative_future_plans": r"(明年|以后|将来|下个月|今年|未来).{0,30}(打算|计划|想|希望|准备|会|要)|(打算|计划|想|希望|准备|会|要).{0,20}(明年|以后|将来|下个月|今年|未来)",
    "narrative_health_habits": r"(以前|过去|原来).{0,40}(现在|最近|如今|这阵子)",
    "narrative_work_study_problems": r"^(?=.*(因为|所以|但是|不过|由于|结果))(?=.*(问题|慢|难|落后|加班|请假|延期|压力|忙|没|迟到|失败|投诉|低|否|拒|取消|不够|太高))",
    "narrative_travel_story": r"(去年|上次|那次|前年|昨天|前天|旅行|假期|出差|外地|国外|机场|酒店|景点).{0,60}(但是|不过|结果|后来|然后|因为|所以|虽然|正在|的时候|时|这时|突然|幸好|还好|最后|把|，|,)",
    "narrative_movies_books": r"(电影|书|小说|剧|纪录片|剧情片|片|演员|故事|结局|配乐|情节|季).{0,40}(觉得|感觉|不如|没有|比|更|好看|精彩|一般|失望|删|喜欢|满意|出彩|有意思|好听|值得|不错)|(觉得|感觉).{0,30}(电影|书|小说|剧|纪录片|剧情片)",
    "narrative_relationships": r"^(?=.*(朋友|同事|邻居|同学|认识|相处|家人|父母|哥哥|姐姐|妹妹|弟弟|室友))(?=.*(一直|总是|总|经常|每次|十年|多年|互相|每周|从小|无话不谈|最近|老))",
    "narrative_wishes_regrets": r"(希望|后悔|早知道|要是|如果).{0,30}(当初|当时|小时候|早|就|回到|没|学过)",
}


def passes_zh(pattern, zh):
    rx = ZH_CHECKS.get(pattern)
    if not rx:
        raise ValueError(f"Unknown pattern: {pattern}")
    return bool(re.search(rx, zh))


MAX_WORDS = {"grammar": 18, "narrative": 24}
MIN_WORDS = 4


def word_count(text):
    return len(WORD_RE.findall(text))


LABELS = {
    "past_simple": "past simple verb + a past time phrase",
    "past_continuous": "was/were + verb-ing, with when or while",
    "present_perfect": "have/has + past participle (for experience, completion, or duration)",
    "going_to": "be going to + verb",
    "will": "will + verb",
    "used_to": "used to + verb",
    "first_conditional": "if + present tense, will/can/may + verb (no would)",
    "second_conditional": "if + past tense, would/could/might + verb",
    "modals_obligation": "must / have to / should / not allowed to",
    "comparatives": "comparative adjective + than, or as ... as",
    "tag_questions": "statement + comma + a negative tag such as isn't it, don't you, haven't you",
    "relative_clauses": "a clause with who / which / where / that",
    "gerund_infinitive": "verb + -ing (enjoy swimming) AND verb + to + verb (plan to save)",
    "passive": "be + past participle (is cleaned, was rejected, is already prepared)",
    "reported_speech": "said / told / asked + reported statement or question",
    "narrative_daily_routine": "frequency adverb + sequence words (first, then)",
    "narrative_last_weekend": "past simple + a connector",
    "narrative_childhood": "used to / when I was / grew up",
    "narrative_future_plans": "going to / plan to / will",
    "narrative_health_habits": "used to for the past + now for the present",
    "narrative_work_study_problems": "a reason or result connector (because, so, but)",
    "narrative_travel_story": "past tense + a connector such as when, while, so, but, then",
    "narrative_movies_books": "a media noun + an opinion or comparative",
    "narrative_relationships": "present perfect (have/has + participle) or a who/that clause",
    "narrative_wishes_regrets": "wish / if only / should have",
}


# Ten concrete everyday angles per pattern. The planner writes two sentences per angle.
ANGLES = {
    "past_simple": [
        "上周末去看爷爷奶奶", "昨天开会时电脑突然坏了", "前天在超市遇到老同学",
        "去年夏天去了海边", "上周把钥匙弄丢了", "今天早上上班迟到了",
        "上个月搬了新家", "昨天晚上看了一部电影", "上周给妈妈打了电话",
        "昨天在餐厅点了一桌子菜",
    ],
    "past_continuous": [
        "昨晚八点做饭时有人敲门", "昨天下午开会时手机响了", "上周六下雨时在等公交",
        "昨晚十点洗澡时停电了", "前天晚上看电视时邻居来借东西", "昨天中午吃饭时同事打来电话",
        "上周日逛超市时遇到朋友", "昨晚写报告时孩子哭了", "前天下午在公园跑步时下起了雨",
        "今天早上做早饭时烤箱响了",
    ],
    "present_perfect": [
        "在这座城市住了五年", "去过海边三次", "还没吃过这家店", "已经做完今天的工作",
        "从来没学过游泳", "刚刚收到你的邮件", "这周已经加了三天班", "认识他十年了",
        "最近一直睡不好", "到现在还没收到快递",
    ],
    "going_to": [
        "下个月搬到新公寓", "这个周末去看朋友", "明年换一份工作", "今晚早点睡",
        "下周开始学吉他", "这个假期去爬山", "下个月买一台新电脑", "明天下午去理发",
        "今年存钱买一辆自行车", "下周末请朋友吃饭",
    ],
    "will": [
        "明天帮朋友修电脑", "下周把书还给你", "明年带父母去旅行", "今晚给你打电话",
        "后天陪孩子去动物园", "下个月开始锻炼", "下周把报告交上去", "明天早上叫你起床",
        "下周末帮你搬家", "以后多陪家人",
    ],
    "used_to": [
        "以前每天喝咖啡", "小时候走路上学", "过去常去那家小店", "以前不怎么会做饭",
        "小时候住在小城市", "以前每天坐公交上班", "过去周末常去爬山", "以前很怕狗",
        "以前总熬夜", "过去不会用智能手机",
    ],
    "first_conditional": [
        "如果赶不上这班车", "如果明天下雨", "如果你有空", "如果价格太贵", "如果找不到路",
        "如果他不接电话", "如果今晚加班", "如果周末天气好", "如果菜太辣", "如果忘记带钥匙",
    ],
    "second_conditional": [
        "如果我是你", "如果我有很多钱", "如果我会开车", "如果今天不上班", "如果我能选",
        "如果房子再大一点", "如果我是老板", "如果我不怕高", "如果我明天不用上班",
        "如果能回到十年前",
    ],
    "modals_obligation": [
        "小区晚上十点后不能放音乐", "上班必须穿正装", "图书馆里应该安静", "坐飞机不能带液体",
        "病人必须按时吃药", "这里不允许停车", "孩子睡前应该刷牙", "会议室里不能吃东西",
        "员工得在周五前交报告", "博物馆里不能开闪光灯",
    ],
    "comparatives": [
        "地铁比打车便宜", "这家店服务比那家好", "今天比昨天冷", "开车比坐火车快",
        "这个包比那个轻", "在家做饭比外面吃省钱", "这本书没有电影好看", "他跑得比我快",
        "新手机比旧的重", "这家餐厅不如那家热闹",
    ],
    "tag_questions": [
        "你关上了窗户", "明天九点开会", "你不太喜欢吃辣", "这是你的伞", "公交车站就在前面",
        "你已经吃过饭了", "他明天不来上班", "这部电影很好看", "你会说英语", "我们还要再等一会儿",
    ],
    "relative_clauses": [
        "那个穿蓝外套的人帮我找到钱包", "我认识一个会修电脑的朋友", "这是我昨天买的那本书",
        "那个住在楼下的老人很热心", "我想找一个能说英语的导游", "这就是我跟你提过的那家店",
        "那个帮我搬家的同事今天请假了", "我有一只每天都跟着我的猫", "这就是我们上次开会的地方",
        "那个总迟到的同事今天又晚了",
    ],
    "gerund_infinitive": [
        "喜欢周末做饭，也想学做甜点", "讨厌排队，但愿意等这家店", "建议坐地铁，决定不买车",
        "喜欢跑步，希望参加比赛", "介意开窗", "想学游泳，怕呛水", "考虑换工作，打算先存钱",
        "喜欢看小说，也想写一本", "建议早点出发，避免堵车", "想买相机，决定先攒钱",
    ],
    "passive": [
        "自行车上周修好了", "我的快递被别人拿走了", "会议改到下午三点了", "窗户是昨天擦的",
        "那家店被新老板接手了", "我的手机被偷了", "晚餐已经准备好了", "这个包裹是早上送来的",
        "我的申请被拒绝了", "教室每天都会打扫",
    ],
    "reported_speech": [
        "他告诉我会议改到三点", "医生说要多喝水", "朋友问我周末有没有空", "老板让我明天早点到",
        "妈妈提醒我带伞", "同事说他下周请假", "客服说会帮我查一下", "老师告诉我们考试很简单",
        "邻居问我能不能帮忙收快递", "他问我喜不喜欢这个城市",
    ],
    "narrative_daily_routine": [
        "早上七点起床跑步", "通勤路上听播客", "午休和同事吃饭", "晚上做饭看剧", "睡前读半小时书",
        "周末打扫房间", "每天喝两杯咖啡", "晚上十一点睡觉", "下班顺路买菜", "周三晚上去健身房",
    ],
    "narrative_last_weekend": [
        "和朋友去爬山，很累但风景美", "在家补觉，然后打扫卫生", "去看了一场电影，觉得一般",
        "带孩子去公园野餐", "加班两天，周日才休息", "去郊区看父母", "逛二手市场买了一把椅子",
        "在家学做面包，烤糊了", "和朋友吃饭聊天到很晚", "下雨没出门，在家整理照片",
    ],
    "narrative_childhood": [
        "住在一座小城市，在河边玩", "夏天和邻居孩子捉迷藏", "每天早上被妈妈叫醒",
        "放学后在小卖部买零食", "寒假去外婆家过年", "学骑自行车摔了好几次",
        "喜欢在院子里养小动物", "和哥哥抢电视看", "考试前熬夜复习", "暑假每天去游泳",
    ],
    "narrative_future_plans": [
        "明年换工作", "存钱买房", "学一门新语言", "带父母旅行", "开始健身",
        "搬到离公司近的地方", "养一只狗", "考一个证书", "减少加班", "每周做一次饭",
    ],
    "narrative_health_habits": [
        "以前很少运动，现在每周游泳两次", "以前总吃外卖，现在自己做饭", "以前熬夜，现在十一点睡",
        "以前每天喝奶茶，现在改喝水", "以前不走路，现在每天走一万步", "以前不吃早饭，现在每天吃",
        "以前很少吃蔬菜，现在每餐都有", "以前周末躺着，现在去爬山", "以前总喝咖啡，现在改喝茶",
        "以前不体检，现在每年查一次",
    ],
    "narrative_work_study_problems": [
        "项目进度慢，因为同事请假", "报告没写完，因为电脑坏了", "考试没考好，因为复习时间不够",
        "开会迟到，因为路上堵车", "方案被否了，因为预算太高", "最近总加班，因为人手不够",
        "论文延期，因为数据出了问题", "客户投诉，因为送货太慢", "学习效率低，因为总被打断",
        "面试失败，因为太紧张",
    ],
    "narrative_travel_story": [
        "在另一个城市迷路，老人送到车站", "赶飞机迟到，工作人员帮忙改签", "下雨没带伞，店主借伞",
        "钱包丢了，警察帮忙找回", "酒店房间有问题，前台换了房", "错过末班车，打车回酒店",
        "在山上手机没电，向路人求助", "行李被拿错，机场帮忙找到", "语言不通，用手势点餐",
        "景点关门，临时改了行程",
    ],
    "narrative_movies_books": [
        "电影没有原著小说好看", "新剧比上一季差", "这本书开头慢，后面精彩", "纪录片比剧情片真实",
        "演员演得好，但故事一般", "小说太长，电影删了很多", "结局太仓促，不太满意",
        "配乐很好听，值得再看", "朋友推荐的书很有意思", "看了两遍才看懂",
    ],
    "narrative_relationships": [
        "认识十年的朋友总帮忙", "和同事相处得很好", "邻居经常互相照应", "大学同学每年聚一次",
        "和姐姐无话不谈", "一个朋友总在我需要时出现", "和室友分担家务", "老朋友搬到别的城市",
        "认识一个新朋友，聊得来", "和家人每周视频",
    ],
    "narrative_wishes_regrets": [
        "真希望当初多学一门外语", "后悔没早点开始存钱", "要是当时多问一句就好了",
        "希望小时候学过钢琴", "后悔昨天没去参加聚会", "早知道就早点出门了",
        "真希望能回到那一天", "后悔没有接受那份工作", "要是当时拍张照片就好了",
        "希望当初选了另一个专业",
    ],
}
