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

PHRASAL_EN = {
    "phrasal_get_up": re.compile(
        r"\b(wake|woke|woken|waking|get|got|gotten|getting)\s+(?:\w+\s+){0,2}up\b", re.I),
    "phrasal_put_on": re.compile(
        r"\b(put|puts|putting|try|tries|tried|trying)\s+(?:\w+\s+){0,2}on\b|"
        r"\b(take|took|taken|taking|remove|removed|removing)\s+(?:\w+\s+){0,2}off\b", re.I),
    "phrasal_pick_up": re.compile(
        r"\b(pick|picks|picked|picking)\s+(?:\w+\s+){0,2}up\b|"
        r"\b(drop|drops|dropped|dropping)\s+(?:\w+\s+){0,2}off\b", re.I),
    "phrasal_turn_on_off": re.compile(
        r"\b(turn|turns|turned|turning|switch|switches|switched|switching)\s+(?:\w+\s+){0,2}(on|off)\b", re.I),
    "phrasal_look_for": re.compile(
        r"\b(look|looks|looked|looking)\s+(for|up)\b|\b(check|checks|checked|checking)\b|"
        r"\b(find|finds|found|finding)\s+out\b", re.I),
    "phrasal_figure_out": re.compile(
        r"\b(figure|figures|figured|figuring)\s+(?:\w+\s+){0,2}out\b", re.I),
    "phrasal_go_back": re.compile(
        r"\b(come|came|coming|go|goes|went|going|get|got|getting|drive|drove|driving|"
        r"walk|walked|walking|run|ran|running|rush|rushed|head|headed|heading)"
        r"\s+(?:\w+\s+){0,2}back\b", re.I),
    "phrasal_go_out": re.compile(
        r"\b(go|goes|went|going)\s+out\b|\b(hang|hangs|hung|hanging)\s+out\b", re.I),
    "phrasal_work_out": re.compile(
        r"\b(work|works|worked|working)\s+(?:\w+\s+){0,2}out\b", re.I),
    "phrasal_run_out": re.compile(
        r"\b(ran|run|runs|running)\s+out\b", re.I),
    "phrasal_end_up": re.compile(
        r"\b(show|shows|showed|showing)\s+up\b|\b(end|ends|ended|ending)\s+up\b", re.I),
    "phrasal_turn_out": re.compile(
        r"\b(turn|turns|turned|turning)\s+out\b", re.I),
    "phrasal_fill_out": re.compile(
        r"\b(fill|fills|filled|filling)\s+(?:\w+\s+){0,2}(out|in)\b|"
        r"\b(check|checks|checked|checking)\s+out\b", re.I),
    "phrasal_set_up": re.compile(
        r"\b(set|sets|setting)\s+(?:\w+\s+){0,2}up\b|\b(broke|break|breaks|breaking|broken)\s+down\b", re.I),
    "phrasal_calm_down": re.compile(
        r"\b(calm|calms|calmed|calming)\s+(?:\w+\s+){0,2}down\b|"
        r"\b(slow|slows|slowed|slowing)\s+down\b|"
        r"\b(clean|cleans|cleaned|cleaning)\s+(?:\w+\s+){0,2}up\b", re.I),
}

