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
TEMPLATE = ROOT / "prompts" / "generate_pack.txt"
SYSTEM = "You write English translations for bilingual flashcards. Output only valid JSON."

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")
PAST_RE = re.compile(
    r"\b(was|were|did|went|came|got|made|took|saw|said|told|had|found|left|gave|bought|"
    r"thought|knew|wanted|needed|liked|worked|booked|ordered|paid|arrived|finished|called|"
    r"asked|looked|tried|started|stopped|changed|moved|opened|closed|lost|met|sent|brought|"
    r"kept|ran|ate|drank|slept|woke|forgot|broke|chose|drove|flew|felt|heard|held|spoke|"
    r"spent|stood|taught|threw|understood|wore|won|wrote|visited|studied|learned|learnt)\b",
    re.I,
)
TIME_RE = re.compile(r"\b(yesterday|last|ago|this morning|when i was|in \d{4})\b", re.I)
FREQ_RE = re.compile(
    r"\b(always|usually|often|sometimes|rarely|never|every day|every morning|"
    r"once a week|twice a week)\b",
    re.I,
)
CONNECTOR_RE = re.compile(
    r"\b(because|but|so|then|after that|although|though|when|while|after)\b", re.I
)


def item(scene, scene_zh, scene_en, pack, pattern, micro, micro_zh, target, situation, hint, zh):
    return {
        "scene": scene,
        "scene_zh": scene_zh,
        "scene_en": scene_en,
        "group": "语法句型" if pack == "grammar" else "个人叙事",
        "pack": pack,
        "pattern": pattern,
        "topic": pattern.replace("narrative_", "") if pack == "narrative" else None,
        "micro": micro,
        "micro_zh": micro_zh,
        "target": target,
        "situation": situation,
        "hint": hint,
        "zh": zh,
        "min_words": 5,
        "max_words": 24 if pack == "narrative" else 18,
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
    p.add_argument("--out-dir", default=str(ROOT / "data" / "pilot" / "sentences"))
    p.add_argument("--reference-dir", default=str(ROOT / "data" / "sentences_polished"))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verify-dir", help="check pattern compliance for a directory of records")
    p.add_argument("--finalize", action="store_true", help="merge polished output, reverting lost patterns")
    p.add_argument("--raw-dir", default=str(ROOT / "data" / "pilot" / "sentences"))
    p.add_argument("--polished-dir", default=str(ROOT / "data" / "pilot" / "polished"))
    p.add_argument("--final-dir", default=str(ROOT / "data" / "pilot" / "final"))
    return p.parse_args()


def expand(text):
    t = text.lower().replace("’", "'")
    t = re.sub(r"\b(he|she|it)'s(?=\s+going to\b)", r"\1 is", t)
    t = re.sub(r"\b(i|you|we|they)'ve\b", r"\1 have", t)
    t = re.sub(r"\b(he|she|it)'s\b", r"\1 has", t)
    t = re.sub(r"\b(i|you|he|she|it|we|they)'ll\b", r"\1 will", t)
    t = re.sub(r"\bi'm\b", "i am", t)
    t = re.sub(r"\b(you|we|they)'re\b", r"\1 are", t)
    t = re.sub(r"\b(he|she|it|i|you|we|they)'d\b", r"\1 would", t)
    return t


def passes_pattern(pattern, en):
    t = en.lower().replace("’", "'")
    n = expand(t)
    if pattern == "past_simple":
        return bool(PAST_RE.search(n)) and bool(TIME_RE.search(n))
    if pattern == "past_continuous":
        return bool(re.search(r"\b(was|were)\s+\w+ing\b", n)) and bool(re.search(r"\b(when|while)\b", n))
    if pattern == "present_perfect":
        return bool(re.search(
            r"\b(have|has)\s+(never\s+|ever\s+|already\s+|just\s+|recently\s+|only\s+)?"
            r"(been|got|gotten|done|seen|made|taken|gone|eaten|paid|lost|found|left|finished|"
            r"arrived|booked|ordered|changed|moved|worked|lived|known|had|sent|broken|forgotten|"
            r"received|completed|visited|tried|studied|learned|learnt|kept|written|read)\b", n))
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
        return bool(re.search(r"\b(must|mustn't|have to|has to|had to|should|shouldn't|allowed to)\b", n))
    if pattern == "comparatives":
        return bool(re.search(
            r"\b(\w+er|more|less)\s+than\b|\bas\s+\w+\s+as\b|\bthe\s+\w+est\b|\bbetter\b|\bworse\b", n))
    if pattern == "tag_questions":
        return bool(re.search(
            r",\s*(right|isn't it|aren't they|aren't you|don't you|doesn't it|didn't you|"
            r"can't you|won't you|okay)\b", n))
    if pattern == "relative_clauses":
        return bool(re.search(r"\b(who|which|where|whose)\b", n))
    if pattern == "gerund_infinitive":
        return bool(re.search(
            r"\b(enjoy|like|love|hate|prefer|finish|stop|avoid|mind|suggest|keep|practice|consider)\s+\w+ing\b", n)) \
            and bool(re.search(r"\b(want|need|hope|plan|decide|try|learn|would like)\s+to\s+\w+\b", n))
    if pattern == "passive":
        return bool(re.search(
            r"\b(is|are|was|were|be|been|being)\s+(\w+ed|made|done|given|taken|sent|paid|fixed|"
            r"cleaned|delivered|charged|refunded|updated|included|required|allowed|closed|opened|"
            r"built|written|held|kept|sold|stolen|damaged|lost|broken|locked|checked)\b", n))
    if pattern == "reported_speech":
        return bool(re.search(r"\b(said|told|asked)\b", n))
    if pattern == "narrative_daily_routine":
        return bool(FREQ_RE.search(n)) and bool(re.search(r"\b(first|then|after that)\b", n))
    if pattern == "narrative_last_weekend":
        return bool(PAST_RE.search(n)) and bool(CONNECTOR_RE.search(n))
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
        return bool(PAST_RE.search(n)) and bool(re.search(r"\b(when|while|then|because|but|after)\b", n))
    if pattern == "narrative_movies_books":
        return bool(re.search(r"\b(think|feel|find|thought|felt)\b", n)) \
            and bool(re.search(
                r"\b(better|worse|more|less|as\s+\w+\s+as|interesting|boring|good)\b", n))
    if pattern == "narrative_relationships":
        return bool(re.search(
            r"\b(who|that|have known|has known|have been|has been|met)\b", n))
    if pattern == "narrative_wishes_regrets":
        return bool(re.search(r"\b(wish|if only|should have|regret)\b", n))
    raise ValueError(f"Unknown pattern: {pattern}")


def word_count(text):
    return len(WORD_RE.findall(text))


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


def load_reference(reference_dir):
    rows = []
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
        "phase": 3,
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
    if not passes_pattern(it["pattern"], en):
        return "pattern_miss"
    return None


def generate(args):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    done = existing_uids(out_dir)
    pending = [it for it in ITEMS if make_uid(it["scene"], it["zh"]) not in done]
    ref_rows = load_reference(args.reference_dir)
    pilot_rows = []

    print(f"Pilot items: {len(ITEMS)} | already done: {len(ITEMS) - len(pending)} | pending: {len(pending)}")
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
    index = {(it["scene"], it["zh"]): it for it in ITEMS}
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
    index = {(it["scene"], it["zh"]): it for it in ITEMS}
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
