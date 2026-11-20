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

PHRASAL_FORMS = {
    "phrasal_ask_for": (("ask", "asks", "asked", "asking"), "for"),
    "phrasal_back_up": (("back", "backs", "backed", "backing"), "up"),
    "phrasal_break_up": (("break", "breaks", "broke", "broken", "breaking"), "up"),
    "phrasal_bring_up": (("bring", "brings", "brought", "bringing"), "up"),
    "phrasal_call_back": (("call", "calls", "called", "calling"), "back"),
    "phrasal_call_off": (("call", "calls", "called", "calling"), "off"),
    "phrasal_carry_on": (("carry", "carries", "carried", "carrying"), "on"),
    "phrasal_check_in": (("check", "checks", "checked", "checking"), "in"),
    "phrasal_come_across": (("come", "comes", "came", "coming"), "across"),
    "phrasal_come_over": (("come", "comes", "came", "coming"), "over"),
    "phrasal_come_up_with": (("come", "comes", "came", "coming"), "up with"),
    "phrasal_cut_down": (("cut", "cuts", "cutting"), "down"),
    "phrasal_deal_with": (("deal", "deals", "dealt", "dealing"), "with"),
    "phrasal_eat_out": (("eat", "eats", "ate", "eaten", "eating"), "out"),
    "phrasal_get_along": (("get", "gets", "got", "gotten", "getting"), "along"),
    "phrasal_get_away": (("get", "gets", "got", "gotten", "getting"), "away"),
    "phrasal_get_in": (("get", "gets", "got", "gotten", "getting"), "in"),
    "phrasal_get_off": (("get", "gets", "got", "gotten", "getting"), "off"),
    "phrasal_get_on": (("get", "gets", "got", "gotten", "getting"), "on"),
    "phrasal_get_over": (("get", "gets", "got", "gotten", "getting"), "over"),
    "phrasal_get_through": (("get", "gets", "got", "gotten", "getting"), "through"),
    "phrasal_give_up": (("give", "gives", "gave", "given", "giving"), "up"),
    "phrasal_go_ahead": (("go", "goes", "went", "gone", "going"), "ahead"),
    "phrasal_go_over": (("go", "goes", "went", "gone", "going"), "over"),
    "phrasal_grow_up": (("grow", "grows", "grew", "grown", "growing"), "up"),
    "phrasal_hold_on": (("hold", "holds", "held", "holding"), "on"),
    "phrasal_keep_up": (("keep", "keeps", "kept", "keeping"), "up"),
    "phrasal_let_down": (("let", "lets", "letting"), "down"),
    "phrasal_look_after": (("look", "looks", "looked", "looking"), "after"),
    "phrasal_look_forward_to": (("look", "looks", "looked", "looking"), "forward to"),
    "phrasal_look_into": (("look", "looks", "looked", "looking"), "into"),
    "phrasal_look_out": (("look", "looks", "looked", "looking"), "out"),
    "phrasal_make_up": (("make", "makes", "made", "making"), "up"),
    "phrasal_pay_back": (("pay", "pays", "paid", "paying"), "back"),
    "phrasal_point_out": (("point", "points", "pointed", "pointing"), "out"),
    "phrasal_put_away": (("put", "puts", "putting"), "away"),
    "phrasal_put_off": (("put", "puts", "putting"), "off"),
    "phrasal_put_up_with": (("put", "puts", "putting"), "up with"),
    "phrasal_run_into": (("run", "runs", "ran", "running"), "into"),
    "phrasal_take_out": (("take", "takes", "took", "taken", "taking"), "out"),
    "phrasal_throw_away": (("throw", "throws", "threw", "thrown", "throwing"), "away"),
    "phrasal_turn_down": (("turn", "turns", "turned", "turning"), "down"),
    "phrasal_turn_up": (("turn", "turns", "turned", "turning"), "up"),
    "phrasal_wear_out": (("wear", "wears", "wore", "worn", "wearing"), "out"),
    "phrasal_write_down": (("write", "writes", "wrote", "written", "writing"), "down"),
}

for _name, (_forms, _particle) in PHRASAL_FORMS.items():
    _pt = _particle.replace(" ", r"\s+")
    if _particle == "in":
        _pt = r"in(?:to)?"
    PHRASAL_EN[_name] = re.compile(
        r"\b(?:" + "|".join(_forms) + r")\s+(?:\w+\s+){0,2}" + _pt + r"\b",
        re.I,
    )
del _name, _forms, _particle, _pt

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

FUNCTIONAL_EN = {
    "func_requests": re.compile(
        r"\b(can|could|would)\s+you\b|\bwould you mind\b|\bdo you mind\b", re.I),
    "func_permission": re.compile(
        r"\b(can|could|may|might)\s+i\b|\bis it (okay|ok|all right|fine) if\b|"
        r"\bam i allowed to\b", re.I),
    "func_suggestions": re.compile(
        r"\b(how about|what about|why don't|why not|maybe we should|we could|you could|"
        r"let's|let us|shall we)\b", re.I),
    "func_complaints": re.compile(
        r"\b(i am afraid|there is a problem|there's a problem|doesn't work|does not work|"
        r"keeps \w+ing|not happy|i am worried|i am concerned)\b|"
        r"\b(this|it|the \w+) (is|are) too\b|"
        r"\btoo (salty|sweet|spicy|cold|hot|expensive|noisy|loud|slow|dirty|small|big|crowded|dark|bright)\b",
        re.I),
    "func_apologies": re.compile(
        r"\b(sorry|apologize|apologise|my fault|excuse me|forgive me)\b", re.I),
    "func_clarification": re.compile(
        r"\b(what do you mean|do you mean|are you saying|just to be clear|to clarify|"
        r"i mean)\b", re.I),
    "func_negotiation": re.compile(
        r"\b(could we|would it be possible|what if|maybe we can|can we|"
        r"is there any way|would that work)\b", re.I),
    "func_opinions": re.compile(
        r"\b(i think|i don't think|i do not think|in my opinion|to me|personally|"
        r"i feel|i believe)\b", re.I),
    "func_agreement": re.compile(
        r"\b(i agree|that's true|that is true|exactly|you're right|you are right|"
        r"good point|i think so too|absolutely|(do|don't) you agree)\b", re.I),
    "func_disagreement": re.compile(
        r"\b(i don't think|i do not think|i'm not sure|i am not sure|i see your point|"
        r"i disagree|that's not quite|not really|i'm afraid not|i am afraid not)\b", re.I),
    "func_refusal": re.compile(
        r"\b(i would rather not|i'd rather not|i am afraid i can not|i'm afraid i can't|"
        r"maybe another time|not this time)\b|"
        r"\bi (can not|can't) (come|go|make it|stay|tonight|today)\b", re.I),
    "func_reassurance": re.compile(
        r"\b(don't worry|do not worry|no worries|it's okay|it is okay|it's fine|it is fine|"
        r"take your time|it happens|that's all right|that is all right)\b", re.I),
    "func_invitations": re.compile(
        r"\b(would you like|do you want)( \w+){0,3} to\b|\bare you free\b|"
        r"\bwhy don't you\b|\bcome join\b|\bhow about joining\b|\bwant to join\b", re.I),
    "func_thanks": re.compile(
        r"\b(thanks|thank you|i (really )?appreciate|you're welcome|you are welcome|no problem|"
        r"my pleasure|don't mention it)\b", re.I),
    "func_offers": re.compile(
        r"\b(can i help|shall i|let me|would you like me to|do you need help|"
        r"i can \w+ (it|that) for you|need a hand|offered to help|needed a hand)\b", re.I),
}

