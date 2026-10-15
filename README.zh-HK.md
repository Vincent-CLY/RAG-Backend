# 🚀 RAG-Backend: 個人檔案知識庫與求職輔助 AI 系統

[ [English](./README.md) ] | [ 繁體中文 / 粵語 ] | [ [📖 核心技術概念與架構決策筆記](./NOTES.md) ]

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Java 21](https://img.shields.io/badge/Java-21+-ED8B00.svg?logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/閘道-Spring%20Boot%203.3-6DB33F.svg?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Virtual Threads](https://img.shields.io/badge/並行-Virtual%20Threads-007396.svg)](https://openjdk.org/jeps/444)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/向量庫-Qdrant-DC382D.svg?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![LangChain](https://img.shields.io/badge/框架-LangChain-1C3C3C.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/智能體-LangGraph-1C3C3C.svg)](https://langchain-ai.github.io/langgraph/)
[![LangSmith](https://img.shields.io/badge/可觀測-LangSmith-FF6F00.svg)](https://smith.langchain.com/)
[![Docling](https://img.shields.io/badge/文檔解析-Docling-052FAD.svg)](https://github.com/DS4SD/docling)
[![MCP](https://img.shields.io/badge/協議-Model%20Context%20Protocol-4B0082.svg)](https://modelcontextprotocol.io/)

一個專為**個人檔案知識庫管理**、**智慧求職履歷配對**以及 **MCP (Model Context Protocol) 伺服器整合**而設計的多模態 RAG 後端系統。

本系統支援多格式文件解析（履歷、作品集、研究報告、投影片、試算表、內嵌圖表與掃描表格），完整保留版面結構與語意上下文，透過 FastAPI 暴露嚴格校驗的 REST API，並以標準化 MCP 協議直連外部主流 AI 客戶端（如 Claude Desktop、Cursor）。

---

## 🎯 專案願景與核心目標

1. **個人知識寶庫 (Personal Vault)**：全面數位化並深度索引履歷、作品集、證照與專案經歷（支援 PDF、PPTX、DOCX、XLSX、HTML、圖片、音視頻）。
2. **AI 求職智慧副駕 (Job Copilot)**：結構化解析目標職缺 (JD)，比對技能落差，自動生成符合 STAR 原則的經歷論述與面試應答建議。
3. **隨插即用 MCP 伺服器**：將檢索功能包裝為標準 MCP Server，讓任何支援 MCP 的 LLM 工具皆能直接調用個人數據庫。
4. **做中學 AI 開發工程實踐**：從零出發，實作現代 AI 工程核心技術（版面分析、混合檢索、狀態機 Agent 與可觀測性除錯）。
5. **雙語多元架構 (Polyglot)**：結合 Python 無可取替嘅 AI/ML 生態，同 Java Virtual Threads 嘅高並行閘道——每種語言各展所長、各司其職。

---

## 🏗️ 多元架構：邊種語言管邊一層？

刻意嘅**職責分離 (Separation of Concerns)**：Java Virtual Threads 管**邊界／控制平面**（安全、路由、限流、可觀測）；Python 管 **AI／資料平面**（解析、檢索、Agent、生成）。完整決策理由見 [NOTES.md §6.9](./NOTES.md)。

| 關注點 | 語言 / 技術 | 點解歸佢管？ |
| :--- | :--- | :--- |
| **認證授權 / 安全** | Java Spring Security | 企業級 OAuth2/JWT/SSO 生態最成熟 + JVM 級審計 |
| **限流 / 配額 / 多租戶** | Java (Resilience4j/Bucket4j) | 高並行下精細配額控制 |
| **API 閘道 / BFF / 路由** | Java Spring WebFlux | 非阻塞閘道，穩定吞大量並發 |
| **非同步 ingest 隊列** | Java + Kafka/RabbitMQ | 重解析卸載，保護 AI Core |
| **可觀測性（JVM 層）** | Java Micrometer/Prometheus | JVM metrics + OpenTelemetry 貫穿兩邊 |
| **文檔解析** | Python (Docling) | AI/ML 生態無可取替 |
| **向量檢索 / 重排序** | Python (LlamaIndex/Qdrant) | Python 主導 RAG 檢索引擎 |
| **多智能體編排** | Python (LangGraph) | agent 框架原生 Python |
| **LLM 生成 / 護欄** | Python | LLM SDK + prompt 生態最強 |

> ⚠️ **防過度工程提醒**：兩套 runtime 會增加 complexity。個人專題**先用純 Python 跑通 V1–V3**，到需要企業級安全、配額或 JVM 生態整合時先引入 Java 閘道（V4）。

---

## 🗺️ 六階段演進架構藍圖 (Python + Java 混合)

```
[第 1 階段：核心基礎 RAG、型別驗證與 API 閘道]
Docling / Tesseract ➔ 版面感知分塊 ➔ LangChain + Qdrant ➔ FastAPI + Pydantic ➔ LangSmith 追蹤除錯

                                      ▼

[第 2 階段：多模態轉錄、LlamaIndex 高級索引與混合搜尋]
Whisper 音視頻轉錄 ➔ LlamaIndex 層級索引 ➔ Qdrant 混合檢索 (Dense + BM25) ➔ RRF ➔ 兩級 Reranker ➔ JD 智能匹配

                                       ▼

[第 3 階段：LangGraph 自主 Agent 流程與 MCP 生態]
LangGraph 狀態機 (Self-RAG / Routing) ➔ FastMCP 伺服器 (Claude / Cursor) ➔ Docker & 雲端部署

                                       ▼

[第 4 階段：Java + Python 混合閘道 (Virtual Threads)]
Java 21 Spring Boot WebFlux (Virtual Threads) 邊界閘道 ➔ 安全 + 限流 ➔ Kafka 非同步 ingest ➔ REST/gRPC ➔ Python AI Core ➔ OpenTelemetry 追蹤

                                       ▼

[第 5 階段：多智能體混合聊天機器人 (MoA)]
LangGraph MoA：導演 ➔ 研究員 / 邏輯分析師 / 質疑者 / 解題者 ➔ 編碼專家團隊（可客製技能）➔ 模型路由 ➔ n8n / Dify 整合

                                       ▼

[第 6 階段：微調與蒸餾 (Nemotron-4)]
QLoRA 領域適配 ➔ Nemotron-4 獎勵模型 ➔ DPO/SteerLM 對齊 ➔ Minitron 蒸餾 ➔ RAGAS 把關發佈

```

---

## 📦 各版本技術棧與細部子步驟 (Tech Stack & Sub-steps)

### 🔹 第 1 階段：核心基礎 RAG、型別驗證與 API 閘道
專注於高品質跨格式文檔解析、嚴格資料型別契約、向量資料庫儲存、API 接口建構與端到端除錯觀測。

#### 技術棧 (Tech Stack)
* **文檔解析 (Parsing)**：`Docling` (IBM 開源視覺版面模型), `Tesseract OCR` (純掃描降級備援), `openpyxl`, `python-docx`
* **管線編排 (Orchestration)**：`LangChain` (v0.3+ / 1.x LCEL 表達式)
* **型別驗證 (Data Contracts)**：`Pydantic v2`
* **向量資料庫 (Vector Database)**：`Qdrant` (支援本機記憶體、本地磁碟持久化或 Qdrant Cloud 永久免費方案)
* **API 框架**：`FastAPI` + `uvicorn` (內置 Swagger UI `/docs` 測試介面)
* **觀測除錯 (Observability)**：`LangSmith`
* **環境與套件管理**：`uv`

#### 詳細步驟與子步驟 (Detailed Sub-steps)
* **Step 1.1: 多格式文檔解析與版面分析 (Document Ingestion & Parsing)**
  * `1.1.1 多格式讀取`：統一解析 PDF、PPTX、DOCX、XLSX、HTML、Markdown 與純文字。
  * `1.1.2 視覺版面分析 (Layout Analysis)`：識別多欄排版、閱讀順序與大綱標題層級 (H1/H2/H3)。
  * `1.1.3 表格結構化還原`：將簡歷與數據表格完整還原為 Markdown/HTML 表格語法，避免行列斷裂。
  * `1.1.4 圖像圖表關聯 (Visual Binding)`：提取專案投影片與作品集中的圖表，並自動綁定下方圖表說明文字 (Captions)。
* **Step 1.2: 結構感知分塊與元數據注入 (Layout-Aware Chunking & Metadata)**
  * `1.2.1 層級感知分塊`：依據大綱段落切分，確保切片保留所屬章節標題語意。
  * `1.2.2 原子區塊保護 (Atomic Chunking)`：確保表格、程式碼區塊與圖表描述不被硬切開。
  * `1.2.3 元數據標註 (Metadata Injection)`：為每一切片注入 `source_file`、`page_number`、`document_type`、`timestamp`。
* **Step 1.3: 向量化與 Qdrant 資料庫存儲 (Embedding & Vector Storage)**
  * `1.3.1 語意向量生成`：調用 `text-embedding-3-small` 生成 1536 維語意向量。
  * `1.3.2 Qdrant Collection 初始化`：設定 Cosine 相似度度量與 HNSW 索引參數。
  * `1.3.3 Payload 索引建立`：在 Qdrant 建立 Payload 索引，支援毫秒級 Metadata 條件過濾。
* **Step 1.4: 基礎檢索與問答管線 (Retrieval & Generation Pipeline)**
  * `1.4.1 Top-K 向量檢索`：利用 Cosine 相似度搜尋撈出最相關的前 K 個語意切片。
  * `1.4.2 系統提示詞工程 (System Prompting)`：設計具備個人檔案背景設定與防幻覺規則（Grounding Guardrails）的 Prompt。
  * `1.4.3 上下文拼接生成`：調用 `gpt-4o-mini` / `gpt-4o` 生成具備來源引用的嚴謹回答。
* **Step 1.5: Pydantic 嚴格驗證與 FastAPI 服務 (API Gateway)**
  * `1.5.1 請求與回應模式定義`：以 Pydantic 規範 `RAGRequest` 與 `RAGResponse`（保證型別邊界）。
  * `1.5.2 RESTful API 端點構建`：提供 `/query` (問答)、`/ingest` (文件入庫)、`/health` (健康檢查)。
  * `1.5.3 互動式 Swagger UI`：提供本機 `/docs` 視覺化測試介面，方便未來串接 Bot 或前端。
* **Step 1.6: LangSmith 觀測除錯與追蹤 (Observability & Tracing)**
  * `1.6.1 零侵入式追蹤配置`：透過環境變數自動捕獲每次檢索與 LLM 調用。
  * `1.6.2 Trace 瀑布圖分析`：在 LangSmith 後台檢視 Retrieval 準確度、Token 消耗與延遲瓶頸。

---

### 🔹 第 2 階段：多模態轉錄、LlamaIndex 高級索引與混合搜尋
專注於擴展輸入維度至音視頻、引入 LlamaIndex 專精的檢索優化索引、Qdrant 雙路混合搜尋與求職專屬評估。

#### 技術棧 (Tech Stack)
* **影音轉寫 (Transcription)**：`OpenAI Whisper` / `faster-whisper`, `ffmpeg-python`
* **進階索引 (Indexing)**：`LlamaIndex` (`llama-index-core`, `llama-index-readers-docling`, `llama-index-vector-stores-qdrant`)
* **向量與稀疏存儲**：`Qdrant` (Dense 密集向量 + Sparse BM25 / SPLADE 稀疏向量)
* **重排序 (Reranker)**：`flashrank` 或 `BAAI/bge-reranker-large` (Cross-Encoder)
* **求職適配引擎**：客製化 Python 技能比對邏輯 + Pydantic 評分 Schema

#### 詳細步驟與子步驟 (Detailed Sub-steps)
* **Step 2.1: 多模態影音轉錄 (Multimodal Audio & Video)**
  * `2.1.1 影音音軌提取`：從作品示範影片（MP4/WebM）或面試錄音中分離高音質音訊。
  * `2.1.2 帶時間戳記語音轉寫 (Timestamped Transcription)`：利用 Whisper 將語音轉為文字並標記時間點。
  * `2.1.3 多模態切片入庫`：將轉寫內容關聯至對應專案節點，保留時間戳 metadata。
* **Step 2.2: LlamaIndex 高級檢索架構 (Advanced Indexing Engine)**
  * `2.2.1 句子視窗檢索 (Sentence-Window Retrieval)`：以單句為單位做向量索引，檢索時自動擴展前後 3-5 句 Context Window。
  * `2.2.2 父子節點檢索 (Parent-Child / Hierarchical Node Parsing)`：以小切片（Child）精準搜尋，命中後返回完整段落（Parent）。
* **Step 2.3: 雙路混合檢索與重排序 (Hybrid Search & Reranking)**
  * `2.3.1 稀疏向量生成 (Sparse Lexical Vector)`：建立 BM25 關鍵字統計權重（專門鎖定公司名、技能縮寫、工具版本號）。
  * `2.3.2 雙路互惠排名融合 (Reciprocal Rank Fusion - RRF)`：由 Qdrant 原生結合語意與關鍵字搜尋結果。
  * `2.3.3 Cross-Encoder 重排序 (Reranking)`：將初步撈出的 Top-20 片段透過 Reranker 重新深度打分，篩選出最精確的 Top-5。
* **Step 2.4: 專屬求職匹配與評估模組 (Automated Job Matching)**
  * `2.4.1 JD 職缺結構化解析`：提取 JD 中之必備技能、加分項、工作年資與職責。
  * `2.4.2 技能落差矩陣計算 (Skill Gap Matrix)`：對比個人知識庫，標記強項與不足。
  * `2.4.3 客製化履歷論述建議`：針對目標職缺生成符合 STAR 原則的經歷描寫建議。

---

### 🔹 第 3 階段：LangGraph 自主 Agent 流程與 MCP 生態
專注於自主工作流、自我評估修正，並開放標準化 MCP 協議供外部客戶端無縫調用。

#### 技術棧 (Tech Stack)
* **Agent 狀態機**：`LangGraph` (StateGraph、條件分支路由、循環思考、Human-in-the-loop)
* **開放協議 (MCP)**：`FastMCP` / `mcp` SDK (Anthropic Model Context Protocol 官方標準)
* **容器化與雲端部署**：`Docker`, `Docker Compose`, `Fly.io` / `Render` / `Hugging Face Spaces`

#### 詳細步驟與子步驟 (Detailed Sub-steps)
* **Step 3.1: LangGraph 自主決策狀態機 (Agentic Workflow Engine)**
  * `3.1.1 系統狀態定義 (State Schema)`：維護對話歷史、使用者意圖、檢索文檔、重試次數與評分。
  * `3.1.2 意圖動態路由 (Query Routing Node)`：自動判斷當前問題是詢問履歷、分析 JD、還是閒聊。
  * `3.1.3 自我反思與查詢重寫 (Self-RAG Reflection)`：若檢索內容相關性評分過低，自動修改搜尋詞重新檢索。
  * `3.1.4 幻覺校驗節點 (Hallucination Checker)`：驗證生成答案是否完全由檢索文檔支撐，否則退回重構。
* **Step 3.2: MCP (Model Context Protocol) 伺服器建構**
  * `3.2.1 MCP Tools 暴露`：將 RAG 檢索與 JD 配對封裝為標準 Tool（如 `search_profile`, `analyze_job_fit`）。
  * `3.2.2 MCP Resources 暴露`：將履歷原始文字、專案 Markdown 映射為可供外部讀取的 Resource。
  * `3.2.3 Client 串接配置`：提供 `claude_desktop_config.json` 與 Cursor 設定檔，實現即插即用。
* **Step 3.3: 容器化與雲端生產部署 (Production & Deployment)**
  * `3.3.1 多階段構建 Dockerfile`：優化映像檔大小，分離構建環境與執行環境。
  * `3.3.2 容器編排 (Docker Compose)`：一鍵啟動 FastAPI 服務與本機 Qdrant。
  * `3.3.3 雲端自動化部署`：將 API 與 MCP 服務部署至雲端，提供線上公開 Demo 與健康監控。

---

## 🛠️ 開發環境設定與快速啟動 (Quickstart)

### 必要前置環境
* **Python**: `3.11+`
* **套件管理工具**: [uv](https://docs.astral.sh/uv/)（極速 Python 環境管理器）
* **Qdrant**: 本機 Docker 或免費 [Qdrant Cloud](https://cloud.qdrant.io/) 叢集

### 1. 下載專案並安裝依賴
```bash
# 複製儲存庫
git clone https://github.com/Vincent-CLY/RAG-Backend.git
cd RAG-Backend

# 使用 uv 同步安裝依賴環境
uv sync
```

### 2. 配置環境變數
複製範本檔案並填入你的 API 金鑰：
```bash
cp .env.example .env
```
請確保填入以下必要變數：
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=http://localhost:6333
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=rag-backend
```

### 3. 本機啟動 Qdrant (如使用雲端則可略過)
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### 4. 啟動 FastAPI 伺服器
```bash
uv run uvicorn main:app --reload --port 8000
```
打開瀏覽器訪問 `http://localhost:8000/docs` 即可透過 Swagger 互動介面測試 RAG 檢索與問答！

---

## 📖 核心技術解析與架構決策筆記

想了解背後的技術原理同選型原因？
👉 請閱讀完整技術筆記 [**架構筆記與專業名詞字典 (NOTES.md)**](./NOTES.md)，入面深入拆解：
* RAG 完整管線（端到端 Pipeline）深度圖解。
* 傳統搜尋 vs 向量搜尋 vs 混合檢索 (Hybrid Search) vs 重排序 (Reranker)。
* Docling 版面感知分塊與 LlamaIndex 句子視窗分塊的黃金搭檔配合。
* 「LlamaIndex + Qdrant + LangGraph」業界最強組合的職責邊界分工。
* 為非本科學習者準備的 AI 開發者名詞速查字典。

---

## 📄 專案授權
本專案採用 [MIT License](LICENSE) 開源授權。