DISCOURSE_EN = {
    "discourse_actually": re.compile(
        r"\b(actually|in fact|to be honest|honestly)\b", re.I),
    "discourse_probably": re.compile(
        r"\b(probably|maybe|perhaps)\b", re.I),
    "discourse_though": re.compile(
        r"\b(though|although|however|even though)\b", re.I),
    "discourse_by_the_way": re.compile(
        r"\b(by the way|speaking of|anyway)\b", re.I),
    "discourse_as_far_as": re.compile(
        r"\b(as far as i know|as far as i can tell|as far as i remember)\b", re.I),
    "discourse_turns_out": re.compile(
        r"\b(it turns out|it turned out|turned out|turns out)\b", re.I),
    "discourse_kind_of": re.compile(
        r"\b(kind of|sort of|a bit|a little)\b", re.I),
    "discourse_at_least": re.compile(
        r"\b(at least|in the end|after all)\b", re.I),
    "discourse_no_wonder": re.compile(
        r"\b(no wonder|that explains why)\b|\bthat's why\b", re.I),
    "discourse_on_purpose": re.compile(
        r"\b(on purpose|by mistake|by accident|accidentally)\b", re.I),
}


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
    if pattern in PHRASAL_EN:
        return bool(PHRASAL_EN[pattern].search(n))
    if pattern in DISCOURSE_EN:
        return bool(DISCOURSE_EN[pattern].search(t))
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
    "phrasal_get_up": r"(起床|起来|醒来|睡醒|叫醒|起不来)",
    "phrasal_put_on": r"(穿上|戴上|换上|脱下|脱掉|试穿|加.{0,2}件)",
    "phrasal_pick_up": r"(接|送|取|拿|搬|顺路|放到|放下|送到)",
    "phrasal_turn_on_off": r"(打开|开灯|开电脑|开电视|开空调|关灯|关门|关掉|关上|关机|开一下)",
    "phrasal_look_for": r"(找|寻找|查|打听|发现|不见|丢了|营业时间)",
    "phrasal_figure_out": r"(弄明白|搞清楚|想通|搞懂|弄懂|弄清楚|想清楚|研究|想明白)",
    "phrasal_go_back": r"(回来|回去|返回|回到|回家|回公司|回学校|回酒店|回座位|回老家)",
    "phrasal_go_out": r"(出去|出门|聚会|逛街|一起玩|走走|喝一杯|旅游)",
    "phrasal_work_out": r"(锻炼|健身|运动|解决|想出|商量|办法|顺利)",
    "phrasal_run_out": r"(用完|没了|喝完了|吃完了|花完|没电|不够|快没|用光)",
    "phrasal_end_up": r"(出现|到场|没来|最后|结果|竟然|变成|走到|待了)",
    "phrasal_turn_out": r"(结果|原来|没想到|发现|竟然是|虚惊一场)",
    "phrasal_fill_out": r"(填表|填|表格|申请|问卷|结账|退房|登记|报销)",
    "phrasal_set_up": r"(安装|设置|布置|安排|调试|准备|坏|故障|出问题|死机|抛锚|打不开)",
    "phrasal_calm_down": r"(冷静|别急|慢点|放松|平静|打扫|收拾|清理|安慰)",
    "discourse_actually": r"(其实|实际上|说实话|老实说|事实上)",
    "discourse_probably": r"(可能|也许|大概|说不定|估计|应该会)",
    "discourse_though": r"(不过|虽然|但是|可是|然而|尽管|但)",
    "discourse_by_the_way": r"(顺便|对了|话说|顺便问)",
    "discourse_as_far_as": r"(据我了解|据我所知|就我了解|就我所知|我记得|印象中)",
    "discourse_turns_out": r"(原来|结果|没想到|竟然|才发现|虚惊一场)",
    "discourse_kind_of": r"(有点|有些|稍微|挺|还算|一点)",
    "discourse_at_least": r"(至少|最后|毕竟|总算|还是)",
    "discourse_no_wonder": r"(难怪|怪不得|原来如此|所以)",
    "discourse_on_purpose": r"(故意|不小心|无意|误|不是故意|留一盏灯)",
}


def passes_zh(pattern, zh):
    rx = ZH_CHECKS.get(pattern)
    if not rx:
        raise ValueError(f"Unknown pattern: {pattern}")
    return bool(re.search(rx, zh))