COLLOCATION_EN = {
    "coll_make": re.compile(
        r"\b(make|makes|made|making)\s+(?:\w+\s+){0,3}"
        r"(decision|mistake|call|effort|friends|sure|plan|choice|difference|list|appointment)\b",
        re.I),
    "coll_take": re.compile(
        r"\b(take|takes|took|taken|taking)\s+(?:\w+\s+){0,3}"
        r"(break|look|seat|walk|care|time|rest|shower|bus|train|subway|metro|photo|photos|pictures|turn|turns|chance)\b",
        re.I),
    "coll_have": re.compile(
        r"\b(have|has|had|having)\s+(?:\w+\s+){0,3}"
        r"(look|chat|rest|break|problem|fun|time|dinner|lunch|breakfast|coffee|meeting|appointment)\b",
        re.I),
    "coll_get": re.compile(
        r"\b(get|gets|got|gotten|getting)\s+(?:\w+\s+){0,3}"
        r"(ready|better|lost|chance|dressed|home|started|used to|tired|hungry|angry|permission)\b",
        re.I),
    "coll_keep_pay": re.compile(
        r"\b(keep|keeps|kept|keeping)\s+(?:\w+\s+){0,3}"
        r"(in touch|calm|promise|promises|quiet|going|warm|cool|fit|exercising|practicing)\b|"
        r"\b(pay|pays|paid|paying)\s+(?:\w+\s+){0,3}"
        r"(attention|visit|bill|rent|fine|price|tax)\b", re.I),
    "coll_prepositions": re.compile(
        r"\b(depend on|depends on|depended on|interested in|good at|afraid of|"
        r"wait for|waiting for|waited for|look forward to|looking forward to|"
        r"worried about|proud of|famous for|ready for|different from|similar to)\b", re.I),
    "coll_word_family_decide": re.compile(
        r"\b(decide|decides|decided|deciding|decision|decisions|choose|chooses|chose|"
        r"chosen|choosing|choice|choices|advise|advises|advised|advice|explain|explains|"
        r"explained|explanation)\b", re.I),
    "coll_word_family_success": re.compile(
        r"\b(succeed|succeeds|succeeded|success|successful|successfully|improve|improves|"
        r"improved|improvement|develop|develops|developed|developing|development|grow|grows|growing|grew|grown|growth|"
        r"breakthrough|breakthroughs)\b",
        re.I),
    "coll_frequency": re.compile(
        r"\b(always|usually|often|sometimes|occasionally|rarely|seldom|never|ever|once|every day|every week|"
        r"once a week|twice a week)\b", re.I),
    "coll_time_money": re.compile(
        r"\b(on time|in time|in advance)\b|"
        r"\b(afford|affords|afforded)\b|"
        r"\b(spend|spends|spent|spending|waste|wastes|wasted|wasting|save|saves|saved|saving|"
        r"afford|affords|afforded|cost|costs|take|takes|took|taking)\b[^.;]{0,30}"
        r"\b(time|money|hours|minutes)\b|"
        r"\b(time|money)\b[^.;]{0,30}\b(spend|waste|save|cost|afford)\w*\b", re.I),
    "word_pairs_say_tell": re.compile(
        r"\b(say|says|said|saying|tell|tells|told|telling)\b", re.I),
    "word_pairs_speak_talk": re.compile(
        r"\b(speak|speaks|spoke|spoken|speaking|talk|talks|talked|talking)\b", re.I),
    "word_pairs_borrow_lend": re.compile(
        r"\b(borrow|borrows|borrowed|borrowing|lend|lends|lent|lending)\b", re.I),
    "word_pairs_bring_take": re.compile(
        r"\b(bring|brings|brought|bringing|take|takes|took|taken|taking)\b", re.I),
    "word_pairs_learn_study_teach": re.compile(
        r"\b(learn|learns|learned|learnt|learning|study|studies|studied|studying|"
        r"teach|teaches|taught|teaching)\b", re.I),
    "word_pairs_see_look_watch": re.compile(
        r"\b(see|sees|saw|seen|seeing|look|looks|looked|looking|"
        r"watch|watches|watched|watching)\b", re.I),
    "word_pairs_hear_listen": re.compile(
        r"\b(hear|hears|heard|hearing|listen|listens|listened|listening)\b", re.I),
    "word_pairs_hope_wish": re.compile(
        r"\b(hope|hopes|hoped|hoping|wish|wishes|wished|wishing)\b", re.I),
    "word_pairs_remember_remind": re.compile(
        r"\b(remember|remembers|remembered|remembering|remind|reminds|reminded|reminding)\b", re.I),
    "word_pairs_win_earn": re.compile(
        r"\b(win|wins|won|winning|earn|earns|earned|earning|"
        r"beat|beats|beaten|beating)\b", re.I),
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
    t = re.sub(r"\b(he|she|it)'s(?=\s+\w+ing\b)", r"\1 is", t)
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
    if pattern in FUNCTIONAL_EN:
        return bool(FUNCTIONAL_EN[pattern].search(t) or FUNCTIONAL_EN[pattern].search(n))
    if pattern in COLLOCATION_EN:
        return bool(COLLOCATION_EN[pattern].search(t) or COLLOCATION_EN[pattern].search(n))
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
    if pattern == "present_continuous":
        return bool(re.search(
            r"\b(am|is|are)\s+(?:(?:not|still|just|now)\s+)?(?:\w+ing|busy\s+\w+ing)\b", n)) \
            and not re.search(r"\bgoing to\b", n)
    if pattern == "past_perfect":
        return bool(re.search(
            r"\bhad\s+(?:already\s+|just\s+|never\s+|not\s+|only\s+|recently\s+)?"
            r"(left|arrived|finished|started|seen|met|gone|been|done|eaten|paid|lost|found|"
            r"forgotten|told|said|bought|booked|sent|taken|made|heard|read|written|"
            r"changed|moved|cleaned|closed|opened|stopped|ended|begun|come|known|"
            r"got|gotten|waited|worked|studied|cooked|fixed|returned|sold|"
            r"\w{3,}ed)\b", n)) \
            or bool(re.search(r"\bhad not\s+\w+\b", n))
    if pattern == "third_conditional":
        return bool(re.search(r"\bif\b", n)) and bool(re.search(r"\bhad\s+\w+", n)) \
            and bool(re.search(r"\bwould(?: not)?\s+have\s+\w+", n))
    if pattern == "quantifiers":
        return bool(re.search(
            r"\b(some|any|many|much|a few|a little|a lot of|lots of|enough|"
            r"too many|too much|a couple of|several|none|plenty of)\b", n))
    if pattern == "prepositions_time":
        return bool(re.search(
            r"\b(in|on|at)\s+(?:the\s+)?(morning|afternoon|evening|night|weekend|"
            r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
            r"january|february|march|april|may|june|july|august|september|october|"
            r"november|december|spring|summer|autumn|fall|winter|noon|midnight|"
            r"weekends|weekdays|weekend|weekday)\b", n)) \
            or bool(re.search(r"\b(at|around)\s+\d{1,2}(?::\d{2})?\b", n))
    if pattern == "question_words":
        return bool(re.match(r"\s*(what|where|when|who|why|how|which|whose)\b", t))
    if pattern == "too_enough":
        return bool(re.search(r"\btoo\s+\w+\b|\b\w+\s+enough\b|\benough\s+\w+\b", n))
    if pattern == "so_such":
        return bool(re.search(
            r"\bso\s+(happy|tired|busy|expensive|cold|hot|kind|funny|good|bad|nice|"
            r"difficult|easy|late|early|fast|slow|loud|quiet|beautiful|delicious|angry|"
            r"nervous|excited|worried|surprised|interesting|boring|far|close|small|big)\b", n)) \
            or bool(re.search(r"\bsuch\s+(a|an)\b", n))
    if pattern == "causative":
        return bool(re.search(
            r"\b(have|has|had|get|gets|got|getting)\s+(?:\w+\s+){0,5}"
            r"(done|fixed|repaired|cleaned|cut|washed|delivered|installed|checked|painted|"
            r"built|made|served|printed|sent|translated|changed|replaced|upgraded)\b", n))
    if pattern == "modals_deduction":
        return bool(re.search(
            r"\b(must be|must have|can not be|could not be|could be|could have|"
            r"might be|might have|may be|should be|must not be)\b", n))
    if pattern == "present_perfect_continuous":
        return bool(re.search(r"\b(have|has)\s+been\s+\w+ing\b", n))
    if pattern == "indirect_questions":
        return bool(re.search(
            r"\b(do you know|did you know|can you tell me|could you tell me|"
            r"i wonder|i was wondering|do you remember|can you remember)\b", n))
    if pattern == "gerund_subject":
        return bool(re.match(
            r"\s*(swimming|reading|cooking|walking|learning|exercising|traveling|"
            r"travelling|saving|driving|running|sleeping|shopping|working|studying|"
            r"listening|speaking|cleaning|gardening|eating|drinking|smoking|jogging|"
            r"cycling|writing|painting|singing|dancing|going|getting)\b", t)) \
            or bool(re.search(
                r"\b(swimming|reading|cooking|walking|learning|exercising|traveling|"
                r"travelling|saving|driving|running|shopping|studying|cleaning)\b"
                r"\s+(is|was|can|helps|makes|takes)\b", n))
    if pattern == "adverbs_manner":
        return bool(re.search(
            r"\b(quickly|carefully|quietly|slowly|loudly|politely|clearly|easily|"
            r"suddenly|immediately|seriously|properly|neatly|safely|gently|firmly|"
            r"honestly|kindly|badly|well|fast|hard|early|late|angrily|happily|calmly)\b", n))
    if pattern == "reflexive_pronouns":
        return bool(re.search(
            r"\b(myself|yourself|himself|herself|itself|ourselves|yourselves|themselves)\b", n))
    if pattern == "hf_core":
        return bool(re.search(
            r"\b(went|came|told|thought|knew|thing|things|job|jobs|most|ever)\b", n))
    if pattern == "roleplay":
        return True
    if pattern == "life_scene":
        return True
    if pattern in (
        "register_casual", "register_neutral", "register_formal",
        "register_workplace", "register_soft",
    ):
        return True
    if pattern == "unless":
        return bool(re.search(r"\bunless\b", n))
    if pattern == "in_case":
        return bool(re.search(r"\bin case\b", n))
    if pattern == "as_as":
        if re.search(r"\b(not|never)\b|n't\b", n):
            return False
        return bool(re.search(
            r"\bas\s+(?!(?:soon|well)\b)(?!(?:far|long|much|many)\s+as\b)(?:[a-z]+\s+){0,4}as\b", n))
    if pattern == "dialogue":
        return bool(re.search(r"(^|\n)\s*a[::]", n)) and bool(re.search(r"(^|\n)\s*b[::]", n))
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
    "func_requests": r"(请|能|能不能|可以|帮我|帮忙|麻烦|好吗|行吗|一下)",
    "func_permission": r"(可以|能不能|能|允许|行吗|好吗|我想问|介意)",
    "func_suggestions": r"(建议|不如|要不|怎么样|咱们|可以试试|试试|要不要|最好)",
    "func_complaints": r"(太|不满|有问题|坏了|不工作|吵|慢|不对|一直|总是|投诉|不满意|漏水|不制冷)",
    "func_apologies": r"(对不起|抱歉|不好意思|是我的错|怪我|道歉)",
    "func_clarification": r"(什么意思|你是说|我的意思是|确认|再说一遍|听不太懂|是指|指的是)",
    "func_negotiation": r"(能不能|可不可以|商量|换个|要不|各让一步|折中|延迟|提前|优惠|分期)",
    "func_opinions": r"(我觉得|我认为|在我看来|个人|感觉|我的看法)",
    "func_agreement": r"(同意|赞同|没错|确实|说得对|我也这么想|有道理|对呀)",
    "func_disagreement": r"(不同意|不觉得|不太同意|不这么认为|不认为|不一定|恐怕不行|保留意见|不太对)",
    "func_refusal": r"(不了|不行|不能|不方便|下次|改天|算了|恐怕|不想|拒绝|婉拒|就不|不去了)",
    "func_reassurance": r"(别担心|别急|没关系|没事|慢慢来|放心|不用担心|会好的|不怪你)",
    "func_invitations": r"(要不要|一起|参加|有空|邀请|愿意|来我家|聚一聚|赏脸)",
    "func_thanks": r"(谢谢|感谢|多谢|不客气|不用谢|应该的|帮了大忙)",
    "func_offers": r"(我帮你|需要|要我|让我|帮你|需不需要|我来|帮忙吗|搭把手)",
    "coll_make": r"(做|决定|犯.{0,4}错|打.{0,2}电话|努力|交.{0,3}朋友|确保|确认|安排|预约|清单|区别|计划|选择|选)",
    "coll_take": r"(休息|看一下|坐|散步|照顾|花.{0,4}时间|洗.{0,2}澡|坐车|拍.{0,3}照片|轮流|轮到|机会)",
    "coll_have": r"(看一看|看一下|聊天|休息|问题|玩得|时间|吃晚饭|咖啡|会议|预约)",
    "coll_get": r"(准备|好转|迷路|机会|穿好|到家|习惯|累|饿|生气|许可)",
    "coll_keep_pay": r"(保持联系|冷静|守信|安静|坚持|保温|注意|听讲|看望|付账|付钱|房租|罚单|罚款)",
    "coll_prepositions": r"(取决于|依靠|对.{0,6}感兴趣|擅长|害怕|等|期待|担心|骄傲|有名|闻名|准备好|做.{0,3}准备|不同于|相似)",
    "coll_word_family_decide": r"(决定|选择|建议|解释|选|劝|说明)",
    "coll_word_family_success": r"(成功|进步|提高|发展|成长|长得|长大|改善|失败|突破)",
    "coll_frequency": r"(总是|经常|通常|有时|偶尔|从不|从来不|从没|很少|每天|每周|一次|两次|曾经)",
    "coll_time_money": r"(按时|准时|及时|提前|花.{0,4}(时间|钱|小时|分钟)|浪费时间|时间.{0,3}浪费|省钱|花钱|省.{0,3}钱|存.{0,2}钱|负担|价格|费用|赶时间|买不起)",
    "present_continuous": r"(正在|正|在).{0,10}(呢|着|做|看|等|听|吃|写|打|修|开会|忙|下|刮|找|跑|接|哭|玩|洗|用|学|说)|现在.{0,12}(在|正)",
    "past_perfect": r"(已经|早就|之前|那时|等到|发现|才想起|才想到).{0,26}(了|过)|到.{0,12}的时候",
    "third_conditional": r"(如果|要是).{0,34}(就|早就).{0,14}(会|不会|能|就)",
    "quantifiers": r"(一些|一点|一点儿|很多|许多|不少|几个|够|太多|太少|没什么|有些|大量|多少)",
    "prepositions_time": r"(在|到|从).{0,8}(早上|上午|中午|下午|晚上|夜里|周末|星期|周一|周二|周三|周四|周五|周六|周日|春天|夏天|秋天|冬天|半夜)|(在|到|从).{0,8}[一二三四五六七八九十0-9]{1,2}月|(周一|周二|周三|周四|周五|周六|周日|周末|春天|夏天|秋天|冬天).{0,12}(见面|开会|出发|回来|去|很)|(早上|下午|晚上).{0,12}(去|见面|开会|出发|回来)",
    "question_words": r"(什么|哪里|哪儿|谁|为什么|怎么|几点|哪个|哪些|多少|多久|多远|什么时候)",
    "too_enough": r"(太.{0,8}了|不够|够.{0,3}(了|吗)|太.{0,8}(不能|没法|拿不动|做不完|吃不下))",
    "so_such": r"(这么|那么|如此|真是.{0,12}了)",
    "causative": r"(让人|请人|找人|叫.{0,8}(修|洗|剪|装|做|送|打扫)|让.{0,8}(修|洗|剪|装|做|送|打扫)|送去|拿去.{0,5}(修|洗)|让人.{0,6}(送|修|做|装))",
    "modals_deduction": r"(一定|肯定|可能|也许|应该|不可能|不会|说不定|想必)",
    "present_perfect_continuous": r"(一直|最近|这些天|这几年|很久|已经).{0,24}(学|等|做|工作|住|锻炼|找|忙|加班|下雨|准备|哭|睡|写|开会|装修)|(学|等|做|工作|住|锻炼|哭).{0,12}了.{0,6}(年|个月|天|小时)",
    "indirect_questions": r"(你知道|知不知道|能不能告诉我|可不可以告诉我|我想知道|我想问|请问|帮我问问)",
    "gerund_subject": r"^(学|跑|走|游泳|做饭|读书|阅读|开车|旅行|存钱|锻炼|早睡|早起|听音乐|打扫|画画|唱歌|跳舞|养花|喝茶|熬夜|运动)",
    "adverbs_manner": r"(认真地|仔细地|慢慢地|轻轻地|安静地|大声地|清楚地|礼貌地|顺利地|安全地|紧紧地|开心地|生气地|很快|很慢|很仔细|很认真|得很好|得很快|得很早|得很晚|说得好|做得好)",
    "reflexive_pronouns": r"(我自己|你自己|他自己|她自己|它自己|我们自己|你们自己|他们自己|自己)",
    "word_pairs_say_tell": r"(说|告诉|讲|跟.{0,6}说|对.{0,6}说|说不出|说实话|说清楚)",
    "word_pairs_speak_talk": r"(说英语|会说|说话|讲话|聊天|聊|谈|讨论|演讲|发言|小声|大声|流利|说得)",
    "word_pairs_borrow_lend": r"(借|借给|借出|借来|向.{0,6}借)",
    "word_pairs_bring_take": r"(带|带来|带去|拿去|带回|带走|拿走|拿给|拿出去|拿到|带孩子|带朋友)",
    "word_pairs_learn_study_teach": r"(学|学习|学会|教|自学|上课|复习)",
    "word_pairs_see_look_watch": r"(看见|看到|看|观看|盯着|望|瞧)",
    "word_pairs_hear_listen": r"(听见|听到|听|倾听|听不清)",
    "word_pairs_hope_wish": r"(希望|但愿|要是.{0,20}就好了|盼着|期望)",
    "word_pairs_remember_remind": r"(记得|记住|想起|想起来|想不起来|记不起来|提醒|忘了|忘记)",
    "word_pairs_win_earn": r"(赢|赢得|挣|赚|打败|获胜|拿第一)",
    "roleplay": r"[\u4e00-\u9fff]",
    "dialogue": r"A[:：][\s\S]{2,60}B[:：]",
}


