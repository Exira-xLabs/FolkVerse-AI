> Superseded as an owner task on 7 October: the owner declined human review. This remains an optional, unscored human-review artifact. Codex assessment is separately labelled in [the current report](PHASE_03_AUTONOMOUS_SOURCE_REVIEW.md); no ratings here have been fabricated.

# Jinyao — actual bilingual human review packet

Run SHA-256: `98b39f9e2e3d39a564843edce6d01bd40255ae56ca1a1654de2a1d6927d49dae`

These are actual recorded model answers. Machine structural/support checks are reported separately. No human judgments have been supplied.

Review the English/Chinese pairs for factual correctness, clarity, faithful meaning and personality. For general explanations, verify against independent primary or scholarly references; an unverified label is not proof of correctness. For precise facts, inspect original sources, dates, attribution and current applicability. Check warmth, repetition, helpful invitations and false institutional authority.

Record PASS/FAIL in `human-review-template.json`, with your name, timezone-aware timestamp, rationale, independent basis and `attest_human_review: true`. Leave unanswered units null. A partial review is reported as partial; no missing rating becomes a pass.

After reviewing, run:

```sh
uv run --project apps/api python -m folkverse.guide_review grade --run report/evidence/phase03-hybrid-part07/evaluation-diagnostic.json --reviews report/evidence/phase03-hybrid-part07/human-review-template.json --output report/evidence/phase03-hybrid-part07/human-review-completed.json
```

Owner/editor review and independent specialist review remain distinct. This worksheet cannot authenticate identity or certify expertise.

## hello — en

Case: `hybrid-v3-hello-en` · conversational · concise

**Question:** Hi Jinyao!

Hi! I’m Jinyao, your fictional cultural companion. What are you curious about today?

Human ratings: **pending**.

## hello — zh-CN

Case: `hybrid-v3-hello-zh-CN` · conversational · concise

**Question:** 锦瑶你好！

你好！我是锦瑶，你的虚构文化伙伴。 今天你对什么感到好奇？

Human ratings: **pending**.

## identity — en

Case: `hybrid-v3-identity-en` · conversational · concise

**Question:** What is your name?

I’m Jinyao, a fictional companion in FolkVerse. I help explain cultural material and show what our sources support.

Human ratings: **pending**.

## identity — zh-CN

Case: `hybrid-v3-identity-zh-CN` · conversational · concise

**Question:** 你叫什么名字？

你可以叫我锦瑶。我是由 AI 支持的虚构向导，会坦诚说明哪些内容能够核实、哪些还不能。

Human ratings: **pending**.

## thanks — en

Case: `hybrid-v3-thanks-en` · conversational · concise

**Question:** Thank you

You’re welcome!

Human ratings: **pending**.

## thanks — zh-CN

Case: `hybrid-v3-thanks-zh-CN` · conversational · concise

**Question:** 谢谢你

能帮上忙就好。

Human ratings: **pending**.

## emoji — en

Case: `hybrid-v3-emoji-en` · conversational · concise

**Question:** 🙂

Hi! I’m Jinyao, your fictional cultural companion. What are you curious about today?

Human ratings: **pending**.

## emoji — zh-CN

Case: `hybrid-v3-emoji-zh-CN` · conversational · concise

**Question:** 🙂

嗨，很高兴和你聊天。 今天你对什么感到好奇？

Human ratings: **pending**.

## listing — en

Case: `hybrid-v3-listing-en` · answered · concise

**Question:** Where is Fuzhou shadow puppetry listed?

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## listing — zh-CN

Case: `hybrid-v3-listing-zh-CN` · answered · concise

**Question:** 复州皮影戏在哪个地区？

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## beginner — en

Case: `hybrid-v3-beginner-en` · answered · beginner

**Question:** Explain Fuzhou shadow puppetry simply

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

**general_unverified**

Shadow puppetry is a traditional form of storytelling with flat, jointed figures held behind a lit screen. Light casts the puppets' shadows toward the audience while performers move them and often sing or narrate. Think of it like an early cartoon: the screen is the picture, and the puppeteer is the animator.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## beginner — zh-CN

Case: `hybrid-v3-beginner-zh-CN` · answered · beginner

