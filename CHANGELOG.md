# 更新说明

## Gemini 脚本兼容官方 API 格式（camelCase）

### 问题

中转层对接 Gemini 官方 API 后，请求/响应格式从供应商自定义的 snake_case 变为 Gemini 官方的 camelCase，导致：
- 图片输入请求失败（`inline_data` → `inlineData`）
- 响应解析找不到图片数据（`inline_data` → `inlineData`）

### 修复

`generate_gemini_image.py`：
- 请求中 image input 字段统一使用 `inlineData` / `mimeType` / `data`（camelCase）
- 响应解析同时兼容 `inlineData`（官方）和 `inline_data`（旧版），确保向后兼容

### 影响脚本

- `generate_gemini_image.py`
- `generate_gemini_image_with_refs.py`（依赖主脚本，自动修复）

---

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