def passes_zh(pattern, zh):
    rx = ZH_CHECKS.get(pattern)
    if not rx:
        raise ValueError(f"Unknown pattern: {pattern}")
    return bool(re.search(rx, zh))


MAX_WORDS = {
    "grammar": 18, "narrative": 24, "phrasal": 18, "discourse": 20,
    "functional": 20, "collocation": 18, "roleplay": 20, "dialogue": 70,
    "hf": 16, "life": 20, "register": 24,
}
MIN_WORDS = 4


def word_count(text):
    return len(WORD_RE.findall(text))


PHRASAL_ZH = {
    "phrasal_ask_for": r"(请求|要求|跟.{0,4}要|找.{0,4}要|申请|开口)",
    "phrasal_back_up": r"(备份|支持|撑腰|备用)",
    "phrasal_break_up": r"(分手|散伙|拆开|分开)",
    "phrasal_bring_up": r"(提起|提到|说起|养大|抚养|提出)",
    "phrasal_call_back": r"(回电话|打回去|回个电话|再打)",
    "phrasal_call_off": r"(取消|叫停|不办)",
    "phrasal_carry_on": r"(继续|接着|坚持下去)",
    "phrasal_check_in": r"(入住|登记|值机|办手续)",
    "phrasal_come_across": r"(偶然|碰到|遇到|无意中)",
    "phrasal_come_over": r"(过来|来我|来一趟|来坐)",
    "phrasal_come_up_with": r"(想出|想到|提出|想到一个)",
    "phrasal_cut_down": r"(减少|少吃|少喝|削减|降低)",
    "phrasal_deal_with": r"(处理|应付|解决|面对)",
    "phrasal_eat_out": r"(出去吃|下馆子|在外面吃)",
    "phrasal_get_along": r"(相处|合得来|处得|关系)",
    "phrasal_get_away": r"(离开|脱身|抽身|走开)",
    "phrasal_get_in": r"(进.{0,3}屋|进.{0,3}门|上车|进.{0,3}站|进.{0,3}去)",
    "phrasal_get_off": r"(下车|下飞机|下班|下公交)",
    "phrasal_get_on": r"(上车|上飞机|上.{0,4}公交|上.{0,4}地铁)",
    "phrasal_get_over": r"(克服|恢复|走出来|缓过来)",
    "phrasal_get_through": r"(接通|打通|通过|办完|度过)",
    "phrasal_give_up": r"(放弃|戒掉|不干了|别想)",
    "phrasal_go_ahead": r"(先走|继续|开始|往前|你先)",
    "phrasal_go_over": r"(复习|过一遍|检查一遍|核对)",
    "phrasal_grow_up": r"(长大|成长|小时候)",
    "phrasal_hold_on": r"(等一下|稍等|别挂|等等)",
    "phrasal_keep_up": r"(跟上|保持|跟得上|不落后)",
    "phrasal_let_down": r"(失望|辜负)",
    "phrasal_look_after": r"(照顾|照看|看着|帮你管)",
    "phrasal_look_forward_to": r"(期待|盼望|等不及|盼着)",
    "phrasal_look_into": r"(调查|查一下|了解|研究)",
    "phrasal_look_out": r"(小心|当心|注意|留神)",
    "phrasal_make_up": r"(编造|编个|瞎说|和好|凑)",
    "phrasal_pay_back": r"(还钱|还给你|还清|报销|回报)",
    "phrasal_point_out": r"(指出|提醒|说明|指出来)",
    "phrasal_put_away": r"(收起来|放好|收好|归位)",
    "phrasal_put_off": r"(推迟|延期|拖到|往后推)",
    "phrasal_put_up_with": r"(忍受|容忍|受不了|将就)",
    "phrasal_run_into": r"(碰到|遇到|撞见|偶遇)",
    "phrasal_take_out": r"(拿出来|带出去|取出|掏出|外卖)",
    "phrasal_throw_away": r"(扔掉|丢掉|扔了|丢弃)",
    "phrasal_turn_down": r"(拒绝|调小|关小|降低)",
    "phrasal_turn_up": r"(出现|调大|开大|露面|到场)",
    "phrasal_wear_out": r"(磨破|穿坏|累坏|磨损)",
    "phrasal_write_down": r"(写下|记下|记下来|写下来)",
    "hf_core": r"[\u4e00-\u9fff]",
    "life_scene": r"[\u4e00-\u9fff]",
    "register_casual": r"[\u4e00-\u9fff]",
    "register_neutral": r"[\u4e00-\u9fff]",
    "register_formal": r"[\u4e00-\u9fff]",
    "register_workplace": r"[\u4e00-\u9fff]",
    "register_soft": r"[\u4e00-\u9fff]",
    "unless": r"(除非|否则|要不然|不然)",
    "in_case": r"(以防|万一|免得|提前|备用|带上|准备)",
    "as_as": r"(一样|那么|像.{0,8}一样)",
}
ZH_CHECKS.update(PHRASAL_ZH)

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
    "comparatives": "comparative adjective/adverb, with than for an explicit comparison, or (not) as ... as",
    "tag_questions": "statement + comma + an appropriately positive or negative question tag",
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
    "narrative_wishes_regrets": "wish / if only / should have / regret (wishes or regrets about the past)",
    "phrasal_get_up": "wake up or get up (phrasal verb)",
    "phrasal_put_on": "put on or take off (clothes or shoes)",
    "phrasal_pick_up": "pick up or drop off (a person or thing)",
    "phrasal_turn_on_off": "turn on or turn off (a device or light)",
    "phrasal_look_for": "look for or find out",
    "phrasal_figure_out": "figure out (work out an answer or reason)",
    "phrasal_go_back": "come back or go back",
    "phrasal_go_out": "go out or hang out",
    "phrasal_work_out": "work out (exercise or solve)",
    "phrasal_run_out": "run out (of something)",
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
    "func_requests": "Could you / Can you / Would you mind (a polite request)",
    "func_permission": "Can I / Could I / May I / Is it okay if I (asking permission)",
    "func_suggestions": "How about / Why don't we / We could / Maybe we should",
    "func_complaints": "I'm afraid ... / This is too ... / It keeps ... (a complaint)",
    "func_apologies": "Sorry / I apologize / It was my fault",
    "func_clarification": "What do you mean / Do you mean / Just to be clear",
    "func_negotiation": "Could we / Would it be possible / What if",
    "func_opinions": "I think / In my opinion / To me / Personally",
    "func_agreement": "I agree / Exactly / That's true / You're right",
    "func_disagreement": "I don't think / I'm not sure / I see your point, but",
    "func_refusal": "I'd rather not / I'm afraid I can't / Maybe another time",
    "func_reassurance": "Don't worry / It's okay / Take your time / No worries",
    "func_invitations": "Would you like to / Do you want to / Are you free",
    "func_thanks": "Thanks / I appreciate it / You're welcome / My pleasure",
    "func_offers": "Can I help / Shall I / Let me / Would you like me to",
    "coll_make": "make collocation (make a decision, make a mistake, make sure, make a call, make a plan, make a list)",
    "coll_take": "take + noun (take a break, take a look, take care, take time, take a seat, take turns, take the subway, take photos)",
    "coll_have": "have + noun (have a look, have a chat, have fun, have time, have a rest, have dinner, have coffee, have a meeting)",
    "coll_get": "get collocation (get ready, get better, get lost, get a chance, get tired, get hungry, get used to, get permission)",
    "coll_keep_pay": "keep (keep in touch / keep calm / keep a promise / keep quiet) or pay (pay attention / pay the bill / pay rent / pay a fine / pay a visit)",
    "coll_prepositions": "verb/adjective + preposition (depend on, interested in, good at, afraid of, wait for, look forward to)",
    "coll_word_family_decide": "decide/decision, choose/choice, advise/advice, explain/explanation",
    "coll_word_family_success": "succeed/success/successful, improve/improvement, develop/development, grow/growth",
    "coll_frequency": "a frequency adverb (always, usually, often, sometimes, rarely, never)",
    "coll_time_money": "time or money collocation (on time, in time, in advance, spend/waste/save time, spend/save money, afford, cost)",
    "present_continuous": "am/is/are + verb-ing (an action happening now)",
    "past_perfect": "had + past participle (an action before another past action)",
    "third_conditional": "if + had + past participle, would have + past participle",
    "quantifiers": "a quantifier such as some, any, many, much, a few, a little, enough",
    "prepositions_time": "in/on/at + a time expression (at 7, on Monday, in the morning)",
    "question_words": "a wh-question starting with what, where, when, who, why, how, or which",
    "too_enough": "too + adjective/adverb, adjective/adverb + enough, or enough + noun",
    "so_such": "so + adjective, or such a + noun",
    "causative": "have/get + object + past participle (have it fixed, get my hair cut)",
    "modals_deduction": "present or past deduction: e.g. must/might/could be, can't be, must/might/could have + past participle",
    "present_perfect_continuous": "have/has been + verb-ing",
    "indirect_questions": "Do you know ...? / Could you tell me ...? / I wonder ...",
    "gerund_subject": "an -ing verb as the subject (Swimming is good for you)",
    "adverbs_manner": "an adverb of manner (quickly, carefully, politely, well)",
    "reflexive_pronouns": "a reflexive pronoun (myself, yourself, himself, ourselves)",
    "word_pairs_say_tell": "say (say something) or tell (tell someone something)",
    "word_pairs_speak_talk": "speak (a language / formally) or talk (talk to someone)",
    "word_pairs_borrow_lend": "borrow (take and return) or lend (give for a while)",
    "word_pairs_bring_take": "bring (toward the speaker) or take (away from the speaker)",
    "word_pairs_learn_study_teach": "learn (gain knowledge), study (work at it), or teach (help someone learn)",
    "word_pairs_see_look_watch": "see (notice), look (direct your eyes), or watch (view for a while)",
    "word_pairs_hear_listen": "hear (receive sound) or listen (pay attention to sound)",
    "word_pairs_hope_wish": "hope + present/future, or wish + past (an unreal wish)",
    "word_pairs_remember_remind": "remember (keep in mind) or remind (help someone remember)",
    "word_pairs_win_earn": "win (a game or prize), earn (money), or beat (an opponent)",
    "roleplay": "the service worker's direct reply to the customer, with you/your or an offer to help",
    "dialogue": "both turns of the exchange, kept on two lines as A: ... and B: ...",
}