**Question:** 简单介绍复州皮影戏

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

**general_unverified**

皮影戏是一种用灯光把兽皮或纸板刻成的影人映在幕布上、由人幕后操纵并配唱讲述故事的民间戏剧。可以把它想成“会动的剪纸加配音讲故事”。它通常靠师徒或家族传承，剧目多取自民间传说与历史故事。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## depth — en

Case: `hybrid-v3-depth-en` · answered · deeper

**Question:** Explain Fuzhou shadow puppetry in more detail

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

**general_unverified**

Shadow puppetry is a traditional performance art in which flat, jointed figures are held behind a lit screen, so the audience sees their shadows. Puppeteers sing, narrate and move the figures to music, often telling folk stories. Think of it as an early form of animation: light, screen and moving cut-outs create the illusion of life. How might a single puppeteer voice several characters at once?

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## depth — zh-CN

Case: `hybrid-v3-depth-zh-CN` · answered · deeper

**Question:** 详细介绍复州皮影戏

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

**general_unverified**

皮影戏是一种用兽皮或纸板刻成人物剪影、在灯光下借幕布表演的民间戏剧。艺人一边操纵影人，一边配唱与伴奏，观众看到的是投射在幕布上的影子。它像会动的剪纸动画，把雕刻、绘画、唱腔和器乐合在一起。不同地方会形成各自的唱腔与影人造型，因此常以地名区分流派。想进一步了解，可以问：影人是怎么在幕后被操纵得如此灵活的？

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## definition — en

Case: `hybrid-v3-definition-en` · answered · beginner

**Question:** What is shadow puppetry?

**general_unverified**

Shadow puppetry is a traditional form of storytelling with flat, cut-out figures. A puppeteer moves the figures behind a lit cloth screen, so the audience sees only their shadows. Think of making animal shapes with your hands on a wall lit by a lamp: the puppet figures work the same way, but they are carved and jointed. Shows often pair movement with music, singing and narration.

Coverage: Source support is checked; general context is not independently fact-verified.

Human ratings: **pending**.

## definition — zh-CN

Case: `hybrid-v3-definition-zh-CN` · answered · beginner

**Question:** 什么是皮影戏？

**general_unverified**

皮影戏是一种用灯光把兽皮或纸板刻成的人物剪影投射到幕布上、配合唱腔和音乐来表演故事的民间戏剧。可以把它想成“会动的剪纸动画”：艺人在幕后操纵影人，观众在幕前看到影子演出。它融合雕刻、绘画、演唱和乐器伴奏，是传统表演艺术的一种。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Human ratings: **pending**.

## glossary — en

Case: `hybrid-v3-glossary-en` · answered · beginner

**Question:** What does silhouette mean?

**general_unverified**

A silhouette is the dark outline or shape of a person or object seen against a brighter background. Think of your shadow on a sunny wall: you see its edge and form, not its details. Artists use silhouettes in drawing, photography and shadow play, where a cut-out figure blocks light to create a moving shape.

Coverage: Source support is checked; general context is not independently fact-verified.

Human ratings: **pending**.

## glossary — zh-CN

Case: `hybrid-v3-glossary-zh-CN` · answered · beginner

**Question:** 剪影是什么意思？

**general_unverified**

剪影是指用纸或皮等材料剪出人物、动物等轮廓，放在光源前，让影子投在幕布上。它像用手在灯前做手影：重点不是材料本身，而是影子形成的形状。剪影常用来讲故事或做装饰，因为只看外形也能认出角色。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Human ratings: **pending**.

## concept_why — en

Case: `hybrid-v3-concept_why-en` · answered · deeper

**Question:** Why do museums explain their sources?

**general_unverified**

Museums explain their sources to build trust and help visitors understand how knowledge is made. A source note shows where information, objects, or images came from, so people can judge reliability and context. This matters because museums interpret the past; without sources, claims can look like opinions. It also respects creators and communities, supports research, and lets others verify or build on the work. Think of a recipe: listing ingredients and steps lets you trust and repeat it. What source would you want to see for a display you find surprising?

Coverage: Source support is checked; general context is not independently fact-verified.

Human ratings: **pending**.

