# Optional Doubao source advisor

Set `ARK_API_KEY` and optionally `ARK_MODEL` to enable the Volcengine Ark
advisor. Credentials are read from the process environment only and are never
written to source code, logs, artifacts, or release archives.

Doubao can only reorder already configured legal source types. It cannot invent
a PDF URL, DOI, license, bibliographic fact, or successful download. Invalid
responses and API failures fall back to deterministic ordering. MIME, `%PDF-`,
EOF, checksum, version and provenance checks remain mandatory.

```powershell
$env:ARK_API_KEY = "<rotated-key>"
$env:ARK_MODEL = "doubao-smart-router-250928"
```
