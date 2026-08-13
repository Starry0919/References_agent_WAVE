# Same-PDF Parser Benchmark v2

Five lawful local PDFs were parsed by OpenDataLoader 2.5.0 and PyPDF fallback. OpenDataLoader completed 5/5 in 25.8s batch, emitted page-level blocks/bboxes, Markdown and images; fallback completed 5/5 but had no native table/figure/page-block contract.

Critical limitation: these exact five PDFs do not have matching repository MinerU clean artifacts. Existing MinerU artifacts are other papers. Therefore `pdf_parser_same_pdf_benchmark_v2.json` explicitly records `NO_MATCHING_MINERU_ARTIFACT_FOR_THESE_5_PDFS`; no OpenDataLoader-vs-MinerU superiority claim is made. MinerU remains PRIMARY, OpenDataLoader becomes SHADOW, PyPDF remains FALLBACK.