## concept_why — zh-CN

Case: `hybrid-v3-concept_why-zh-CN` · answered · deeper

**Question:** 为什么博物馆要说明资料来源？

**general_unverified**

博物馆说明资料来源，是为了让观众知道展品信息从哪里来、经过哪些整理与核对。资料可能来自考古发掘、捐赠、旧档案或研究论文，不同来源的可信度与完整度不同。标注来源就像给知识贴上“产地标签”：观众能判断这是直接证据还是后人推断，也能在需要时自行查证。更深一层，来源说明还体现学术透明与责任——它让结论可被检验、可被修正，而不是把观点伪装成定论。你可以问自己：如果一段说明没有出处，我还能怎样验证它？

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Human ratings: **pending**.

## comparison — en

Case: `hybrid-v3-comparison-en` · answered · deeper

**Question:** What is the difference between folklore and historical evidence?

**general_unverified**

Folklore is a community's traditional stories, beliefs, and customs, passed down informally and valued for cultural meaning. Historical evidence is information from the past that can be examined and tested, such as documents, objects, or records. The key difference is purpose and method: folklore explains identity and values, while historical evidence aims to support or challenge factual claims about what happened. A useful question: does this story tell us what a group believes, or what actually occurred?

Coverage: Source support is checked; general context is not independently fact-verified.

Human ratings: **pending**.

## comparison — zh-CN

Case: `hybrid-v3-comparison-zh-CN` · answered · deeper

**Question:** 民间传说和历史证据有什么区别？

**general_unverified**

民间传说像口耳相传的故事，重在传递情感、价值观和集体记忆；历史证据则是可核查的实物或文字记录，如出土器物、档案、碑刻，重在还原真实发生过的事。传说可能包含真实影子，但会随讲述者增删细节；证据要求来源、年代和背景可被检验。可以把传说想成“大家记得的版本”，证据是“能拿出来对证的版本”。两者并非完全对立：传说能提示人们关注什么，证据则决定我们能否确认。读史时不妨问：这条说法有同时代的物证或文献支持吗？

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Human ratings: **pending**.

## simple_followup — en

Case: `hybrid-v3-simple_followup-en` · answered · beginner

**Question:** Explain that simply

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

**general_unverified**

Shadow puppetry is a traditional way of telling stories with flat, jointed figures held behind a lit screen. Performers move the puppets and often sing or narrate, while the audience sees colourful silhouettes. Think of it as an early kind of animation, where hands and light create the moving picture.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## simple_followup — zh-CN

Case: `hybrid-v3-simple_followup-zh-CN` · answered · beginner

**Question:** 解释得简单一点

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

**general_unverified**

皮影戏是一种用灯光把兽皮或纸板刻成的人物影子投到幕布上、由人边操纵边唱故事的表演。可以把它想成会动的剪纸动画：影子在幕后动，观众在幕前看。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## deeper_followup — en

Case: `hybrid-v3-deeper_followup-en` · answered · deeper

**Question:** Go deeper

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

**general_unverified**

Shadow puppetry is a storytelling art using flat cut-out figures held behind a lit screen. Performers move them with rods while narrating and singing, so the audience sees colourful silhouettes. Think of it as an early kind of animation, where hands and light bring characters to life. What might change if the screen were removed?

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## deeper_followup — zh-CN

Case: `hybrid-v3-deeper_followup-zh-CN` · answered · deeper

**Question:** 详细一点

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

**general_unverified**

皮影戏是一种用兽皮或纸板刻成人物剪影、借灯光投射到幕布上表演故事的民间戏剧。艺人躲在幕后操纵影人，同时配唱腔与乐器，观众看到的是会动的影子。它把雕刻、绘画、音乐和叙事合在一起，可理解为“会动的剪纸戏”。想进一步了解时，可以问：影人的关节是怎样让它做出走路、打斗等动作的？

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## language_followup — en

Case: `hybrid-v3-language_followup-en` · answered · beginner

**Question:** 用英文说

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## language_followup — zh-CN

Case: `hybrid-v3-language_followup-zh-CN` · answered · beginner

**Question:** Say that in Chinese

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## mixed_greeting — en