MAX_WORDS = {"grammar": 18, "narrative": 24, "phrasal": 18, "discourse": 20}
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
    "phrasal_get_up": "wake up or get up (phrasal verb)",
    "phrasal_put_on": "put on or take off (clothes or shoes)",
    "phrasal_pick_up": "pick up or drop off (a person or thing)",
    "phrasal_turn_on_off": "turn on or turn off (a device or light)",
    "phrasal_look_for": "look for or find out",
    "phrasal_figure_out": "figure out (work out an answer or reason)",
    "phrasal_go_back": "come back or go back",
    "phrasal_go_out": "go out or hang out",
    "phrasal_work_out": "work out (exercise or solve)",
    "phrasal_run_out": "run out of (something)",
    "phrasal_end_up": "show up or end up",
    "phrasal_turn_out": "turn out (the result was ...)",
    "phrasal_fill_out": "fill out / fill in a form, or check out",
    "phrasal_set_up": "set up, or break down (a device or machine)",
    "phrasal_calm_down": "calm down, slow down, or clean up",
    "discourse_actually": "actually / in fact / to be honest",
    "discourse_probably": "probably / maybe / perhaps",
    "discourse_though": "though / although / however",
    "discourse_by_the_way": "by the way / speaking of",
    "discourse_as_far_as": "as far as I know / as far as I can tell",
    "discourse_turns_out": "it turns out / it turned out",
    "discourse_kind_of": "kind of / sort of / a bit",
    "discourse_at_least": "at least / in the end / after all",
    "discourse_no_wonder": "no wonder / that explains why",
    "discourse_on_purpose": "on purpose / by mistake / accidentally",
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
    "phrasal_get_up": [
        "早上闹钟响了但不想起床", "周末睡到很晚才起", "早上叫孩子起床", "出差时早起赶车",
        "昨晚没睡好今天起不来", "定闹钟提醒自己起床", "早上醒来先看手机", "起床后先喝水",
        "冬天早上很难起床", "早起去跑步",
    ],
    "phrasal_put_on": [
        "出门前穿外套", "下雨天穿雨鞋", "进屋后脱下外套", "试穿新买的衣服",
        "戴帽子防晒", "开会前换上正装", "运动前换上运动鞋", "睡觉前脱掉袜子",
        "天气冷加一件毛衣", "进门前脱鞋",
    ],
    "phrasal_pick_up": [
        "下班顺路接孩子", "去机场接朋友", "开车送同事回家", "把快递从驿站取回来",
        "在餐厅取外卖", "把垃圾拿到楼下", "送孩子去学校", "让司机在门口接你",
        "帮朋友取行李", "把东西放到寄存处",
    ],
    "phrasal_turn_on_off": [
        "进屋开灯", "出门关空调", "睡前关电视", "开电脑准备工作",
        "手机没电找充电器", "开热水器洗澡", "关掉厨房的灯", "开暖气取暖",
        "关掉吵闹的电视", "开会前关手机铃声",
    ],
    "phrasal_look_for": [
        "找钥匙出门", "在超市找牛奶", "上网查资料", "打听租房信息",
        "找一份兼职", "发现钱包不见了", "查一下营业时间", "问路找地铁站",
        "找丢失的耳机", "发现孩子发烧了",
    ],
    "phrasal_figure_out": [
        "弄明白新软件怎么用", "想通朋友为什么生气", "搞清楚怎么换乘", "弄懂一道数学题",
        "想明白下一步怎么做", "搞懂机器的用法", "弄明白账单为什么这么高", "研究怎么修好打印机",
        "想清楚要不要换工作", "弄明白孩子为什么哭",
    ],
    "phrasal_go_back": [
        "下班后回公司拿东西", "放假回老家看父母", "忘带东西回家取", "旅行结束回到城市",
        "送完人再返回家", "回学校取毕业证", "从医院回家休息", "吃完饭再回办公室",
        "回到酒店拿行李", "回到座位上继续工作",
    ],
    "phrasal_go_out": [
        "周末和朋友出去吃饭", "晚上出去散步", "和朋友出去看电影", "下班后出去喝一杯",
        "周末一起出去玩", "天气好出去走走", "晚上不想出去待在家", "和朋友出去逛街",
        "出去买点东西", "放假出去旅游",
    ],
    "phrasal_work_out": [
        "每周去健身房锻炼", "在家跟着视频锻炼", "早上跑步锻炼身体", "事情最后顺利解决",
        "商量出一个办法", "身体不舒服还坚持锻炼", "锻炼后洗澡", "想出一个省钱的办法",
        "两个人一起想办法", "锻炼太多第二天很累",
    ],
    "phrasal_run_out": [
        "家里没牛奶了要去买", "手机快没电了", "出门发现汽油不够", "做饭时发现没盐了",
        "咖啡喝完了", "月底钱快花完了", "打印纸用完了", "时间不够了要加快",
        "纸巾用完了", "食物吃完了要再买",
    ],
    "phrasal_end_up": [
        "朋友说来吃饭最后没出现", "聚会来了很多人", "开会迟到的人终于出现", "本打算回家最后去了别处",
        "买了一件没打算买的东西", "迷路最后走到一个公园", "加班到最后很晚才回家", "约好见面对方没出现",
        "本来只想待一会儿最后待了一下午", "计划改变最后做了别的",
    ],
    "phrasal_turn_out": [
        "以为难结果很简单", "以为是玩笑结果是真的", "结果发现钱包在包里", "原来他早就知道了",
        "面试结果比想象的好", "天气预报说下雨结果没下", "结果那家店关门了", "原来两个人认识",
        "结果是虚惊一场", "结果比预期便宜很多",
    ],
    "phrasal_fill_out": [
        "入住酒店填表", "办卡填申请表", "报销要填表格", "网上填问卷",
        "退房结账", "在超市结账", "医院填就诊单", "报名考试填信息",
        "结账时发现少算", "填完表交给工作人员",
    ],
    "phrasal_set_up": [
        "安装新打印机", "设置新手机", "布置生日聚会", "电脑突然死机",
        "电梯出故障", "车在路上抛锚", "开会前调试设备", "在客厅装书架",
        "网站打不开", "安排一次视频会议",
    ],
    "phrasal_calm_down": [
        "孩子哭闹安慰他", "朋友生气劝他冷静", "自己紧张时深呼吸", "遇到麻烦别着急",
        "开车慢一点", "说话慢一点", "收拾房间", "打扫厨房",
        "清理桌上的东西", "事后慢慢平静下来",
    ],
    "discourse_actually": [
        "纠正别人的误会", "说出真实想法", "其实不想去聚会", "实话实说菜不好吃",
        "其实已经买过了", "其实我不住在这附近", "说实话有点累", "其实价格没那么贵",
        "其实我更喜欢在家", "事实上计划已经改了",
    ],
    "discourse_probably": [
        "猜朋友会迟到", "可能下雨带伞", "大概要等半小时", "也许明天有空",
        "估计他已经走了", "可能忘带钥匙了", "大概不会涨价", "说不定会提前到",
        "应该会喜欢这个礼物", "可能还要再等等",
    ],
    "discourse_though": [
        "东西贵但质量好", "虽然累但很开心", "天气不好不过还是出门了", "他答应了然而没来",
        "便宜可是不太好看", "虽然忙还是回了消息", "路远不过风景好", "虽然难但值得学",
        "味道一般但是便宜", "不过我还是想试试",
    ],
    "discourse_by_the_way": [
        "顺便问一下时间", "对了明天开会", "话说你最近怎么样", "顺便说一句钥匙在桌上",
        "对了记得带伞", "顺便说一下地址变了", "话说这家店新开的", "对了你吃饭了吗",
        "顺便问一句要不要一起", "对了下午有快递",
    ],
    "discourse_as_far_as": [
        "据我所知今天不开门", "据我了解他搬家了", "就我知道的价格没变", "我记得会议改到周五",
        "据我了解这家店很有名", "就我所知还没有通知", "据我所知地铁更快", "印象中他不太吃辣",
        "据我了解活动免费", "就我知道的今天有雨",
    ],
    "discourse_turns_out": [
        "原来钥匙在口袋里", "结果那家店倒闭了", "没想到是同乡", "原来他已经结婚了",
        "结果发现买错了", "原来问题出在电池", "结果比想的简单", "原来他早就知道",
        "没想到会遇到老朋友", "结果是虚惊一场",
    ],
    "discourse_kind_of": [
        "有点累想休息", "这件事有点麻烦", "稍微有点贵", "我有点担心",
        "今天有点冷", "这道菜有点辣", "他有点不高兴", "房间稍微小一点",
        "有点想家", "还算顺利",
    ],
    "discourse_at_least": [
        "至少没迟到", "最后总算赶上了", "毕竟第一次做", "至少价格还算合理",
        "最后还是决定去", "至少天气不错", "毕竟不是他的错", "最后还是买了",
        "至少比上次好", "最后还是说了实话",
    ],
    "discourse_no_wonder": [
        "难怪他没来原来生病了", "怪不得这么便宜原来是旧的", "难怪堵车原来在修路", "难怪他累原来加了一周班",
        "怪不得没回消息手机没电", "难怪店关了老板退休了", "难怪味道熟悉是妈妈做的", "怪不得他生气你迟到了",
        "难怪这么冷窗户开着", "难怪没人排队今天工作日",
    ],
    "discourse_on_purpose": [
        "故意不说话", "不小心打翻杯子", "不是故意迟到的", "误把盐当成糖",
        "故意绕远路散步", "不小心删了文件", "故意留一盏灯", "不小心说漏嘴",
        "故意早点到", "不小心坐过站",
    ],
}