# Chinese phrasing the planner must use for the newest packs, so the English
# translation can keep the exact target structure.
ZH_HINTS = {
    "func_requests": "请你……好吗 / 你能……吗 / 你方便……吗 / 你介意……吗",
    "func_permission": "我可以……吗 / 能不能…… / 我能不能……",
    "func_suggestions": "要不…… / 不如…… / 我们……怎么样 / 可以试试",
    "func_complaints": "太……了 / 一直…… / 有点问题（语气礼貌）",
    "func_apologies": "对不起 / 抱歉 / 不好意思 / 是我的错",
    "func_clarification": "你是说……吗 / 我的意思是…… / 确认一下",
    "func_negotiation": "能不能…… / 可不可以…… / 要不我们…… / 各让一步",
    "func_opinions": "我觉得…… / 我认为…… / 在我看来……",
    "func_agreement": "我同意 / 你说得对 / 确实 / 没错",
    "func_disagreement": "我不这么认为 / 我不同意 / 我觉得不太对",
    "func_refusal": "这次我就不去了 / 恐怕不行 / 下次吧",
    "func_reassurance": "别担心 / 没关系 / 慢慢来 / 没事",
    "func_invitations": "你要不要…… / 一起来……吧 / 有空吗",
    "func_thanks": "谢谢你 / 感谢 / 不客气 / 不用谢",
    "func_offers": "我来帮你…… / 需要我……吗 / 要不要我……",
    "coll_make": "做决定、犯错、打电话、确认、交朋友",
    "coll_take": "休息、看一下、照顾、花时间",
    "coll_have": "看一看、聊天、玩得开心、有时间",
    "coll_get": "准备好、好转、迷路、得到机会",
    "coll_keep_pay": "保持联系、冷静、注意、付账",
    "coll_prepositions": "取决于、对……感兴趣、擅长、害怕、等、期待、担心、为……骄傲",
    "coll_word_family_decide": "决定、选择、建议、解释",
    "coll_word_family_success": "成功、进步、改善、发展、成长",
    "coll_frequency": "总是、通常、经常、有时、很少、从不",
    "coll_time_money": "准时、及时、花时间、浪费时间、存钱、买得起",
    "present_continuous": "现在正在…… / 正在……呢 / 这会儿在……",
    "past_perfect": "到……的时候，已经……了 / 早就……了 / 才发现……",
    "third_conditional": "如果当时……，就……了 / 要是……，早就……",
    "quantifiers": "一些、一点儿、很多、几个、够、太多、太少",
    "prepositions_time": "在……点 / 在星期…… / 在……月 / 在早上、下午、晚上",
    "question_words": "什么、哪里、谁、为什么、怎么、几点、哪个",
    "too_enough": "太……了 / ……不够 / 够……了",
    "so_such": "这么…… / 那么…… / 真是……",
    "causative": "让人…… / 找人…… / 叫……修 / 送去……",
    "modals_deduction": "一定…… / 可能…… / 不可能…… / 应该……",
    "present_perfect_continuous": "一直在…… / 最近一直…… / 已经……多久了",
    "indirect_questions": "你知道……吗 / 能不能告诉我…… / 请问……",
    "gerund_subject": "学…… / 跑步…… / 早睡……（用动词短语作主语）",
    "adverbs_manner": "认真地、仔细地、慢慢地、大声地、很好地",
    "reflexive_pronouns": "我自己、你自己、他自己、我们自己、自己",
    "word_pairs_say_tell": "说…… / 告诉某人…… / 跟我说…… / 说实话",
    "word_pairs_speak_talk": "说英语 / 说话 / 聊天 / 跟某人谈一谈",
    "word_pairs_borrow_lend": "向某人借…… / 借给某人…… / 借我……",
    "word_pairs_bring_take": "带来 / 带去 / 拿去 / 带孩子去…… / 带……回家",
    "word_pairs_learn_study_teach": "学…… / 学习…… / 教…… / 自学",
    "word_pairs_see_look_watch": "看见 / 看一下 / 看电视 / 看比赛",
    "word_pairs_hear_listen": "听见 / 听音乐 / 听我说 / 听不清",
    "word_pairs_hope_wish": "希望…… / 但愿…… / 要是……就好了",
    "word_pairs_remember_remind": "记得…… / 提醒我…… / 想起来……",
    "word_pairs_win_earn": "赢了…… / 赢得…… / 挣……钱 / 赚…… / 打败……",
}