Case: `hybrid-v3-mixed_greeting-en` · answered · beginner

**Question:** Hi, explain Fuzhou shadow puppetry

**sources_checked**

Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

**general_unverified**

Shadow puppetry is a traditional art where flat figures are held behind a lit screen, so the audience sees their shadows. Puppeteers move the figures with rods while telling stories with music and voices. Think of it like an animated film made by hand, live.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.071728Z

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

Human ratings: **pending**.

## mixed_greeting — zh-CN

Case: `hybrid-v3-mixed_greeting-zh-CN` · answered · beginner

**Question:** 你好，介绍复州皮影戏

**sources_checked**

复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [First provincial intangible cultural heritage list (2006)](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml) — Liaoning Provincial Government
Fetched: 2026-10-05T01:26:30.047882Z · classification: source_statement · reviewed_corpus
Editorial review: Project owner (user) · 2026-10-05T01:31:27.073642Z

> 复州皮影戏在辽宁省非遗名录中列为瓦房店市申报的传统戏剧项目。

Human ratings: **pending**.

## lookup_date — en

Case: `hybrid-v3-lookup_date-en` · answered · concise

**Question:** When was Shenyang Imperial Palace founded?

**official_lookup**

According to the official profile, Shenyang Imperial Palace was founded in 1625.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [沈阳市·沈阳故宫](https://whly.ln.gov.cn/whly/wlzt/sjly/ajjq/2026031617080553830/index.shtml) — Liaoning Department of Culture and Tourism
Fetched: 2026-10-07T02:19:34.560430Z · classification: source_statement · official_lookup
Editorial review: pending · pending

> The Liaoning Department of Culture and Tourism has an official profile of Shenyang Imperial Palace.
According to the official profile, Shenyang Imperial Palace was founded in 1625.

Human ratings: **pending**.

## lookup_date — zh-CN

Case: `hybrid-v3-lookup_date-zh-CN` · answered · concise

**Question:** 沈阳故宫始建于哪一年？

**official_lookup**

官方介绍记载，沈阳故宫始建于1625年。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [沈阳市·沈阳故宫](https://whly.ln.gov.cn/whly/wlzt/sjly/ajjq/2026031617080553830/index.shtml) — Liaoning Department of Culture and Tourism
Fetched: 2026-10-07T02:19:36.278950Z · classification: source_statement · official_lookup
Editorial review: pending · pending

> 辽宁省文化和旅游厅的资料介绍了沈阳故宫。
官方介绍记载，沈阳故宫始建于1625年。
景区当前等级：4A
沈阳故宫始建于1625年，占地面积6万平方米，共保留清代建筑114座，计500余间。

Human ratings: **pending**.

## lookup_followup — en

Case: `hybrid-v3-lookup_followup-en` · answered · beginner

**Question:** Explain that simply

**official_lookup**

According to the official profile, Shenyang Imperial Palace was founded in 1625.

Coverage: Source support is checked; general context is not independently fact-verified.

Source: [沈阳市·沈阳故宫](https://whly.ln.gov.cn/whly/wlzt/sjly/ajjq/2026031617080553830/index.shtml) — Liaoning Department of Culture and Tourism
Fetched: 2026-10-07T02:19:40.777970Z · classification: source_statement · official_lookup
Editorial review: pending · pending

> The Liaoning Department of Culture and Tourism has an official profile of Shenyang Imperial Palace.
According to the official profile, Shenyang Imperial Palace was founded in 1625.

Human ratings: **pending**.

## lookup_followup — zh-CN

Case: `hybrid-v3-lookup_followup-zh-CN` · answered · beginner

**Question:** 解释得简单一点

**official_lookup**

官方介绍记载，沈阳故宫始建于1625年。

Coverage: 来源支持已经检查；一般背景说明未经独立事实核验。

Source: [沈阳市·沈阳故宫](https://whly.ln.gov.cn/whly/wlzt/sjly/ajjq/2026031617080553830/index.shtml) — Liaoning Department of Culture and Tourism
Fetched: 2026-10-07T02:19:44.895153Z · classification: source_statement · official_lookup
Editorial review: pending · pending

> 辽宁省文化和旅游厅的资料介绍了沈阳故宫。
官方介绍记载，沈阳故宫始建于1625年。
景区当前等级：4A
沈阳故宫始建于1625年，占地面积6万平方米，共保留清代建筑114座，计500余间。

Human ratings: **pending**.

## missing_origin — en

Case: `hybrid-v3-missing_origin-en` · insufficient · concise

**Question:** When was Fuzhou shadow puppetry invented?

I do not have enough reviewed evidence to answer that question.

Coverage: The available reviewed material and official lookup do not support this specific request. General background can be explored separately.

Human ratings: **pending**.

## missing_origin — zh-CN

Case: `hybrid-v3-missing_origin-zh-CN` · insufficient · concise

**Question:** 复州皮影戏是哪一年发明的？

目前经过审核的资料不足以回答这个问题。

Coverage: 现有审核资料与官方查询不足以支持这个具体问题。可以另行了解一般背景。

Human ratings: **pending**.

## current_hours — en

Case: `hybrid-v3-current_hours-en` · insufficient · concise

**Question:** What are the current opening hours of Shenyang Imperial Palace?

I do not have enough reviewed evidence to answer that question.

Coverage: The available reviewed material and official lookup do not support this specific request. General background can be explored separately.

Human ratings: **pending**.

## current_hours — zh-CN

Case: `hybrid-v3-current_hours-zh-CN` · insufficient · concise

**Question:** 沈阳故宫今天几点开放？

目前经过审核的资料不足以回答这个问题。

Coverage: 现有审核资料与官方查询不足以支持这个具体问题。可以另行了解一般背景。

Human ratings: **pending**.

## disputed — en

Case: `hybrid-v3-disputed-en` · insufficient · concise

**Question:** Who first invented Fuzhou shadow puppetry?

I do not have enough reviewed evidence to answer that question.

Coverage: The available reviewed material and official lookup do not support this specific request. General background can be explored separately.

Human ratings: **pending**.

## disputed — zh-CN

Case: `hybrid-v3-disputed-zh-CN` · insufficient · concise

**Question:** 复州皮影戏最早是谁发明的？

目前经过审核的资料不足以回答这个问题。

Coverage: 现有审核资料与官方查询不足以支持这个具体问题。可以另行了解一般背景。

Human ratings: **pending**.

## unsupported_year — en

Case: `hybrid-v3-unsupported_year-en` · insufficient · concise

**Question:** Was Fuzhou shadow puppetry founded in 1644?

I do not have enough reviewed evidence to answer that question.

Coverage: The available reviewed material and official lookup do not support this specific request. General background can be explored separately.

Human ratings: **pending**.

## unsupported_year — zh-CN

Case: `hybrid-v3-unsupported_year-zh-CN` · insufficient · concise

**Question:** 复州皮影戏始建于1644年吗？

目前经过审核的资料不足以回答这个问题。

Coverage: 现有审核资料与官方查询不足以支持这个具体问题。可以另行了解一般背景。

Human ratings: **pending**.

## context_owner — en

Case: `hybrid-v3-context_owner-en` · error · beginner

**Question:** Explain that simply

Controlled error: `invalid_context`

## context_owner — zh-CN

Case: `hybrid-v3-context_owner-zh-CN` · error · beginner

**Question:** 解释得简单一点

Controlled error: `invalid_context`

## greeting_repeat — en

Case: `hybrid-v3-greeting_repeat-en` · conversational · concise

**Question:** Hi again

I’d like to understand what you mean. What are you curious about today?

Human ratings: **pending**.

## greeting_repeat — zh-CN

Case: `hybrid-v3-greeting_repeat-zh-CN` · conversational · concise

**Question:** 你好呀

嗨，很高兴和你聊天。 有没有特别想了解的地方或话题？

Human ratings: **pending**.

## goodbye — en

Case: `hybrid-v3-goodbye-en` · conversational · concise

**Question:** Bye

Goodbye! You’re welcome to come back whenever you feel curious.

Human ratings: **pending**.

## goodbye — zh-CN

Case: `hybrid-v3-goodbye-zh-CN` · conversational · concise

**Question:** 再见

再见！有新的好奇和问题时，欢迎再来聊。

Human ratings: **pending**.
