# 更新说明

## gpt-image skill 新增 `--quality` 参数支持

### 脚本变更

`generate_image.py` 和 `generate_image_with_refs.py` 均新增 `--quality` 参数：

```bash
python scripts/generate_image.py "a cyberpunk cat" --quality high
python scripts/generate_image_with_refs.py "same character" --quality low --image ./ref.jpg
```

可选值：
- `auto`（默认）— 模型自动选择最佳质量
- `low` — 快速草稿，token 成本最低
- `medium` — 平衡质量和速度
- `high` — 最佳细节和保真度，token 成本最高

### 文档更新

SKILL.md 新增 **Size and Quality Reference** 参考小节，包含：
- 常用分辨率对照表（含生成速度提示）
- 自定义分辨率约束条件（max 3840px、16px 倍数等）
- quality 各档位速度/成本/适用场景对照
- 快速决策规则（draft → low / final → high 等）

分辨率说明也已同步更新：支持任意自定义分辨率（满足约束即可），不再限于固定几个尺寸。
