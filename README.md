# 生活英语句子卡组

面向中文母语者的场景化生活英语 Anki 卡组：**中文正面、英文背面**，用于练日常口语输出，而不是英译中理解。词汇控制在 A1–B2，话题按真实生活场景组织。

- 25 个生活场景、204 个微情境
- 当前 3,691 张卡片（每场景 107–214 张）
- 本地 Ollama 生成 + 润色，AnkiConnect 幂等导入

## 卡组内容

| 项目 | 值 |
|---|---|
| 场景数 | 25 |
| 微情境数 | 204 |
| 卡片数 | 3,691（生成 3,692，1 张跨场景重复未导入） |
| 正面 | `[场景中文] 中文句子` |
| 背面 | `[Scene English] English sentence.` |
| 词频 | A1–B2 日常口语；wordfreq 做生僻词检查 |

场景覆盖：服装购物、超市、餐厅、外卖、打车、机场、酒店、问路、医院药店、银行、网购、咖啡快餐、公共交通、手机网络、快递、理发、租房维修、汽车停车、紧急情况、办公室、学校、电话客服、社交、观光、天气闲聊。

## 目录结构

```
config/scenes.toml          场景、微情境与目标数量
prompts/                    Ollama 系统提示与生成提示
scripts/
  plan.py                   生成微情境计划（每个微情境 8–10 个具体情境）
  clean_plans.py            清理计划中的泛化项与跨微情境重复
  generate.py               按计划生成中英句子（可断点续跑）
  qc.py                     质检（重复、词频、专名、长度、标点等）
  review_report.py          生成静态 HTML 审阅页
  polish.py                 用 14B 润色英文（原文件不动，输出到独立目录）
  reconcile_polish.py       回退润色产生的同场景重复/近似重复
  import_anki.py            AnkiConnect 导入与更新
  build_release.py          构建 .apkg、数据 zip 与校验和
  run_*.sh                  批量运行脚本
.github/workflows/
  build.yml                 CI：质检、构建、来源证明、Release
data/
  plans/                    各场景微情境计划
  sentences/                7B 生成结果（JSONL，每场景一个文件）
  sentences_polished/       14B 润色结果（Anki 当前数据来源）
  patches/                  逐卡润色记录（uid、old_en、new_en）
  archive/                  早期废弃的试点版本
  benchmark.jsonl           人工撰写的风格基准句
reports*/                   质检报告、审阅页、润色汇总（本地生成，不入库）
dist/                       本地/CI 构建产物（不入库）
```

## 环境要求