# Ten concrete everyday angles per pattern. The planner writes two sentences per angle.
LABELS.update({
    "phrasal_ask_for": "ask for",
    "phrasal_back_up": "back up",
    "phrasal_break_up": "break up",
    "phrasal_bring_up": "bring up",
    "phrasal_call_back": "call back",
    "phrasal_call_off": "call off",
    "phrasal_carry_on": "carry on",
    "phrasal_check_in": "check in",
    "phrasal_come_across": "come across",
    "phrasal_come_over": "come over",
    "phrasal_come_up_with": "come up with",
    "phrasal_cut_down": "cut down",
    "phrasal_deal_with": "deal with",
    "phrasal_eat_out": "eat out",
    "phrasal_get_along": "get along",
    "phrasal_get_away": "get away",
    "phrasal_get_in": "get in",
    "phrasal_get_off": "get off",
    "phrasal_get_on": "get on",
    "phrasal_get_over": "get over",
    "phrasal_get_through": "get through",
    "phrasal_give_up": "give up",
    "phrasal_go_ahead": "go ahead",
    "phrasal_go_over": "go over",
    "phrasal_grow_up": "grow up",
    "phrasal_hold_on": "hold on",
    "phrasal_keep_up": "keep up",
    "phrasal_let_down": "let down",
    "phrasal_look_after": "look after",
    "phrasal_look_forward_to": "look forward to",
    "phrasal_look_into": "look into",
    "phrasal_look_out": "look out",
    "phrasal_make_up": "make up",
    "phrasal_pay_back": "pay back",
    "phrasal_point_out": "point out",
    "phrasal_put_away": "put away",
    "phrasal_put_off": "put off",
    "phrasal_put_up_with": "put up with",
    "phrasal_run_into": "run into",
    "phrasal_take_out": "take out",
    "phrasal_throw_away": "throw away",
    "phrasal_turn_down": "turn down",
    "phrasal_turn_up": "turn up",
    "phrasal_wear_out": "wear out",
    "phrasal_write_down": "write down",
    "hf_core": "went/came/told/thought/knew or thing/job/most/ever",
    "life_scene": "one natural everyday spoken sentence for this scene",
    "register_casual": "a relaxed, casual English sentence for friends or family",
    "register_neutral": "a standard polite English sentence for everyday situations",
    "register_formal": "a formal, polite English sentence for an email or official situation",
    "register_workplace": "a professional, polite English sentence for work",
    "register_soft": "a soft, indirect English sentence that sounds polite",
    "unless": "unless + a condition clause",
    "in_case": "in case + a precaution",
    "as_as": "as + adjective + as (positive comparison)",
})

