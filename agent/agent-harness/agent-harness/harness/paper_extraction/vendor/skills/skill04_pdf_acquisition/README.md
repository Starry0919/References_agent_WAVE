# Skill04：论文 PDF 获取与可追溯制品管理

根据 Skill03 验证后的 DOI 自动定位合法开放获取 PDF，记录来源、下载尝试、许可证（若来源提供）、版本、SHA-256 和文件路径；用户上传 PDF 使用同一验证和 Artifact 管理流程，并可直接进入 Skill05。

本实现吸收桌面 `论文下载` 技能中的多来源定位、严格 PDF 检查和失败清单思想，但不包含 Sci-Hub、Cloudflare 绕过、浏览器反自动化规避或付费墙绕过。

## 自动下载顺序

1. OpenAlex OA location
2. Europe PMC
3. Unpaywall OA location
4. Semantic Scholar `openAccessPdf`
5. 调用方明确提供的出版商 PDF URL
6. 调用方明确提供的仓储 PDF URL
7. DOI 标准内容协商

所有响应均检查扩展名/文件名、`%PDF-` magic、内容类型、非空内容和 `%%EOF`，HTML 页面不会保存为 PDF。

## OpenAlex

OpenAlex 用于小批量 DOI 的开放获取定位。配置：

```powershell
$env:OPENALEX_API_KEY = "your-key"
```

只使用 OpenAlex 标记为 OA 的 location 及其 `pdf_url`。API 未配置、无 OA URL 或下载失败时会继续下一个合法来源。

OpenAlex 当前要求 API key；免费 key 有每日免费额度。密钥不会写入日志、Artifact 或下载尝试。

## Unpaywall

可选配置：

```powershell
$env:UNPAYWALL_EMAIL = "your-email@example.org"
```

未配置时自动跳过。

## 小批量与指定论文

```json
{
  "download_policy": {
    "max_candidates": 5,
    "paper_ids": ["paper:example"]
  }
}
```

`paper_ids` 先筛选，`max_candidates` 再限制本批次；未处理项进入 `deferred_items`。模块编排器默认每批最多 5 篇，可通过 `options.pdf_download_policy` 调整。

## 输出

- `paper_artifacts`：已验证 PDF，可直接交给 Skill05。
- `failed_items`：每个来源的完整尝试记录。
- `deferred_items`：因小批量策略延后处理的论文。
- `manual_download_items`：DOI 链接和失败原因，供用户合法手动获取后通过 `manual_uploads` 重新进入。

每个成功 Artifact 保留论文身份、来源 URL、下载时间、下载状态、版本、checksum、不可变复用状态和全部尝试记录。

## 人工上传

```json
{
  "manual_uploads": [
    {
      "path": "D:\\papers\\paper.pdf",
      "paper_id": "paper:manual"
    }
  ]
}
```

上传文件不会跳过完整性检查，但不要求 DOI。