- macOS（M1 Pro / 32 GB 实测通过）
- Python 3.12
- [uv](https://docs.astral.sh/uv/) 管理虚拟环境
- Ollama，模型 `qwen2.5:7b`（生成）与 `qwen2.5:14b`（润色）
- Anki + AnkiConnect 插件（默认 `http://127.0.0.1:8765`）

```bash
/Users/Larry/.local/bin/uv venv .venv --python 3.12
/Users/Larry/.local/bin/uv pip install --python .venv/bin/python -r requirements.txt
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
```

> 注意：部分 shell 里 `uv` 被 alias 成 `uv pip`，建议使用绝对路径调用。

## 使用流程

```bash
# 1. 生成微情境计划
python3 scripts/plan.py --scene shopping_clothes --items 10
python3 scripts/clean_plans.py --apply

# 2. 生成句子（--pause 控制调用间隔，降低发热）
python3 scripts/generate.py --scene shopping_clothes --pause 2

# 3. 质检与审阅页
.venv/bin/python scripts/qc.py --check-target
.venv/bin/python scripts/review_report.py

# 4. 14B 润色（写入 data/sentences_polished/）
.venv/bin/python scripts/polish.py --batch 10 --pause 1
python3 scripts/reconcile_polish.py --apply

# 5. 润色版质检与审阅页
.venv/bin/python scripts/qc.py --data-dir data/sentences_polished --report-dir reports_polished --check-target
.venv/bin/python scripts/review_report.py \
  --data-dir data/sentences_polished \
  --qc-report reports_polished/qc_report.json \
  --out reports/review_polished.html

# 6. 导入 Anki
python3 scripts/import_anki.py --data-dir data/sentences_polished --apply
# 已有卡片需要同步最新英文时：
python3 scripts/import_anki.py --data-dir data/sentences_polished --update-existing --verify --apply
```

批量脚本按顺序执行即可：`run_core_plans.sh` → `run_generate_core.sh` → `run_generate_remaining.sh`；`run_overnight.sh` 串起质检与剩余场景，`run_polish.sh` 在生成结束后自动润色。

## 数据格式

每张卡一行 JSON（JSONL）：

```json
{
  "uid": "shopping_clothes-1644cf6af8",
  "scene": "shopping_clothes",
  "scene_zh": "服装购物",
  "scene_en": "Clothes Shopping",
  "group": "日常消费与餐饮",
  "phase": 1,
  "micro": "price_discount",
  "micro_zh": "问价格和折扣",
  "zh": "这件衣服价格是多少？",
  "en": "How much does this piece of clothing cost?",
  "sub": "问这件衣服的价格",
  "angle": "ask for information, ...",
  "model": "qwen2.5:7b",
  "created_at": "2026-11-17T18:20:00+00:00"
}
```

`uid` 由 `场景 id + SHA-1(规范化中文)[:10]` 生成，中文不变则 UID 不变，便于 Anki 幂等更新。

## Anki 结构

- 牌组：`生活英语句子`
- 笔记类型：`生活句子 ZH→EN`
- 字段：`Chinese`、`English`、`SceneZH`、`SceneEN`
- 标签：`scene::<id>`、`micro::<scene>::<micro>`、`phase::<n>`、`src::<model>`、`uid::<uid>`

`data/imported.json` 记录 UID → Anki note id，属于本机数据，已加入 `.gitignore`。

## 质检说明

`qc.py` 检查：缺失字段、未知场景/微情境、重复 UID、同场景重复中英文、语言混入、长度、标点、专名、品牌、正式用语，以及基于 `wordfreq` 的生僻词。跨场景重复只记为警告，因为同一句话在不同场景下仍有练习价值。

当前状态（2026-11-18）：润色版 0 错误；警告主要为生僻词、T恤/Wi-Fi/登机口字母等专名、少量品牌词（微信、支付宝），以及 43 处跨场景重复。

## Git 与 LFS

仓库忽略 `.venv/`、日志、HTML 报告与本机导入清单。当前跟踪文件中最大约 100 KB，**不需要 Git LFS**。若以后加入 `.apkg`、音频或图片等大文件，可执行：

```bash
git lfs install
git lfs track "*.apkg" "*.mp3" "*.png" "*.jpg"
git add .gitattributes
```

## 构建产物

```bash
.venv/bin/python scripts/build_release.py --version v1.0.0
```

输出到 `dist/`：

- `anki_sentence-<version>.apkg`：可直接导入 Anki 的牌组。牌组 ID、笔记类型 ID 与卡片 GUID 均固定，重复导入会更新已有卡片而不是新建。
- `anki_sentence-<version>-data.zip`：润色后 JSONL 数据、场景配置、提示词、README 与 LICENSE。
- `SHA256SUMS`：两份产物的 SHA-256 校验值。

## CI 与发布

[.github/workflows/build.yml](.github/workflows/build.yml) 在以下情况触发：

- 推送到 `main`：质检 + 构建，产物上传为 workflow artifact，版本名为 `dev-<short sha>`。
- 推送 `v*.*.*` 标签：先校验语义化版本号，再构建、生成来源证明，并创建附带全部产物的 GitHub Release。

版本标签必须符合 `vMAJOR.MINOR.PATCH`，可带预发布或构建元数据后缀（如 `v1.2.3-rc.1`、`v1.2.3+build.5`）。不合法（例如 `v1.2`）会让工作流失败。

```bash
git tag v1.0.0
git push origin v1.0.0
```

质检使用 `qc.py --fail-on-error`，存在 error 级别问题时会阻止构建和发布。

## 验证产物来源

工作流用 `actions/attest-build-provenance` 为 `.apkg` 与数据 zip 生成构建来源证明。下载 Release 产物后可验证：

```bash
gh attestation verify anki_sentence-v1.0.0.apkg --repo pnnh/anki_sentence
gh attestation verify anki_sentence-v1.0.0-data.zip --repo pnnh/anki_sentence
```

校验文件完整性：

```bash
sha256sum -c SHA256SUMS
```

## 许可

AGPL-3.0，见 [LICENSE](LICENSE)。