ANGLES = {
    "life_scene": [
        "描述最近一次遇到的情况", "向对方提出一个具体请求", "说明原因或结果",
        "询问细节或价格", "表达担心或不满", "给出建议或提醒",
        "回忆以前的一次经历", "说明自己的计划", "解释一个问题", "确认信息和安排",
    ],
    "register_casual": [
        "约朋友一起吃饭", "请朋友顺手帮个小忙", "跟朋友吐槽今天的事", "跟家人商量周末安排",
        "问朋友借一样东西", "跟朋友说改时间", "跟室友说家里缺什么", "跟朋友分享好消息",
        "拒绝朋友的邀请", "出门前跟家人打招呼",
    ],
    "register_neutral": [
        "向同事借办公用品", "请邻居帮忙收快递", "请店员换一件", "向前台询问流程",
        "请同事改一下时间", "向陌生人问路", "请路人帮忙拍照", "跟老师确认作业要求",
        "跟房东说家里的小问题", "跟同事换班",
    ],
    "register_formal": [
        "写邮件确认预约", "写信申请退款", "向银行说明账户问题", "向公司申请证明",
        "正式投诉服务问题", "邮件里请求延长期限", "回复邮件表示感谢", "书面确认合同细节",
        "向学校申请补考", "正式邀请对方参加会议",
    ],
    "register_workplace": [
        "会上提出不同意见", "向领导汇报进度", "请同事看文件", "向客户确认需求",
        "在群里说明延期", "跟同事协调分工", "向上级请假", "委婉拒绝额外工作",
        "确认下一次会议时间", "给新同事介绍流程",
    ],
    "register_soft": [
        "委婉表达不同意见", "委婉拒绝请求", "委婉指出小错误", "委婉表达担心",
        "委婉提出改进建议", "委婉表达不满", "委婉打断对方", "委婉纠正自己的说法",
        "委婉请求宽限时间", "委婉结束谈话",
    ],
    "unless": [
        "说明参加活动的条件", "提醒不早出发会迟到", "解释规则例外", "劝对方现在就打电话",
        "说明退款的条件", "商量取消的时间限制", "提醒带证件才能进门", "说明下雨就改期",
        "讲清请假要提前说", "说明见面的前提",
    ],
    "in_case": [
        "提醒对方带伞", "出门前检查钥匙", "提前留出堵车时间", "备份重要文件",
        "准备备用方案", "提醒对方存电话号码", "带一点常用药", "出门前给手机充电",
        "把地址提前记下来", "出发前查天气",
    ],
    "as_as": [
        "比较两个人的身高", "比较两个地方的距离", "比较两样东西的价格", "说两个人跑得一样快",
        "说今天和昨天一样冷", "说两种食物一样好吃", "说两件事一样重要", "说两个人一样忙",
        "说两道题一样简单", "说两个价钱一样便宜",
    ],
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
    "func_requests": [
        "请同事帮忙打印文件", "请朋友顺路带杯咖啡", "请服务员拿餐具",
        "请邻居帮忙收快递", "请室友把音乐调小", "请路人帮忙拍照",
        "请同事把会议时间发过来", "请前台多给一条毛巾", "请朋友等你十分钟",
        "请店员换一个尺码",
    ],
    "func_permission": [
        "问能不能提前下班", "问能不能在会议室吃东西", "问能不能借充电器",
        "问能否带朋友来聚会", "问能不能把车停在门口", "问老师能否晚点交作业",
        "问房东能不能养宠物", "问能不能刷卡", "问能否先看菜单",
        "问能不能拍照",
    ],
    "func_suggestions": [
        "建议同事早点出发", "建议朋友先打电话确认", "建议周末去公园走走",
        "建议点少一点菜", "建议先看评价再订酒店", "建议把会议改到下午",
        "建议累了就休息一下", "建议带孩子去动物园", "建议买之前先试一下",
        "建议下雨天带伞",
    ],
    "func_complaints": [
        "房间太吵睡不着", "外卖送得太慢", "新杯子漏水", "空调不制冷",
        "同事开会总迟到", "网速太慢影响工作", "餐厅的菜太咸", "酒店热水不热",
        "快递被放错了地方", "预约被无故取消",
    ],
    "func_apologies": [
        "迟到向朋友道歉", "打翻咖啡向同事道歉", "忘记回消息向朋友道歉",
        "弄丢了借来的书", "走错了会议室", "吵到邻居休息",
        "忘了带答应带的东西", "临时取消约定", "说错话让同事不舒服",
        "把孩子的水杯摔坏",
    ],
    "func_clarification": [
        "没听清会议时间", "确认见面地址", "确认付款方式",
        "确认明天是上午还是下午", "确认要带的材料", "澄清自己不是那个意思",
        "问价格是否含税", "确认集合地点", "问药一天吃几次",
        "确认改期后的时间",
    ],
    "func_negotiation": [
        "和房东谈租金", "和同事换班", "请店家晚点关门", "和客户谈交付时间",
        "和室友商量打扫分工", "请酒店延迟退房", "和维修师傅约上门时间",
        "退货时协商方案", "和教练改上课时间", "请朋友分担费用",
    ],
    "func_opinions": [
        "谈一部电影好不好看", "谈一家餐厅值不值得去", "谈换工作的想法",
        "谈孩子该不该早点睡", "谈周末去哪玩", "谈网购还是去实体店",
        "谈公司搬到新地方", "谈学开车难不难", "谈养宠物的责任",
        "谈早起的好处",
    ],
    "func_agreement": [
        "同意同事的方案", "觉得朋友说得有道理", "同意周末聚会",
        "赞同早点出发", "认同这家餐厅好吃", "同意把会议改到下午",
        "觉得价格合理", "同意孩子先写作业", "觉得电影结局不错",
        "认同同事的担心",
    ],
    "func_disagreement": [
        "不同意周末加班", "觉得这家店没那么好吃", "不认同买最贵的",
        "觉得孩子还太小", "不同意马上搬家", "觉得价格太高",
        "认为不必再等", "不赞同取消旅行", "觉得这个方案风险大",
        "不同意现在就决定",
    ],
    "func_refusal": [
        "拒绝同事的加班请求", "婉拒朋友的聚会邀请", "拒绝推销电话",
        "不接额外的工作", "拒绝借出车子", "婉拒周末帮忙搬家",
        "拒绝换座位", "不参加晚上的活动", "拒绝先付全款",
        "婉拒再吃一块蛋糕",
    ],
    "func_reassurance": [
        "安慰迟到的朋友", "告诉孩子打碎杯子没关系", "安慰面试失败的同事",
        "让新手慢慢来", "安慰丢了东西的室友", "告诉对方不用急着回复",
        "安慰第一次上台的同事", "安抚生气的家人", "让担心费用的朋友放心",
        "安慰把菜做咸了的朋友",
    ],
    "func_invitations": [
        "邀请同事下班喝一杯", "邀请朋友周末来家里吃饭", "邀请邻居孩子一起玩",
        "邀请同事参加生日聚会", "邀请朋友一起看电影", "邀请客户参观新展厅",
        "邀请同学参加婚礼", "邀请朋友一起晨跑", "邀请同事参加读书会",
        "邀请家人一起旅行",
    ],
    "func_thanks": [
        "感谢同事帮忙改报告", "感谢朋友去机场接你", "回应别人的感谢",
        "感谢邻居帮忙收快递", "感谢医生耐心解释", "感谢店员帮忙找尺码",
        "回应同事的道谢", "感谢朋友借书给你", "感谢司机等你",
        "感谢家人做饭",
    ],
    "func_offers": [
        "主动帮同事搬东西", "问朋友需不需要带饭", "主动帮邻居拿快递",
        "问老人需不需要扶一把", "提出帮同事看报告", "问朋友需不需要送站",
        "主动帮室友洗碗", "提出帮客户叫车", "问同事需不需要代班",
        "主动帮孩子收拾书包",
    ],
    "coll_make": [
        "做决定前先商量", "工作中犯了个错", "给朋友打个电话", "努力学英语",
        "在新城市交朋友", "出门前确认带钥匙", "给下周做个计划", "选颜色时做选择",
        "列一张购物清单", "打电话预约牙医",
    ],
    "coll_take": [
        "工作累了休息一下", "试衣服前看一眼", "在公园找个座位", "晚饭后散步",
        "照顾生病的家人", "学新技能需要时间", "早上洗个澡", "坐地铁上班",
        "旅行时拍照", "和家人轮流做饭",
    ],
    "coll_have": [
        "买东西前先看一看", "和朋友聊聊天", "中午休息一下", "车出了点问题",
        "聚会上玩得开心", "今天没有时间", "一起吃晚饭", "喝杯咖啡",
        "下午开会", "预约看医生",
    ],
    "coll_get": [
        "出门前准备好", "感冒慢慢好转", "在陌生地方迷路", "得到一个面试机会",
        "孩子自己穿好衣服", "下班后到家", "慢慢习惯新工作", "忙了一天很累",
        "饿了找点东西吃", "得到老板的许可",
    ],
    "coll_keep_pay": [
        "和朋友保持联系", "遇到事先冷静", "答应的事要做到", "图书馆里保持安静",
        "坚持每天锻炼", "认真听讲", "周末去看望老师", "在餐厅付账",
        "交房租", "收到停车罚单",
    ],
    "coll_prepositions": [
        "周末的安排取决于天气", "对摄影很感兴趣", "很擅长做饭", "害怕坐飞机",
        "在车站等朋友", "期待假期", "担心孩子的成绩", "为团队感到骄傲",
        "家乡以美食有名", "准备好面试",
    ],
    "coll_word_family_decide": [
        "决定换工作", "选一份礼物", "建议朋友早点睡", "解释迟到的原因",
        "做了一个重要的决定", "在两种颜色中选择", "听医生的建议",
        "老师解释这道题", "决定周末不加班", "选择坐火车而不是飞机",
    ],
    "coll_word_family_success": [
        "项目终于成功", "英语进步很大", "城市发展很快", "孩子一年长高不少",
        "面试很成功", "提高了工作效率", "公司业务发展顺利", "学游泳有了突破",
        "生意越来越好", "改善了睡眠",
    ],
    "coll_frequency": [
        "总是忘记带伞", "经常周末去爬山", "通常六点下班", "有时和朋友吃饭",
        "偶尔去看电影", "很少熬夜", "从不喝咖啡", "每天早起",
        "每周锻炼两次", "曾经去过那家店",
    ],
    "coll_time_money": [
        "上班总是准时", "赶上了最后一班车", "做家务花了很多时间",
        "不要把时间浪费在手机上", "每月存一点钱", "这个月花钱太多",
        "买不起新手机", "修车花了不少钱", "提前准备好材料", "为了省钱自己做饭",
    ],
    "present_continuous": [
        "现在外面正在下雨", "孩子正在写作业", "我在等公交车", "他在接电话",
        "妈妈在厨房做饭", "同事们在开会", "我在找钥匙", "邻居在装修",
        "爸爸在看电视", "她们在公园跑步",
    ],
    "past_perfect": [
        "到车站时火车已经开走", "到家发现钥匙忘在公司", "吃完饭才想起没带钱包",
        "到机场时航班已经取消", "开会前他已经准备好材料", "到公司时会议已经开始",
        "睡觉前已经把作业做完", "到医院时医生已经下班", "出门后才想起没关窗",
        "到餐厅时朋友已经点好菜",
    ],
    "third_conditional": [
        "如果昨天早点出门就不会迟到", "如果带伞就不会淋雨", "如果当时多穿点就不会感冒",
        "如果知道会堵车就坐地铁", "如果早点订票就买到便宜票", "如果听你的建议就不会犯错",
        "如果没忘带钥匙就不用等", "如果多复习就能考好", "如果按时出发就赶上火车",
        "如果那天没加班就去聚会",
    ],
    "quantifiers": [
        "冰箱里还有一些鸡蛋", "需要买多少水果", "家里没有多少米了", "来了不少客人",
        "汤里放一点盐", "书包里有很多书", "只剩几个苹果", "时间不够了",
        "人太多了", "菜点太多了",
    ],
    "prepositions_time": [
        "早上七点起床", "周一开会", "晚上八点看电影", "周末去看父母",
        "五月去旅行", "下午三点见客户", "半夜下起雨", "夏天去海边",
        "中午十二点吃饭", "冬天早上很冷",
    ],
    "question_words": [
        "火车几点出发", "附近哪里有好吃的", "这是谁的书", "你为什么迟到",
        "怎么去火车站", "这件衣服多少钱", "哪个颜色好看", "会议什么时候开始",
        "你住在哪儿", "需要多久到机场",
    ],
    "too_enough": [
        "这件外套太贵", "行李太重拿不动", "房间不够大", "汤不够热",
        "他跑得不够快", "时间太短做不完", "咖啡太烫", "座位不够",
        "年纪够大了可以自己决定", "天气太冷不想出门",
    ],
    "so_such": [
        "今天这么冷", "这个蛋糕这么好吃", "他跑得这么快", "这么难的问题",
        "那么远的地方", "天气那么好", "这么小的孩子", "你真是太好了",
        "餐厅那么吵", "这么重要的会议",
    ],
    "causative": [
        "找人修空调", "请人打扫房间", "去理发店剪头发", "让人修电脑",
        "找人装窗帘", "送去洗车", "叫人送水", "请人翻译文件",
        "找人做书架", "拿去修手表",
    ],
    "modals_deduction": [
        "他一定在开会", "灯关着可能出门了", "这么晚不可能还在工作", "他应该是忘了",
        "地上有水一定下过雨", "电话没人接可能睡了", "她脸色不好一定很累", "不可能这么快到",
        "这份礼物应该是给孩子的", "钥匙可能在包里",
    ],
    "present_perfect_continuous": [
        "一直在学英语", "最近一直加班", "在门口等了一个小时", "这几天一直下雨",
        "在这家公司工作了五年", "一直在找房子", "孩子一直在哭", "最近一直在锻炼",
        "学开车学了两个月", "一直在准备考试",
    ],
    "indirect_questions": [
        "你知道附近有没有超市", "能不能告诉我怎么走", "请问洗手间在哪里",
        "你知道他什么时候回来", "我想知道票价多少", "请问几点关门",
        "你知道这班车到不到火车站", "能不能告诉我他的名字", "你知道哪里可以修手机",
        "我想问这里还招不招人",
    ],
    "gerund_subject": [
        "学英语需要时间", "跑步对身体好", "早睡早起很健康", "做饭比外面吃省钱",
        "游泳是最好的运动", "读书能让人放松", "开车上班更方便", "存钱不容易",
        "听音乐能减压", "养花让我开心",
    ],
    "adverbs_manner": [
        "他认真地准备了报告", "她慢慢地走进房间", "请大声一点说", "孩子们安静地看书",
        "他礼貌地拒绝了邀请", "她清楚地解释了原因", "我们安全地到了家", "他很快完成了工作",
        "她开心地笑了", "请仔细地检查一遍",
    ],
    "reflexive_pronouns": [
        "我自己做的晚饭", "你自己要小心", "他自己修好了电脑", "她自己搬了家",
        "孩子自己穿好了衣服", "我们自己想办法", "你们自己决定吧", "他们自己解决了问题",
        "猫自己打开了门", "我自己去就行",
    ],
    "word_pairs_say_tell": [
        "他告诉我明天放假", "妈妈让我早点回家", "老师跟我们说考试推迟了", "他说他不会来",
        "说实话我不太喜欢", "她讲故事给孩子听", "他说不出话来", "请你说清楚一点",
        "他没告诉我这件事", "医生说要多喝水",
    ],
    "word_pairs_speak_talk": [
        "我会说一点英语", "他们用英语交谈", "我想跟你谈谈", "她说话声音很小",
        "老板在会议上发言", "我们聊了很久", "他说话很直接", "你可以跟经理谈",
        "她英语说得很流利", "别在图书馆大声说话",
    ],
    "word_pairs_borrow_lend": [
        "我借了同学一支笔", "他向我借了雨伞", "图书馆可以借书", "我把车借给朋友",
        "能借我手机用一下吗", "他借给我一本书", "请不要把书借给别人", "我向邻居借了工具",
        "相机借我几天", "她把钱借给了弟弟",
    ],
    "word_pairs_bring_take": [
        "明天带伞", "他带了水果来", "请把文件带给我", "我要带孩子去医院",
        "她带走了我的书", "记得带护照", "把垃圾拿出去", "我带了礼物给父母",
        "请把杯子拿到厨房", "他带朋友回家吃饭",
    ],
    "word_pairs_learn_study_teach": [
        "我在学游泳", "他学习很努力", "老师教我们数学", "我每天学一小时英语",
        "她教孩子做饭", "我想学开车", "他在大学学经济", "她自学了编程",
        "教别人也是一种学习", "这门课很难学",
    ],
    "word_pairs_see_look_watch": [
        "我在街上看见老王", "看一下这个菜单", "孩子们在看电视", "我们昨晚看了一部电影",
        "你看这张照片", "我下午去看医生", "她看着窗外发呆", "你看比赛了吗",
        "我看见彩虹了", "帮我看着孩子",
    ],
    "word_pairs_hear_listen": [
        "我听见有人敲门", "我在听音乐", "电话里听不清", "请听我说完",
        "他每天听广播", "你听见外面的声音了吗", "她听讲座很认真", "我们应该听医生的建议",
        "我听出他的声音了", "孩子们在听故事",
    ],
    "word_pairs_hope_wish": [
        "希望明天天气好", "希望你能来", "希望考试通过", "希望早点到家",
        "但愿别再下雨", "要是当时努力就好了", "希望你喜欢这份礼物", "希望孩子快点好起来",
        "但愿我没记错", "希望下次有机会",
    ],
    "word_pairs_remember_remind": [
        "记得带钥匙", "记得关灯", "提醒我下午开会", "提醒他吃药",
        "我想不起来他的名字", "我不记得放在哪儿了", "记得给妈妈打电话", "请提醒我带伞",
        "我记得关过门", "提醒我明天交报告",
    ],
    "word_pairs_win_earn": [
        "我们队赢了比赛", "他赢得了冠军", "她每月挣八千块", "他靠兼职赚钱",
        "我们打败了强队", "这场球我们赢了", "他挣的钱不多", "她赚够了学费",
        "我们赢了第一名", "他靠写作挣钱",
    ],
    "roleplay": [
        "问候并确认对方的预约或需求", "回答价格、时间或地点", "解释一条规则或流程",
        "给出建议或提醒注意事项", "处理对方的问题或投诉", "提供两个可选的方案",
        "核对姓名、数量或联系方式", "说明下一步该怎么做", "为不便道歉并给出补偿",
        "结束对话并道别",
    ],
    "dialogue": [
        "询问营业时间与对方回答", "询问价格与对方回答", "询问位置与对方指路",
        "询问是否有空位或库存与对方确认", "提出要求与对方接受或拒绝",
        "说明问题与对方给出解决办法", "商量时间与对方确认安排", "点单或预订与对方复述确认",
        "询问流程与对方讲解步骤", "道谢道别与对方回应",
    ],
}
