#!/usr/bin/env python3
"""Generate and validate a small pilot batch of grammar/narrative cards."""

import argparse
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from pack_patterns import CJK_RE, MAX_WORDS, MIN_WORDS, passes_en, word_count  # noqa: E402

TEMPLATE = ROOT / "prompts" / "generate_pack.txt"
SYSTEM = "You write English translations for bilingual flashcards. Output only valid JSON."


def item(scene, scene_zh, scene_en, pack, pattern, micro, micro_zh, target, situation, hint, zh):
    groups = {"grammar": "语法句型", "narrative": "个人叙事", "phrasal": "短语动词", "discourse": "口语衔接"}
    return {
        "scene": scene,
        "scene_zh": scene_zh,
        "scene_en": scene_en,
        "group": groups[pack],
        "phase": 4 if pack in ("phrasal", "discourse") else 3,
        "pack": pack,
        "pattern": pattern,
        "topic": pattern.replace("narrative_", "") if pack == "narrative" else None,
        "micro": micro,
        "micro_zh": micro_zh,
        "target": target,
        "situation": situation,
        "hint": hint,
        "zh": zh,
        "min_words": MIN_WORDS,
        "max_words": MAX_WORDS[pack],
    }


ITEMS = [
    item("grammar_past_simple", "语法·一般过去时", "Grammar: Past Simple", "grammar", "past_simple",
         "everyday", "日常经历", "past simple + a past time phrase",
         "描述上周末做的一件具体事情", "Mention when it happened, e.g. last weekend.",
         "我上周末去看了我爷爷奶奶。"),
    item("grammar_past_continuous", "语法·过去进行时", "Grammar: Past Continuous", "grammar", "past_continuous",
         "interruption", "被打断的事", "past continuous + when/while",
         "描述昨晚某个时间正在做什么，以及被打断的事", "Use was/were + -ing and when or while.",
         "我昨晚八点在做饭，突然有人敲门。"),
    item("grammar_present_perfect", "语法·现在完成时", "Grammar: Present Perfect", "grammar", "present_perfect",
         "experience", "经历", "present perfect (have/has + past participle)",
         "讲一次旅行经历，说明去过或没去过哪里", "Use have/has been and ever or never.",
         "我去过海边三次，但还没去过山里。"),
    item("grammar_future_going_to", "语法·going to 计划", "Grammar: Future Plans with Going To", "grammar", "going_to",
         "near_future", "近期安排", "going to for plans",
         "说说明年或下个月的安排", "Use am/is/are going to.",
         "我下个月打算搬到新公寓。"),
    item("grammar_future_will", "语法·will 将来", "Grammar: Future with Will", "grammar", "will",
         "decision", "临时决定", "will for a decision or offer",
         "朋友遇到麻烦，你当场决定帮忙", "Use will for a decision made now.",
         "别担心，我明天会帮你修电脑。"),
    item("grammar_used_to", "语法·used to", "Grammar: Used To", "grammar", "used_to",
         "childhood", "童年习惯", "used to for past habits",
         "对比小时候和现在的习惯", "Include both the past habit and what you do now.",
         "我小时候每天走路去上学，现在坐地铁。"),
    item("grammar_first_conditional", "语法·真实条件句", "Grammar: First Conditional", "grammar", "first_conditional",
         "everyday", "日常选择", "first conditional (if + present, will)",
         "说明如果明天天气好，你们会做什么", "Use if + present simple and will.",
         "如果明天不下雨，我们就去公园野餐。"),
    item("grammar_second_conditional", "语法·虚拟条件句", "Grammar: Second Conditional", "grammar", "second_conditional",
         "advice", "假设建议", "second conditional (if + past, would)",
         "给朋友一个假设性的建议", "Use if I were you or if + past, and would.",
         "如果我是你，我会先跟老板谈一谈。"),
    item("grammar_modals_obligation", "语法·义务与规定", "Grammar: Obligation and Rules", "grammar", "modals_obligation",
         "public", "公共场所", "obligation or permission (must/have to/be allowed to)",
         "说明小区里的规定", "Use be allowed to, must not, or have to.",
         "在这个小区，晚上十点以后不能放音乐。"),
    item("grammar_comparatives", "语法·比较级", "Grammar: Comparatives", "grammar", "comparatives",
         "things", "事物比较", "comparatives (cheaper than / faster)",
         "比较地铁和打车", "Use -er/more ... than or as ... as.",
         "坐地铁比打车便宜，但打车更快。"),
    item("grammar_tag_questions", "语法·附加疑问句", "Grammar: Tag Questions", "grammar", "tag_questions",
         "confirm", "确认事实", "tag question (..., right? / didn't you?)",
         "向朋友确认一个已经发生的细节", "End with a short tag question.",
         "你把窗户关上了，对吧？"),
    item("grammar_relative_clauses", "语法·定语从句", "Grammar: Relative Clauses", "grammar", "relative_clauses",
         "people", "描述人", "relative clause (who/which/where)",
         "说明是哪一个帮助了你的人", "Use who or that after a person.",
         "就是那个穿蓝色外套的人帮我找到钱包的。"),
    item("grammar_gerund_infinitive", "语法·动名词与不定式", "Grammar: Gerunds and Infinitives", "grammar", "gerund_infinitive",
         "likes", "喜好", "gerund and infinitive (enjoy doing / want to do)",
         "说周末喜欢做什么、想学什么", "Use one -ing form after a verb and one to-infinitive.",
         "我喜欢周末做饭，也想学做甜点。"),
    item("grammar_passive", "语法·被动语态", "Grammar: Passive Voice", "grammar", "passive",
         "repairs", "维修", "passive voice (be + past participle)",
         "说明某样东西是什么时候修好的", "Use was/were + past participle.",
         "我的自行车是上周修好的。"),
    item("grammar_reported_speech", "语法·转述句", "Grammar: Reported Speech", "grammar", "reported_speech",
         "message", "转述消息", "reported speech (told/said + clause)",
         "转述别人告诉你的一个消息", "Use told me or said that and change the tense.",
         "他告诉我会议改到下午三点了。"),
    item("grammar_past_simple", "语法·一般过去时", "Grammar: Past Simple", "grammar", "past_simple",
         "work_study", "工作学习", "past simple + a past time phrase",
         "描述昨天工作中发生的一件意外", "Use the past simple and yesterday.",
         "昨天开会的时候，我的电脑突然坏了。"),
    item("grammar_present_perfect", "语法·现在完成时", "Grammar: Present Perfect", "grammar", "present_perfect",
         "duration", "持续到现在", "present perfect with for/since",
         "说明在一个地方住了多久", "Use have/has + past participle and for.",
         "我在这座城市住了五年了。"),
    item("grammar_first_conditional", "语法·真实条件句", "Grammar: First Conditional", "grammar", "first_conditional",
         "travel", "出行状况", "first conditional (if + present, will)",
         "说明赶不上车时的安排", "Use if + present simple and will.",
         "如果我们赶不上这班车，就坐下一班。"),
    item("grammar_used_to", "语法·used to", "Grammar: Used To", "grammar", "used_to",
         "lifestyle", "生活方式改变", "used to for a past habit",
         "对比以前的饮食习惯和现在", "Use used to + base verb and now.",
         "我以前每天喝咖啡，现在改喝茶了。"),
    item("grammar_comparatives", "语法·比较级", "Grammar: Comparatives", "grammar", "comparatives",
         "places", "地点比较", "comparatives (better than / more expensive)",
         "比较两家店的服务和价格", "Use better than and more ... than.",
         "这家店的服务比那家好，但价格也更贵。"),
    item("narrative_daily_routine", "叙事·日常作息", "Narrative: Daily Routine", "narrative", "narrative_daily_routine",
         "weekday", "工作日", "present simple + frequency adverb",
         "描述一个普通工作日的作息", "Use usually, first, then, or every day.",
         "我平时七点起床，先跑步，然后吃早饭。"),
    item("narrative_last_weekend", "叙事·上周末", "Narrative: Last Weekend", "narrative", "narrative_last_weekend",
         "activities", "做了什么", "past simple + connector (because/but/so)",
         "讲上周末做了什么，感觉怎么样", "Mention last weekend, hiking with friends, being tired, and the beautiful scenery. Use although or though.",
         "上周末我和朋友去爬山，虽然很累，但风景特别美。"),
    item("narrative_childhood", "叙事·童年回忆", "Narrative: Childhood Memories", "narrative", "narrative_childhood",
         "home", "小时候的家", "used to / when I was / grew up",
         "讲小时候住在哪里、经常做什么", "Say where you lived and what you often did.",
         "我小时候住在一个小城市，经常在河边玩。"),
    item("narrative_future_plans", "叙事·未来计划", "Narrative: Future Plans", "narrative", "narrative_future_plans",
         "next_year", "明年计划", "going to / will / plan to",
         "说明明年的计划和想做的事", "Use going to or plan to.",
         "明年我打算换一份工作，也想多陪陪家人。"),
    item("narrative_health_habits", "叙事·健康习惯", "Narrative: Health Habits", "narrative", "narrative_health_habits",
         "changes", "最近改变", "used to / recently / frequency",
         "讲健康习惯的前后变化", "Use used to for the past and now for the present, and say how often you swim.",
         "我以前几乎不运动，现在每周游两次泳。"),
    item("narrative_work_study_problems", "叙事·工作学习问题", "Narrative: Work and Study Problems", "narrative", "narrative_work_study_problems",
         "work", "工作", "because/so/but + a problem",
         "讲一个工作项目最近的问题和原因", "Use because or so to explain the reason.",
         "这个项目最近进度很慢，因为有两个同事请假了。"),
    item("narrative_travel_story", "叙事·旅行故事", "Narrative: Travel Story", "narrative", "narrative_travel_story",
         "unexpected", "意外", "past simple/past continuous + connector",
         "讲一次旅行中迷路并得到帮助的经历", "Say where you were traveling, that you got lost, and how the old man helped.",
         "去年我在外地旅行时迷路了，一位老人把我送到了车站。"),
    item("narrative_movies_books", "叙事·电影与书", "Narrative: Movies and Books", "narrative", "narrative_movies_books",
         "compare", "比较", "opinion verb + comparative",
         "评价最近看的一部电影，并和原著比较", "Use I think and not as ... as or better than.",
         "我最近看了一部电影，我觉得没有原著小说好看。"),
    item("narrative_relationships", "叙事·人际关系", "Narrative: Relationships", "narrative", "narrative_relationships",
         "friends", "朋友", "present perfect / relative clause",
         "讲一个认识很久、经常帮助你的朋友", "Mention that this person is your friend, how long you have known them, and how often they help.",
         "我有一个认识十年的朋友，他总是在我需要的时候帮我。"),
    item("narrative_wishes_regrets", "叙事·愿望与遗憾", "Narrative: Wishes and Regrets", "narrative", "narrative_wishes_regrets",
         "regret", "遗憾", "wish / if only / should have",
         "讲一件后悔没做的事", "Use I wish I had or should have.",
         "我真希望当初多学一门外语，现在工作会更方便。"),
    item("phrasal_get_up", "短语·起床与醒来", "Phrasal: Wake Up and Get Up", "phrasal", "phrasal_get_up",
         "morning", "早上", "wake up / get up",
         "说早上闹钟响了但不想起床", "Use wake up or get up, not just wake or rise.",
         "早上闹钟响了，我还是不想起床。"),
    item("phrasal_put_on", "短语·穿戴与脱下", "Phrasal: Put On and Take Off", "phrasal", "phrasal_put_on",
         "weather", "天气变化", "put on / take off",
         "说出门前穿上外套、戴上围巾", "Use put on for clothes or accessories.",
         "出门前我穿上外套，又戴上了围巾。"),
    item("phrasal_pick_up", "短语·接送与拿起", "Phrasal: Pick Up and Drop Off", "phrasal", "phrasal_pick_up",
         "people", "接送人", "pick up / drop off",
         "说下班后顺路接孩子", "Use pick up for collecting a person.",
         "下班后我顺路去接孩子。"),
    item("phrasal_turn_on_off", "短语·开关电器", "Phrasal: Turn On and Turn Off", "phrasal", "phrasal_turn_on_off",
         "home", "家里", "turn on / turn off",
         "说进屋后打开客厅的灯", "Use turn on for a light or device.",
         "进屋后我把客厅的灯打开。"),
    item("phrasal_look_for", "短语·寻找与发现", "Phrasal: Look For and Find Out", "phrasal", "phrasal_look_for",
         "search", "寻找东西", "look for / find out",
         "说找了半天钥匙，最后发现它在包里", "Use look for while searching and find out for discovering.",
         "我找了半天钥匙，最后发现它在包里。"),
    item("phrasal_figure_out", "短语·弄明白", "Phrasal: Figure Out", "phrasal", "phrasal_figure_out",
         "understand", "理解情况", "figure out",
         "说花了一个晚上才弄明白软件怎么用", "Use figure out, not just know or understand.",
         "我花了一个晚上才弄明白这个软件怎么用。"),
    item("phrasal_go_back", "短语·回来与返回", "Phrasal: Come Back and Go Back", "phrasal", "phrasal_go_back",
         "travel", "出行回家", "come back / go back",
         "说忘带手机了，得回家一趟", "Use go back or come back.",
         "我忘带手机了，得回家一趟。"),
    item("phrasal_go_out", "短语·出门与聚会", "Phrasal: Go Out and Hang Out", "phrasal", "phrasal_go_out",
         "friends", "和朋友", "go out / hang out",
         "说周末一般出去吃饭", "Use go out for leaving home to do something.",
         "周末我们一般出去吃饭。"),
    item("phrasal_work_out", "短语·锻炼与解决", "Phrasal: Work Out", "phrasal", "phrasal_work_out",
         "exercise", "锻炼", "work out",
         "说每周去三次健身房锻炼", "Use work out for exercise.",
         "我每周去三次健身房锻炼。"),
    item("phrasal_run_out", "短语·用完与缺少", "Phrasal: Run Out Of", "phrasal", "phrasal_run_out",
         "home", "家里", "run out of",
         "说家里的牛奶喝完了，得去买", "Use run out of, not just finish or use.",
         "家里的牛奶喝完了，我得去买。"),
    item("phrasal_end_up", "短语·出现与结果", "Phrasal: Show Up and End Up", "phrasal", "phrasal_end_up",
         "people", "人和场合", "show up / end up",
         "说朋友说好来吃饭，最后没出现", "Use show up for arriving or appearing.",
         "朋友说好来吃饭，最后却没出现。"),
    item("phrasal_turn_out", "短语·结果与真相", "Phrasal: Turn Out", "phrasal", "phrasal_turn_out",
         "expectation", "和预想不同", "turn out",
         "说以为菜很难做，结果挺简单", "Use turn out to introduce the actual result.",
         "我以为这道菜很难做，结果挺简单的。"),
    item("phrasal_fill_out", "短语·填表与结账", "Phrasal: Fill Out and Check Out", "phrasal", "phrasal_fill_out",
         "forms", "填表格", "fill out / fill in",
         "说入住酒店要先填一张表", "Use fill out for a form.",
         "入住酒店的时候要先填一张表。"),
    item("phrasal_set_up", "短语·安装与故障", "Phrasal: Set Up and Break Down", "phrasal", "phrasal_set_up",
         "install", "安装设置", "set up",
         "说新买的打印机还没安装好", "Use set up for installing or configuring.",
         "新买的打印机我还没安装好。"),
    item("phrasal_calm_down", "短语·冷静与收拾", "Phrasal: Calm Down, Slow Down, Clean Up", "phrasal", "phrasal_calm_down",
         "emotion", "情绪", "calm down / slow down / clean up",
         "说孩子哭得很厉害，怎么哄都停不下来", "Use calm down for becoming calm.",
         "孩子哭得很厉害，怎么哄都冷静不下来。"),
    item("discourse_actually", "口语·其实与说实话", "Discourse: Actually and To Be Honest", "discourse", "discourse_actually",
         "honesty", "真实想法", "actually / in fact / to be honest",
         "说其实不太喜欢喝咖啡", "Start with actually or to be honest.",
         "其实我不太喜欢喝咖啡。"),
    item("discourse_probably", "口语·可能大概", "Discourse: Probably and Maybe", "discourse", "discourse_probably",
         "guess", "猜测", "probably / maybe / perhaps",
         "猜他可能已经走了", "Use probably or maybe.",
         "他可能已经走了。"),
    item("discourse_though", "口语·转折让步", "Discourse: Though and However", "discourse", "discourse_though",
         "contrast", "对比", "though / although / however",
         "说衣服有点贵，不过质量很好", "Use though or although to contrast.",
         "这件衣服有点贵，不过质量很好。"),
    item("discourse_by_the_way", "口语·顺便说", "Discourse: By the Way", "discourse", "discourse_by_the_way",
         "reminder", "提醒", "by the way / speaking of",
         "顺便问明天几点开会", "Use by the way to add a new topic.",
         "顺便问一下，明天几点开会？"),
    item("discourse_as_far_as", "口语·据我所知", "Discourse: As Far As I Know", "discourse", "discourse_as_far_as",
         "facts", "已知信息", "as far as I know",
         "说据自己所知这家店周末不开门", "Use as far as I know.",
         "据我所知，这家店周末不开门。"),
    item("discourse_turns_out", "口语·原来如此", "Discourse: It Turns Out", "discourse", "discourse_turns_out",
         "discovery", "发现真相", "it turns out / it turned out",
         "说原来钥匙一直在口袋里", "Use it turns out or it turned out.",
         "原来钥匙一直在我的口袋里。"),
    item("discourse_kind_of", "口语·有点稍微", "Discourse: Kind Of and Sort Of", "discourse", "discourse_kind_of",
         "feeling", "感受", "kind of / sort of / a bit",
         "说今天有点累，想早点休息", "Use kind of or a bit.",
         "今天有点累，我想早点休息。"),
    item("discourse_at_least", "口语·至少与毕竟", "Discourse: At Least and After All", "discourse", "discourse_at_least",
         "outcome", "最终结果", "at least / in the end / after all",
         "说虽然迟到了，但至少赶上末班车", "Use at least to mention the good side.",
         "虽然迟到了，但至少赶上了最后一班车。"),
    item("discourse_no_wonder", "口语·难怪", "Discourse: No Wonder", "discourse", "discourse_no_wonder",
         "realization", "恍然大悟", "no wonder / that explains why",
         "说难怪你没回消息，原来手机没电了", "Use no wonder when you realize the reason.",
         "难怪你没回消息，原来手机没电了。"),
    item("discourse_on_purpose", "口语·故意与不小心", "Discourse: On Purpose and By Mistake", "discourse", "discourse_on_purpose",
         "accident", "不小心", "on purpose / by mistake / accidentally",
         "为迟到道歉，说不是故意的", "Use on purpose or by mistake.",
         "对不起，我不是故意迟到的。"),
    item("phrasal_get_up", "短语·起床与醒来", "Phrasal: Wake Up and Get Up", "phrasal", "phrasal_get_up",
         "morning", "早上", "wake up / get up",
         "说周末通常睡到九点才起床", "Use wake up or get up.",
         "周末我通常睡到九点才起床。"),
    item("phrasal_pick_up", "短语·接送与拿起", "Phrasal: Pick Up and Drop Off", "phrasal", "phrasal_pick_up",
         "people", "接送人", "pick up / drop off",
         "说朋友开车到门口来接你", "Use pick up for collecting someone.",
         "朋友让我在门口等他，他会开车来接我。"),
    item("phrasal_figure_out", "短语·弄明白", "Phrasal: Figure Out", "phrasal", "phrasal_figure_out",
         "problem", "解决问题", "figure out",
         "说一起想办法，终于弄清楚问题出在哪", "Use figure out.",
         "我们一起想办法，终于弄清楚了问题出在哪。"),
    item("discourse_actually", "口语·其实与说实话", "Discourse: Actually and To Be Honest", "discourse", "discourse_actually",
         "honesty", "真实想法", "actually / in fact / to be honest",
         "说觉得价格有点高", "Start with to be honest or actually.",
         "说实话，我觉得这个价格有点高。"),
    item("discourse_kind_of", "口语·有点稍微", "Discourse: Kind Of and Sort Of", "discourse", "discourse_kind_of",
         "degree", "程度", "kind of / sort of / a bit",
         "说味道还不错，就是稍微有点贵", "Use a bit or kind of to soften the comment.",
         "这家店的味道还算不错，就是稍微有点贵。"),
]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default="qwen2.5:7b")
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--temperature", type=float, default=0.4)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--pause", type=float, default=3.0)
    p.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    p.add_argument("--packs", nargs="*", help="only these pack ids (grammar/narrative/phrasal/discourse)")
    p.add_argument("--out-dir", default=str(ROOT / "data" / "pilot" / "sentences"))
    p.add_argument(
        "--reference-dir",
        nargs="+",
        default=[
            str(ROOT / "data" / "sentences_polished"),
            str(ROOT / "data" / "packs" / "final"),
        ],
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verify-dir", help="check pattern compliance for a directory of records")
    p.add_argument("--finalize", action="store_true", help="merge polished output, reverting lost patterns")
    p.add_argument("--raw-dir", default=str(ROOT / "data" / "pilot" / "sentences"))
    p.add_argument("--polished-dir", default=str(ROOT / "data" / "pilot" / "polished"))
    p.add_argument("--final-dir", default=str(ROOT / "data" / "pilot" / "final"))
    p.add_argument("--overrides", default=str(ROOT / "data" / "pilot" / "overrides.json"))
    return p.parse_args()


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def make_uid(scene, zh):
    return f"{scene}-{hashlib.sha1(normalize(zh).encode('utf-8')).hexdigest()[:10]}"


def load_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def clean_en(text):
    en = str(text).strip().strip("\"'")
    en = re.sub(r"\s+", " ", en)
    for full, half in (("？", "?"), ("！", "!"), ("。", "."), ("，", ","), ("；", ";"), ("：", ":")):
        en = en.replace(full, half)
    if en and en[-1] not in ".?!":
        en += "."
    if en:
        en = en[0].upper() + en[1:]
    return en


def build_prompt(batch):
    lines = []
    for i, it in enumerate(batch, 1):
        lines.append(
            f'{i}. zh: {it["zh"]} | target: {it["target"]} | note: {it["hint"]}'
        )
    return TEMPLATE.read_text(encoding="utf-8").replace("{items}", "\n".join(lines))


def call_ollama(args, prompt, count):
    payload = {
        "model": args.model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "num_predict": max(400, count * 90 + 200),
            "seed": random.randint(0, 2**31 - 1),
        },
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }
    req = request.Request(
        args.ollama_url.rstrip("/") + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=args.timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("message", {}).get("content", "")


def extract_pairs(content):
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise
        data = json.loads(text[start : end + 1])
    if isinstance(data, dict):
        data = data.get("pairs") or data.get("sentences") or []
    if not isinstance(data, list):
        raise ValueError("JSON root is not a list of pairs")
    return data


def load_reference(reference_dirs):
    rows = []
    for reference_dir in reference_dirs:
        for path in sorted(Path(reference_dir).glob("*.jsonl")):
            rows.extend(load_jsonl(path))
    return rows


def is_duplicate(zh, en, ref_rows, pilot_rows):
    nz, ne = normalize(zh), normalize(en)
    for r in ref_rows + pilot_rows:
        if normalize(r["zh"]) == nz or normalize(r["en"]) == ne:
            return True
        if SequenceMatcher(None, nz, normalize(r["zh"])).ratio() >= 0.9:
            return True
        if SequenceMatcher(None, ne, normalize(r["en"])).ratio() >= 0.9:
            return True
    return False


def record_for(it, en, model):
    tags = [f"pack::{it['pack']}", f"pattern::{it['pattern']}"]
    if it["pack"] == "narrative":
        tags.append(f"topic::{it['topic']}")
    return {
        "uid": make_uid(it["scene"], it["zh"]),
        "scene": it["scene"],
        "scene_zh": it["scene_zh"],
        "scene_en": it["scene_en"],
        "group": it["group"],
        "phase": it["phase"],
        "micro": it["micro"],
        "micro_zh": it["micro_zh"],
        "zh": it["zh"],
        "en": en,
        "sub": it["situation"],
        "angle": it["target"],
        "pack": it["pack"],
        "pattern": it["pattern"],
        "topic": it["topic"],
        "tags": tags,
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_record(out_dir, it, rec):
    path = Path(out_dir) / f"{it['scene']}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def existing_uids(out_dir):
    uids = set()
    for path in Path(out_dir).glob("*.jsonl"):
        uids.update(r["uid"] for r in load_jsonl(path))
    return uids


def validate(it, en):
    if CJK_RE.search(en):
        return "en_contains_chinese"
    n = word_count(en)
    if n < it["min_words"] or n > it["max_words"]:
        return f"word_count_{n}"
    if not passes_en(it["pattern"], en):
        return "pattern_miss"
    return None


def selected_items(args):
    return [it for it in ITEMS if not args.packs or it["pack"] in args.packs]


def generate(args):
    items = selected_items(args)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    done = existing_uids(out_dir)
    pending = [it for it in items if make_uid(it["scene"], it["zh"]) not in done]
    ref_rows = load_reference(args.reference_dir)
    pilot_rows = []

    print(f"Pilot items: {len(items)} | already done: {len(items) - len(pending)} | pending: {len(pending)}")
    print(f"Model: {args.model} | batch: {args.batch} | output: {out_dir}")
    for it in pending:
        print(f"  {it['pattern']:<28} {it['scene_zh']} | {it['zh']}")
    if args.dry_run:
        print("\n--- sample prompt ---\n")
        print(build_prompt(pending[: min(3, len(pending))]))
        return

    accepted = 0
    failed = []
    for start in range(0, len(pending), args.batch):
        batch = pending[start : start + args.batch]
        prompt = build_prompt(batch)
        pairs = None
        for attempt in range(args.retries + 1):
            try:
                pairs = extract_pairs(call_ollama(args, prompt, len(batch)))
                break
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                print(f"  retry batch {start // args.batch + 1}: {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(2)
        if not pairs:
            failed.extend((it, "batch_failed") for it in batch)
            continue
        by_id = {}
        for p in pairs:
            if isinstance(p, dict):
                pid = p.get("id")
                if isinstance(pid, str) and pid.isdigit():
                    pid = int(pid)
                if isinstance(pid, int):
                    by_id[pid] = p.get("en", "")
        for i, it in enumerate(batch, 1):
            en = clean_en(by_id.get(i, "")) if by_id.get(i) else ""
            if not en:
                failed.append((it, "missing"))
                continue
            reason = validate(it, en)
            if not reason and is_duplicate(it["zh"], en, ref_rows, pilot_rows):
                reason = "duplicate"
            if reason:
                failed.append((it, reason))
                print(f"  reject {it['pattern']:<28} {reason}: {en}")
                continue
            rec = record_for(it, en, args.model)
            write_record(out_dir, it, rec)
            pilot_rows.append(rec)
            accepted += 1
            print(f"  accept {it['pattern']:<28} {en}")
        if args.pause:
            time.sleep(args.pause)

    for it, reason in list(failed):
        if all(it is not x for x, _ in failed):
            continue
        for attempt in range(args.retries + 1):
            try:
                pairs = extract_pairs(call_ollama(args, build_prompt([it]), 1))
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                print(f"  retry {it['pattern']}: {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(2)
                continue
            by_id = {
                p.get("id"): p.get("en", "")
                for p in pairs
                if isinstance(p, dict) and isinstance(p.get("id"), int)
            }
            en = clean_en(by_id.get(1, "")) if by_id.get(1) else ""
            if not en:
                continue
            problem = validate(it, en)
            if not problem and is_duplicate(it["zh"], en, ref_rows, pilot_rows):
                problem = "duplicate"
            if problem:
                print(f"  retry reject {it['pattern']:<24} {problem}: {en}")
                continue
            rec = record_for(it, en, args.model)
            write_record(out_dir, it, rec)
            pilot_rows.append(rec)
            accepted += 1
            failed = [(x, r) for x, r in failed if x is not it]
            print(f"  recovered {it['pattern']:<24} {en}")
            break
        if args.pause:
            time.sleep(args.pause)

    print(f"\nAccepted {accepted}/{len(pending)} new cards.")
    if failed:
        print("Still failing:")
        for it, reason in failed:
            print(f"  {it['pattern']:<28} {reason} | {it['zh']}")


def verify(args, data_dir):
    rows = []
    for path in sorted(Path(data_dir).glob("*.jsonl")):
        rows.extend(load_jsonl(path))
    index = {(it["scene"], it["zh"]): it for it in selected_items(args)}
    bad = 0
    for rec in rows:
        it = index.get((rec["scene"], rec["zh"]))
        if not it:
            print(f"UNKNOWN {rec['scene']} | {rec['zh']}")
            bad += 1
            continue
        reason = validate(it, rec["en"])
        status = "OK  " if not reason else f"FAIL({reason})"
        print(f"{status} {it['pattern']:<28} {rec['en']}")
        if reason:
            bad += 1
    print(f"\n{len(rows) - bad}/{len(rows)} pass pattern checks")
    return 1 if bad else 0


def finalize(args):
    raw = {}
    for path in sorted(Path(args.raw_dir).glob("*.jsonl")):
        for rec in load_jsonl(path):
            raw[rec["uid"]] = rec
    polished = {}
    for path in sorted(Path(args.polished_dir).glob("*.jsonl")):
        for rec in load_jsonl(path):
            polished[rec["uid"]] = rec
    index = {(it["scene"], it["zh"]): it for it in selected_items(args)}
    overrides = json.loads(Path(args.overrides).read_text(encoding="utf-8")) if Path(args.overrides).exists() else {}
    out_dir = Path(args.final_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("*.jsonl"):
        p.unlink()
    reverted = 0
    for uid, rec in raw.items():
        it = index.get((rec["scene"], rec["zh"]))
        if not it:
            continue
        new = polished.get(uid, {}).get("en", rec["en"])
        if validate(it, new) and not validate(it, rec["en"]):
            rec["polished_en"] = new
            rec["polish_reverted"] = True
            reverted += 1
        else:
            rec["en"] = new
            rec["polish_reverted"] = False
        override = overrides.get(uid)
        if override:
            rec["en"] = override
            rec["manual_override"] = True
        path = out_dir / f"{rec['scene']}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Finalized {len(raw)} cards -> {out_dir} | reverted {reverted} polished rewrites")


def main():
    args = parse_args()
    if args.verify_dir:
        raise SystemExit(verify(args, args.verify_dir))
    if args.finalize:
        finalize(args)
        return
    generate(args)


if __name__ == "__main__":
    main()
