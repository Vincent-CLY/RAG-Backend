# 🧠 RAG & AI Engineering Knowledge Base (技術名詞、架構決策與學習筆記)

[ [English README](./README.md) ] | [ [繁體中文 README](./README.zh-HK.md) ]

本文件專為**從零邁向現代 AI 工程師 (Modern AI Engineer)** 的學習者設計。詳細解構檢索增強生成 (RAG)、向量檢索、多模態處理、自主代理 (Agentic Workflows) 以及 MCP 協議的核心概念、底層數學直覺與專案技術選型決策（Architecture Decision Records - ADR）。

---

## 📑 目錄 (Table of Contents)

1. [為什麼需要 RAG？大語言模型的致命局限](#1-為什麼需要-rag大語言模型的致命局限)
2. [RAG 全管線深度拆解 (End-to-End Pipeline)](#2-rag-全管線深度拆解-end-to-end-pipeline)
3. [搜尋技術大比拼：關鍵字搜尋 vs 向量搜尋 vs 混合檢索](#3-搜尋技術大比拼關鍵字搜尋-vs-向量搜尋-vs-混合檢索)
4. [切片的藝術：分塊 (Chunking) 與檢索 (Retrieval) 的分工與奧秘](#4-切片的藝術分塊-chunking-與檢索-retrieval-的分工與奧秘)
5. [Docling 與 LlamaIndex 的分塊有何本質區別？為什麼它們是絕配？](#5-docling-與-llamaindex-的分塊有何本質區別為什麼它們是絕配)
6. [架構決策與終極組合 (ADR: Architectural Decision Records)](#6-架構決策與終極組合-adr-architectural-decision-records)
   * [LlamaIndex + Qdrant + LangGraph 的黃金職責分離](#61-llamaindex--qdrant--langgraph-的黃金職責分離)
   * [為什麼選擇 Qdrant 而非 OpenSearch？](#62-為什麼選擇-qdrant-而非-opensearch)
   * [為什麼 V1 就要引入 FastAPI 與 Pydantic？](#63-為什麼-v1-就要引入-fastapi-與-pydantic)
   * [什麼是 LangSmith？為什麼說它是 AI 工程師的 X 光機？](#64-什麼是-langsmith為什麼說它是-ai-工程師的-x-光機)
   * [什麼是 MCP (Model Context Protocol)？](#65-什麼是-mcp-model-context-protocol)
   * [什麼是 OSS (開源軟件)？能否「白嫖」雲端免費額度？](#66-什麼是-oss-開源軟件能否白嫖雲端免費額度)
   * [2026 全球主流文檔 Parser 橫向大比拼 (Docling vs LlamaParse vs Marker 2 等)](#67-2026-全球主流文檔-parser-橫向大比拼)
   * [股票走勢圖、複雜圖表與多語言 (中/粵/日/英) 的最佳處理實務](#68-股票走勢圖複雜圖表與多語言-中粵日英-的最佳處理實務)
   * [Python + Java Virtual Threads 雙語混合架構（ADR）](#69-python--java-virtual-threads-雙語混合架構adr)
   * [Multi-Agent / Mixture-of-Agents 多智能體架構](#610-multi-agent--mixture-of-agents-多智能體架構)
   * [生產級加固：RAGAS 評估、快取、護欄與 HNSW 調優](#611-生產級加固ragas-評估快取護欄與-hnsw-調優)
   * [n8n / Dify 自動化工作流定位與整合](#612-n8n--dify-自動化工作流定位與整合)
   * [Nemotron-4 Instruct/Reward 微調與蒸餾進階路線](#613-nemotron-4-instructreward-微調與蒸餾進階路線v4)
7. [非專業人員必讀：AI 開發專用名詞速查字典](#7-非專業人員必讀ai-開發專用名詞速查字典)

---

## 1. 為什麼需要 RAG？大語言模型的致命局限

大語言模型（如 GPT-4o、Claude 3.5 Sonnet）雖然強大，但在企業與個人生產力場景中存在三大硬傷：

1. **知識截止期 (Knowledge Cutoff)**：LLM 的知識只停留在模型訓練完成那一刻，不知道你今天剛更新的履歷或昨天的股市。
2. **缺乏私有領域數據 (No Private Data Access)**：你的個人專案代碼、醫療紀錄、薪資合約未曾公開在網際網絡上，LLM 根本讀不到。
3. **幻覺問題 (Hallucination)**：LLM 本質是「下一個詞預測器（Next-Token Predictor）」，當被問及不知道的事物時，它傾向於「以極度自信的語氣編造看似合理的謊言」。

### 解決方案：RAG (Retrieval-Augmented Generation，檢索增強生成)
RAG 的核心思想非常簡單但極為有效：**「開卷考試」**。
在 LLM 回答問題前，系統先去你的私有資料庫（履歷、專案、筆記）檢索出與問題最相關的參考材料，然後把材料連同問題一起塞入 Prompt，要求 LLM **「僅依據以下提供的參考材料回答」**。
* **優點**：徹底解決幻覺問題、保護私有數據隱私、無需耗費數十萬美元重新微調（Fine-tuning）模型。

---

## 2. RAG 全管線深度拆解 (End-to-End Pipeline)

一個完整的 RAG 系統並非單純的「把文字塞給向量資料庫」，它由兩大核心流程組成：**離線數據入庫流程 (Offline Indexing)** 與 **在線查詢生成流程 (Online Generation)**。

### 📊 端到端流程圖解 (End-to-End Diagram)

```
【離線資料入庫階段 (Offline Ingestion & Indexing)】
多格式文檔 (PDF/PPT/Word/Excel/Images)
       │
       ▼ [1. 文檔解析 Document Parsing: Docling/Tesseract]
結構化 Markdown / HTML (保留表格、圖表與標題)
       │
       ▼ [2. 版面感知分塊 Layout-Aware Chunking]
結構切片 (Chunks with Metadata: 頁碼/章節/來源)
       │
       ▼ [3. 向量化 Embedding: text-embedding-3-small]
高維數值向量 (1536 維 Vector)
       │
       ▼ [4. 存入向量資料庫 Vector DB: Qdrant]
Qdrant 向量空間索引 (HNSW Graph + Payload Index)

--------------------------------------------------------------

【在線檢索生成階段 (Online Retrieval & Generation)】
使用者提問 (User Query)
       │
       ▼ [5. 查詢向量化 Query Embedding]
問題向量 (1536 維 Vector)
       │
       ▼ [6. 語意向量搜尋 / 混合檢索 (Hybrid Retrieval in Qdrant)]
Top-K 相關候選切片 (Candidate Chunks)
       │
       ▼ [7. 重排序 Reranking (Cross-Encoder: bge-reranker)]
Top-N 最精確上下文 (精準打分過濾)
       │
       ▼ [8. 提示詞注入 Prompt Augmentation]
System Prompt + 檢索材料 Context + 使用者提問
       │
       ▼ [9. LLM 推理生成 Generation: GPT-4o-mini]
具備來源引用的嚴謹回答 (Grounded Answer)
       │
       ▼ [10. 型別校驗與輸出 Pydantic Validation & FastAPI]
返回前端 / Bot (具備確定性契約)
```
---

## 3. 搜尋技術大比拼：關鍵字搜尋 vs 向量搜尋 vs 混合檢索

很多剛接觸 AI 的人以為「向量搜尋是萬能的」，這是極度危險的誤解。真正的工業級系統必然採用混合架構：

### 1. 傳統關鍵字搜尋 (Lexical / Keyword Search / BM25)
* **原理**：統計字詞出現頻率（TF-IDF / BM25 算法）。
* **優點**：**精確匹配無敵**。例如搜尋特有名詞、電話號碼、產品序號（如 `Error Code 404`）、人名（`Vincent`）、套件版本（`Python 3.11`）。
* **缺點**：**毫無語意理解**。
  * 搜尋「香港大學畢業生」，搜不到寫著「HKU Student」的簡歷。
  * 搜尋「手機」，搜不到「智能電話」。

### 2. 密集向量語意搜尋 (Dense Vector Search)
* **原理**：透過神經網路模型（如 `text-embedding-3-small`）將字句映射成一串高維浮點數陣列（如 1536 個維度）。語意越相近的字句，在多維幾何空間裡的**餘弦相似度 (Cosine Similarity)** 越高。
* **優點**：**能懂概念、同義詞、跨語言**。搜尋「機器學習專案」，能自動撈出包含「Deep Learning / PyTorch」的內容。
* **缺點**：**對專有名詞、字面精確度極度鈍感**。例如你搜尋「型號 A100-80G」，向量搜尋很可能把「V100-32G」也撈出來，因為在語意空間中它們都是「顯示卡」。

### 3. 混合檢索 (Hybrid Search: Dense + Sparse BM25)
* **原理**：**雙路召回**。一次查詢同時觸發兩條搜索：
  * 第 1 路：走 Qdrant 密集向量語意搜尋。
  * 第 2 路：走 Qdrant 稀疏向量 (Sparse BM25) 關鍵字搜尋。
* **融合機制 (Reciprocal Rank Fusion - RRF)**：將兩邊產生的排名列表以倒數權重加總評分，取出兩者兼備的最優交集。
* **結論**：**1 + 1 > 2**。既不怕專有名詞搜不到，又具備超強語意泛化能力！

### 4. 重排序 (Reranking / Cross-Encoder)
* **為什麼還需要 Reranker？**
  * 向量檢索（Bi-Encoder 架構）為了追求毫秒級速度，是「把 Query 和 Document 分開計算向量」，缺乏細部交互。
  * **Reranker (Cross-Encoder)** 則是把 `Query` 和 `Document` 拼在一起，同時送進 Transformer 模型的每一層注意力機制深度比對打分。
  * 雖然速度較慢，但只需要對初篩出來的前 20 條資料進行重新打分，就能把真正最相關的 3-5 條提到最前面，大幅減少 LLM 的 Token 浪費並提升答案準確度。

---

## 4. 切片的藝術：分塊 (Chunking) 與檢索 (Retrieval) 的分工與奧秘

### 分塊 (Chunking) 的本質矛盾
* **如果切太大（如 1500 字一塊）**：一塊裡面塞滿了多個不同主題，向量被「平均化（Diluted）」，導致語意檢索很難精確命中。
* **如果切太小（如 30 字一塊）**：語意非常單一精確，很容易被搜中；但是送進 LLM 時只有一句話，**缺乏上下文背景 (Context Fragmentation)**，LLM 根本不知道這句話在講誰。

### 檢索 (Retrieval) 的角色
檢索不是單純拿題目去算相似度，優秀的檢索系統包含：
1. **Metadata 篩選 (Filtering)**：在算向量前，先過濾 `category == 'resume'` 或 `year >= 2024`。
2. **多路檢索 (Multi-Retriever)**：結合向量與關鍵字。
3. **擴展檢索 (Contextual Compression / Windowing)**：搜出小核心，返回大視野。

---

## 5. Docling 與 LlamaIndex 的分塊有何本質區別？為什麼它們是絕配？

這是許多人最容易混淆的觀念：**「Docling 有分塊，LlamaIndex 也有分塊，到底差在哪裡？」**

### 1. Docling 的分塊：版面結構感知分塊 (Layout-Aware / Hierarchical Chunking)
* **層級**：**物理世界與視覺排版層級**。
* **它做的事**：Docling 不只是看字，它用視覺多模態模型辨識文件的「空間骨架」：
  * **表格完整性 (Table Preservation)**：傳統切分器每 500 字切一刀，直接把一張包含 10 個欄位的專案經歷表腰斬成兩半，下半截完全沒有欄位標題。Docling 會將整張表格識別為一個獨立的原子區塊 (Atomic Block)。
  * **圖文綁定 (Figure-Caption Binding)**：投影片中的架構圖往往上方是圖、下方是一行小字描述。Docling 會把這張圖的視覺描述與下方文字關聯在同一個 Chunk 中。
  * **標題繼承**：在子段落自動注入「第 2 章 > 專案架構」的層級標籤。

### 2. LlamaIndex 的分塊：檢索演算法優化分塊 (Retrieval-Optimized Chunking)
* **層級**：**向量數學與檢索算法層級**。
* **它做的事**：它接收已經被排版好的乾淨 Markdown/文字，設計特殊的資料結構來解決「精確度 vs 上下文」的矛盾：
  * **句子視窗檢索 (Sentence-Window Retrieval)**：
    * 向量庫只存單獨一句話（向量極度精準，容易被搜到）。
    * 當檢索命中該句子時，LlamaIndex 自動向前後「開窗」，抓取相鄰 3~5 句上下文一起送給 LLM。
  * **父子節點檢索 (Parent-Child / Hierarchical Node Parsing)**：
    * 切割出「小節點 (Child Chunks)」與「大節點 (Parent Chunks)」。
    * 向量搜尋只搜小節點，一旦搜中，系統自動返回它所屬的整篇父章節。

> 💡 **絕配結論**：
> **「Docling 負責把混亂的 PDF/PPT 變成結構完整、排版乾淨的文字；LlamaIndex 負責把這份乾淨文字建立最適合向量搜尋的父子/視窗索引。」**

---

## 6. 架構決策與終極組合 (ADR: Architectural Decision Records)

### 6.1 LlamaIndex + Qdrant + LangGraph 的黃金職責分離

為什麼不只用 LangChain？為什麼不只用 LlamaIndex？

| 元件 | 核心職責 | 為什麼選它？（不可替代性） |
| :--- | :--- | :--- |
| **Docling** | **物理排版解析 (Parser)** | 保留表格、圖表說明、多欄順序，杜絕 GIGO (Garbage In, Garbage Out)。 |
| **LlamaIndex** | **數據檢索引擎 (Retriever)** | 業界最強的 Node 索引機制（Sentence-Window / Parent-Child）。 |
| **Qdrant** | **高維度向量記憶庫 (Vector Store)** | 以 Rust 打造，極速、低內存佔用、原生支援 Dense + BM25 混合檢索，提供永久免費雲端叢集。 |
| **LangGraph** | **大腦指揮中心 (Agent Orchestration)** | 突破傳統線性鏈，提供基於狀態機（State Graph）的循環思考、條件分支、自我反思糾錯能力。 |
| **FastAPI** | **系統對外閘道 (API Gateway)** | 毫秒級異步吞吐量，透過 Pydantic 提供不可篡改的 API 契約與 Swagger `/docs` 調試介面。 |
| **LangSmith** | **全鏈路可觀測性 (Observability)** | X 光級監控，清晰追蹤 Prompt、Token 成本、檢索 Chunk 分數與執行延遲。 |
| **FastMCP** | **開放生態接口 (Standard Protocol)** | Anthropic 推出的開放協議，讓外部 AI 工具（Claude Desktop、Cursor）一鍵直連本系統。 |

### 6.2 為什麼選擇 Qdrant 而非 OpenSearch？
1. **資源消耗**：OpenSearch 是基於 Java 的重型全文搜尋引擎，至少需要 2GB~4GB RAM 才能穩定運行，對於個人開發與輕量伺服器是沉重的負擔。Qdrant 由 Rust 編寫，本機運行僅佔用數十 MB 內存，速度極快。
2. **混合檢索支援**：Qdrant 原生支援密集向量與 BM25 稀疏向量（Sparse Vectors），無需額外啟動 OpenSearch 即可完成雙路召回。
3. **免費託管**：Qdrant Cloud 提供永久免費 1GB 叢集，足以存儲個人作品集與數十萬字履歷數據。

### 6.3 為什麼 V1 就要引入 FastAPI 與 Pydantic？
1. **即時視覺化測試**：啟動 FastAPI 後即可直接在瀏覽器 `http://localhost:8000/docs` 進行互動式 Swagger 測試，無需每次改 code 跑命令列。
2. **型別安全與防禦性程式設計**：Pydantic 保證無論 LLM 如何隨機輸出，送回給前端或使用者的 JSON 格式永遠符合預期，杜絕 `KeyError` 崩潰。
3. **為未來的 Bot 鋪路**：無論後續開發 Telegram Bot、Discord Bot 還是網頁前端，都只需發送 HTTP POST 請求至本服務。

### 6.4 什麼是 LangSmith？為什麼說它是 AI 工程師的 X 光機？
在傳統軟體工程中，我們可以用 `print()` 或 debugger 設中斷點；但在 RAG 系統中，如果 LLM 回答「我不知道」，你無法一眼看出：
* 是文件根本沒讀進去？
* 還是檢索步驟撈到了錯誤的段落？
* 還是 Prompt 寫得太嚴格抑制了回答？
* 還是超過了 Token 上限？

**LangSmith** 會將每一次請求的完整鏈路（Chain of Thought、檢索到的所有 Chunks 與相似度分數、Prompt 最終拼接模樣、模型響應耗時與 Token 費用）以視覺化瀑布圖呈現，讓除錯變得如同照 X 光一樣透明無所遁形。

### 6.5 什麼是 MCP (Model Context Protocol)？
**Model Context Protocol (MCP)** 是由 Anthropic 開源的通用通訊協議，被譽為 **「AI 時代的 Type-C 傳輸線」**。
在 MCP 出現前，要讓 Claude 或 Cursor 讀取你的個人資料庫，你必須為每個客戶端單獨開發外掛或客製化腳本。
有了 MCP：
* 你的 RAG-Backend 只需實作成一個 **MCP Server**，對外公開 Tools（如 `search_profile`）與 Resources（如履歷 Markdown）。
* 任何支援 MCP 的工具（Claude Desktop、Cursor IDE 等）只要在設定檔填入 URL，就能**隨插即用**，直接在對話視窗中調用你的個人資料庫！


### 6.6 什麼是 OSS (開源軟件)？能否「白嫖」雲端免費額度？
* **OSS (Open Source Software)**：開源軟件，源代碼完全公開（例如 Docling, Marker, Linux）。可以在本地或個人服務器免費無限制運行，數據 100% 保存在自己手中，無需支付 API 費用。
* **白嫖雲端免費額度的可行性**：
  * **完全可行**！文檔解析 (Parsing) 與向量化 (Embedding) 屬於**一次性離線工作 (One-off Offline Task)**。
  * 只要在免費額度內解析完畢並寫入 Qdrant 向量數據庫，該資料就**永久可用**，後續線上提問 (Query) 只會讀取 Qdrant，不需再次調用昂貴的 Parser API。
  * **注意點**：保持輸出格式 (Markdown/JSON Schema) 的統一性，避免混合多個不同 Parser 產生的格式差異影響檢索。

### 6.7 2026 全球主流文檔 Parser 橫向大比拼

| 工具名稱 | 類型 | 準確度 (10分) | 複雜表格與圖表 | 多語言能力 (中/粵/日/英) | 免費額度 / 成本 | 適用場景 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Docling (IBM)** | **OSS 本地** | **9.5** | 🌟 極強 (TableFormer) | 🌟 極好 (多語言 OCR) | **完全免費，無限制** | **主力推薦：日常各類文檔與表格** |
| **LlamaParse** | **雲端 API** | **9.6** | 🌟 頂級 (視覺模型解析) | 🌟 頂級 (多語言語意) | **每日 1,000 頁免費** | **備援推薦：複雜圖表與高難度掃描件** |
| **Marker 2** | **OSS 本地** | 9.2 | 8.5 (排版優秀) | 良好 | **完全免費，無限制** | 學術論文、雙欄排版、數學公式 |
| **Mistral OCR** | 雲端 API | **9.7** | 🌟 頂級 (多模態 OCR) | 🌟 頂級 | 提供試用點數 (需綁卡) | 極端複雜文檔、極佳還原度 |
| **MarkItDown (MS)**| **OSS 本地** | 7.5 | 6.5 (基礎還原) | 良好 | **完全免費，極快** | 輕量純文字與簡易 Office 文件 |
| **Unstructured** | OSS / 雲端 | 8.0 | 7.5 | 良好 | OSS 免費 / API 試用 | 傳統企業流程自動化 |
| **Azure Doc Intel**| 企業雲端 | 9.5 | 🌟 發票/報表標竿 | 極好 | 每月 500 頁免費 | 商業發票、制式收據 |
| **Tesseract OCR** | **OSS 本地** | 5.0 | 2.0 (完全不懂排版) | 普通 (需裝語言包) | **完全免費** | **不推薦單獨作為 RAG 主力** |

### 6.8 股票走勢圖、複雜圖表與多語言 (中/粵/日/英) 的最佳處理實務
* **股票圖表與走勢圖痛點**：純文本 Parser 無法將折線圖與 K 線圖還原成數據表。
* **最佳工程解法 (Visual LLM Injection)**：
  1. 利用 Docling 或 LlamaParse 辨識出圖表區域，並提取圖例 (Legend) 與下方圖表標題說明 (Caption)。
  2. 調用輕量視覺大模型 (如  或本地開源  / ) 進行 3 句話摘要總結。
  3. 將該圖表摘要作為文本節點存入 Qdrant，並關聯原圖 metadata。
* **多語言處理 (中/粵/日/英)**：Docling 內置多語言 OCR 引擎，LlamaParse 底層由多模態大模型驅動，皆原生支援香港粵語口語字、繁簡中文與日文假名/漢字。

### 6.9 Python + Java Virtual Threads 雙語混合架構（ADR）

> 本節回答：「點樣用盡 Python 同 Java 嘅各自強項，做到生產級 RAG？」結論係**職責分離（Separation of Concerns）**，唔係用一種語言重寫另一種。

#### 🎯 核心原則：唔好為咗用 Java 而用 Java

* **Java Virtual Threads（Project Loom）** 係為了解決 **blocking I/O 高並行**。當你需要同時 fan-out 去多個下游服務（Python AI Core、資料庫、訊息佇列、LLM 供應商），而呢啲全部係阻塞式呼叫時，virtual thread 可以「每請求一條、block 得極平價」。
* **Python 嘅 `FastAPI` + `uvicorn` + `uvloop`**（async event loop）**已經解決咗大部份 I/O 並行問題**。對一部個人 RAG backend（幾百 QPS），Python 單體絕對夠。
* **過度工程警告**：兩套 runtime、兩套 build、序列化邊界會增加 complexity。個人專題**先 pure Python 跑通 V1**，Java 閘道當進階 / 需要同企業生態整合時先引入。但你**絕對應該學** virtual threads——佢係職場硬技能。

#### 🏗️ 雙語職責分工圖

```
外部 Client (Web / Bot / Claude Desktop / n8n / Dify)
        │
        ▼
╔═══════════════════════════════════════════════════════════╗
║  Java 21+ Spring Boot 3.3 (WebFlux / Virtual Threads)      ║  ← 控制平面 / 閘道層
║  • spring.threads.virtual.enabled=true                     ║
║  • Spring Security + JWT / OAuth2（認證授權）               ║
║  • 速率限制 / 配額 / 多租戶隔離 (Resilience4j / Bucket4j)   ║
║  • 請求路由 / API 組合 / BFF (Backend-for-Frontend)         ║
║  • WebClient 非阻塞 → 呼叫 Python AI Core                  ║
║  • Kafka / RabbitMQ 非同步 ingest 隊列                      ║
║  • Micrometer + Prometheus + Grafana + OpenTelemetry       ║
╚═══════════════════════════════════════════════════════════╝
        │  REST / gRPC（帶 W3C trace context 串聯兩邊 trace）
        ▼
╔═══════════════════════════════════════════════════════════╗
║  Python FastAPI — AI 核心 / Data Plane（async）            ║
║  • Docling 解析 → LlamaIndex / Qdrant 檢索                 ║
║  • Hybrid + Multi-query + HNSW + RRF + 兩級 Rerank         ║
║  • LangGraph Multi-Agent（見 6.10）                        ║
║  • LLM 生成 + Guardrails                                   ║
╚═══════════════════════════════════════════════════════════╝
        │
        ▼
  Qdrant (向量) + PostgreSQL (metadata/state) + Redis (cache/queue)
```

#### 📋 職責分工表（邊個語言管邊部分）

| 關注點 | 語言 / 技術 | 點解係佢？ |
| :--- | :--- | :--- |
| **認證授權 / 安全** | Java Spring Security | 企業級 OAuth2/JWT/SSO 生態最成熟，JVM 級安全審計 |
| **速率限制 / 配額 / 多租戶** | Java（Resilience4j/Bucket4j） | 高並行下需要精細配額控制，virtual threads 輕鬆 fan-out |
| **API 閘道 / BFF / 路由** | Java Spring WebFlux | 非阻塞閘道，穩定吞大量並發連接 |
| **非同步 ingest 隊列** | Java + Kafka/RabbitMQ | 重解析任務卸載，保護 AI Core 不被打爆 |
| **可觀測性（JVM 層）** | Java Micrometer/Prometheus | JVM metrics + OpenTelemetry trace 貫穿兩邊 |
| **文檔解析** | Python（Docling） | AI/ML 生態無可取替 |
| **向量檢索 / 重排序** | Python（LlamaIndex/Qdrant） | Python 主導 RAG 檢索引擎 |
| **Multi-Agent 編排** | Python（LangGraph） | agent 框架原生 Python |
| **LLM 生成 / Guardrails** | Python | LLM SDK、prompt 工程生態最強 |

#### 💻 代碼範例

**Java 端（Virtual Threads 閘道，非阻塞 fan-out 去 Python）：**

```java
// application.yml — Spring Boot 3.2+ 一行啟用虛擬線程
// spring.threads.virtual.enabled=true

@RestController
@RequestMapping("/api/v1")
class RagGatewayController(private val aiCoreClient: WebClient) {

    // 每個請求跑在一條 virtual thread 上：可「阻塞式」寫法，
    // 卻擁有海量並行吞吐，適合同時呼叫多個下游。
    @PostMapping("/query")
    fun query(@Valid @RequestBody req: RagRequest): Mono<RagResponse> =
        aiCoreClient.post()
            .uri("/query")
            .bodyValue(req)                       // 轉發到 Python AI Core
            .retrieve()
            .bodyToMono(RagResponse::class.java)
            .timeout(Duration.ofSeconds(30));     // 韌性：超時保護
}

// 手動起虛擬線程（舊版 Spring 或非 Web 場景）：
// Thread.startVirtualThread(() -> heavyBlockingIoCall());
```

**Python 端（AI Core 接收閘道轉發，trace context 貫穿）：**

```python
# app/ai_core.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from opentelemetry import trace

app = FastAPI(title="RAG AI Core")

class RagRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)

class RagResponse(BaseModel):
    answer: str
    citations: list[str]

@app.post("/query", response_model=RagResponse)
async def query(req: RagRequest) -> RagResponse:
    # 從 W3C traceparent header 接上 Java 端嘅 trace，兩邊 log 串聯
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("rag.retrieve_and_generate"):
        # 1) hybrid retrieve  2) rerank  3) generate（詳見 6.11）
        ...
        return RagResponse(answer="...", citations=[...])
```

#### 📖 新增名詞速記

| 名詞 | 白話解釋 |
| :--- | :--- |
| **Virtual Thread** | Java 嘅「輕量分身」。傳統一條 OS thread 佔 1MB，virtual thread 只佔幾百 bytes，可開幾百萬條，專治 blocking I/O 高並行。 |
| **WebFlux** | Spring 嘅非阻塞 web 框架，配合 WebClient 做高效能閘道。 |
| **BFF** | Backend-for-Frontend，為前端量身打包資料嘅中間層，負責路由、組裝、安全。 |
| **Fan-out** | 一個請求同時撒去多個下游服務，再聚合結果——virtual thread 最擅長。 |
| **Trace Context** | 跨服務嘅「快遞單號」（W3C 標準），令 Java 同 Python 兩邊嘅 log 串成一條鏈。 |

---

### 6.10 Multi-Agent / Mixture-of-Agents 多智能體架構

> 你腦入面嗰個 chatbot（researcher / logic analyst / challenger / solver / coding experts）就係經典嘅 **Multi-Agent Debate / Mixture-of-Agents (MoA)** 模式。`LangGraph` 係實現佢嘅最佳工具。

#### 🎯 鐵律：先用單一強 Model，再上 MoA

* **V1 永遠先用單一強 model**（gpt-4o-mini / claude-sonnet / qwen）。**先證明「好 retrieval + 好 prompt + 單 agent」已經夠好**，再上 multi-agent。
* 九成問題「單 agent + 好 RAG」就解決。MoA 係為咗應付**需要多角度推理、互相質疑、專業分工**嘅難題。
* ⚠️ **代價**：MoA 多次 LLM 調用 = **貴 + 慢**。必須配 **self-consistency、verifier node、early stopping、LangSmith observability** 先睇到邊個 agent 有問題。

#### 🤖 MoA 角色分工

| 角色 | 職責 | 建議模型 |
| :--- | :--- | :--- |
| **Orchestrator（導演）** | 拆解問題、分派任務、控制流程 | 強 model |
| **Researcher** | 調 RAG 檢索、收集證據 | 平價 model |
| **Logic Analyst** | 推理、驗證邏輯一致性 | 中強 model |
| **Challenger（紅隊/質疑者）** | 攻擊假設、找漏洞、防幻覺 | 強 model |
| **Solver / Optimist** | 綜合出最終答案 | 最強 model |
| **Coding Experts Team** | 專門 coding agents + tool calling，可**客製 agent skills** | 專用 coding model |

* **Model routing（模型路由）**：researcher 用平 model，challenger/solver 用強 model → 大幅節省成本。

#### 🔄 控制流程圖（LangGraph StateGraph）

```
START
  │
  ▼
Orchestrator（拆題 + 分派）
  │
  ├──────────────┬──────────────┐
  ▼              ▼              │
Researcher    Logic Analyst     │
(RAG 檢索)    (推理驗證)         │
  │              │              │
  └──────┬───────┘              │
         ▼                      │
     Challenger ◄────────────────┘   （強 model：質疑 + 防幻覺）
     (紅隊挑戰)
         │
         ▼
     Solver / Optimist          （綜合出答案）
     (最強 model)
         │
         ▼
      Verifier ──── 唔達標 loop 回 Challenger
         │
         達標
         ▼
        END

  ＋ Coding Experts Team（specialized agents + tool calling，可客製 skills）
```

#### 💻 代碼範例（LangGraph MoA 骨架）

```python
# app/moa.py
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# 1) 共享狀態：所有 agent 讀寫同一塊黑板
class MoAState(TypedDict):
    question: str
    research: str          # Researcher 寫入
    logic_check: str       # Logic Analyst 寫入
    critique: str          # Challenger 寫入
    answer: str            # Solver 寫入
    passed: bool           # Verifier 判定

# 2) model routing：平/強 model 分工省錢
cheap = ChatOpenAI(model="gpt-4o-mini")
strong = ChatOpenAI(model="gpt-4o")

def orchestrator(state: MoAState) -> MoAState:
    return state  # 拆題邏輯可在此展開

def researcher(state: MoAState) -> MoAState:
    # 調 RAG 檢索 → 用平價 model 摘要
    state["research"] = cheap.invoke(f"檢索並總結：{state['question']}").content
    return state

def logic_analyst(state: MoAState) -> MoAState:
    state["logic_check"] = cheap.invoke(f"驗證邏輯：{state['research']}").content
    return state

def challenger(state: MoAState) -> MoAState:
    # 紅隊：專門找漏洞（強 model）
    state["critique"] = strong.invoke(
        f"請質疑以下論述的漏洞與幻覺：{state['research']}"
    ).content
    return state

def solver(state: MoAState) -> MoAState:
    state["answer"] = strong.invoke(
        f"綜合研究、邏輯與質疑，給出穩妥答案：{state}"
    ).content
    return state

def verifier(state: MoAState) -> str:
    # 唔達標就 loop 回 challenger 再打磨
    return END if state["passed"] else "challenger"

# 3) 組裝狀態圖
g = StateGraph(MoAState)
g.add_node("orchestrator", orchestrator)
g.add_node("researcher", researcher)
g.add_node("logic_analyst", logic_analyst)
g.add_node("challenger", challenger)
g.add_node("solver", solver)
g.add_edge(START, "orchestrator")
g.add_edge("orchestrator", "researcher")
g.add_edge("researcher", "logic_analyst")
g.add_edge("logic_analyst", "challenger")
g.add_edge("challenger", "solver")
g.add_conditional_edges("solver", verifier)   # loop 控制
app = g.compile()
```

#### 📖 新增名詞速記

| 名詞 | 白話解釋 |
| :--- | :--- |
| **Mixture-of-Agents (MoA)** | 多個專家 agent 接力答同一題，再綜合出更強答案——好似「團審」代替「獨審」。 |
| **Orchestrator** | 導演／指揮官，負責拆題同分派，自己通常唔做苦功。 |
| **Red Team / Challenger** | 專門唱反調嘅 agent，負責攻擊假設、逼出漏洞，係防幻覺嘅煞車。 |
| **Self-consistency** | 同一題問幾次取多數決，降低偶發錯誤。 |
| **Verifier** | 把關裁判，答案唔合格就打回重做（形成 loop）。 |
| **Model Routing** | 按任務難度派唔同模型——粗活用平價、精活用強模型，慳錢。 |

---

### 6.11 生產級加固：RAG Pipeline 升級、RAGAS 評估、快取、護欄與 HNSW 調優

> 你原本嘅 pipeline（**hybrid search + multi-query + HNSW + RRF + 最後 production rerank**）已經相當 production 級。以下係可以再升級嘅 8 個方向。

#### 🚀 Pipeline 升級清單

| 升級項 | 原理 | 帶來咩好處 |
| :--- | :--- | :--- |
| **HyDE** | 先用 LLM 生成一條「假設性答案」，再攞佢去檢索（而唔係用原始問題） | 縮短問題與文檔嘅語意距離，顯著提升召回率 |
| **Step-back Prompting** | 把具體問題抽象成一條更上位的問題再檢索 | 搵到更廣嘅背景知識 |
| **Multi-query Expansion** | 一個問題自動擴成 3-5 個變體一起檢索（你已有） | 覆蓋更多表述方式 |
| **Self-RAG / Agentic** | 檢索後自我評分，低分就 rewrite query 重檢索 | 自動修復檢索失敗 |
| **Contextual RAG（Anthropic）** | 為每個 chunk 預生成一段上下文摘要再嵌入 | 大幅提升檢索準確度（業界熱門） |
| **兩級 Rerank** | 第一級輕量（flashrank/bge-base 快），第二級 cross-encoder / ColBERT / LLM-as-reranker | 兼顧速度與精度 |
| **RRF → 加權/learned fusion** | 由單純 RRF 升級為按資料分佈學習權重 | 融合更精準 |
| **Metadata pre-filtering** | 算向量前先過濾 時間/類型/權限 | multi-tenant 必備、提速 |

#### 🏗️ 進階 RAG 全流程圖

```
User Query
   │
   ├─→ [Query Rewrite]  HyDE / Step-back / Multi-query
   │
   ├─→ [Metadata Pre-filter]  category / year / 權限
   │
   ├─→ [Hybrid Recall]  Dense (HNSW) ∥ Sparse (BM25)
   │
   ├─→ [RRF Fusion]  雙路排名融合 → Top-20
   │
   ├─→ [Stage-1 Rerank]  flashrank (快) → Top-10
   │
   ├─→ [Stage-2 Rerank]  cross-encoder / ColBERT → Top-5
   │
   ├─→ [Self-RAG Check]  相關性過低？→ 回 Query Rewrite
   │
   ├─→ [Contextual Augment]  注入 chunk 上下文
   │
   ├─→ [Semantic Cache 命中？]  Redis 直接返回，慳錢
   │
   ▼
[LLM Generate + Guardrails]  →  Grounded Answer + Citations
```

#### 💻 代碼範例（兩級 Rerank + HyDE 概念骨架）

```python
# app/advanced_rag.py
from flashrank import Ranker, RerankRequest

# Stage-1：輕量 reranker（毫秒級）
stage1 = Ranker(model_name="ms-marco-MiniLM-L-12-v2")

def two_stage_rerank(query: str, candidates: list[str]) -> list[str]:
    # Stage-1：flashrank 快速收窄
    r1 = stage1.rerank(RerankRequest(query=query, passages=candidates))
    top10 = [p["text"] for p in r1[:10]]
    # Stage-2：交給更強嘅 cross-encoder / ColBERT（示意，省略載入）
    top5 = cross_encoder_rerank(query, top10)  # 你的精排模型
    return top5

def hyde_query(question: str, llm) -> str:
    # 先用 LLM 生一條假設性答案，攞佢去檢索
    hypo = llm.invoke(f"請生成一段能回答此問題的假設段落：{question}").content
    return hypo  # 把 hypo 向量化去 Qdrant 檢索
```

#### 📏 RAGAS 評估（生產必備）

唔可以靠感覺判斷 RAG 好壞，要用 **RAGAS** 框架量化：

| 指標 | 衡量咩 |
| :--- | :--- |
| **Faithfulness（忠實度）** | 答案有幾忠於檢索到嘅 context（防幻覺） |
| **Answer Relevancy（答案相關度）** | 答案有幾切題 |
| **Context Precision（上下文精確度）** | 撈返嚟嘅 chunk 有幾精準 |
| **Context Recall（上下文召回率）** | 相關資料有幾被撈齊 |

```python
# app/eval.py —— 離線 eval set 量化 RAG 質素
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

data = Dataset.from_list([
    {"question": "我嘅畢業院校係？", "answer": ans,
     "contexts": ctxs, "ground_truth": "香港大學"},
])
result = evaluate(data, metrics=[faithfulness, answer_relevancy,
                                 context_precision, context_recall])
print(result)   # 每次改 prompt/模型後跑一次，防止退化
```

#### ⚡ 其他生產加固

* **Semantic Cache（語意快取）**：相似問題命中 Redis 就直接返回，慳 LLM 錢、降延遲。
* **Guardrails（護欄）**：用 NeMo Guardrails / Guardrails AI 防 prompt injection、PII 洩漏、越界回答。
* **HNSW 調優 + Quantization**：調 `m` / `ef_construct` / `ef_search`；加 scalar/binary quantization 大幅省記憶體。

#### 📖 新增名詞速記

| 名詞 | 白話解釋 |
| :--- | :--- |
| **HyDE** | 先叫 AI 作個「假答案」，再用假答案去搜尋——往往搜到真料。 |
| **Self-RAG** | 檢索完自己評分，唔合格就自己改題目重搜，一條龍自我修復。 |
| **Contextual RAG** | 為每塊資料預先補一句上下文，令佢「單拎出嚟都讀得明」。 |
| **ColBERT** | 一種「遲交互」檢索，比純向量準、比 cross-encoder 快。 |
| **RAGAS** | RAG 專用「考試評分器」，量化答案有幾忠實、有幾切題。 |
| **Semantic Cache** | 語意快取——問題「差不多」就直接拎舊答案，唔使再問 AI。 |
| **Guardrails** | 安全護欄，防止用戶用惡意 prompt 攻擊或套取敏感資料。 |

---

### 6.12 n8n / Dify 自動化工作流定位與整合

> 核心原則：**核心 RAG / Agent 用自己嘅 Python/Java 代碼**（要 control + 客製 skills + scale）；**n8n 做自動化 glue**；**Dify 做原型 / 內部工具 / 實驗場**。三者並存，唔係二選一。

#### 🧩 三者定位對比

| 工具 | 定位 | 適合場景 | 唔適合 |
| :--- | :--- | :--- | :--- |
| **你的 Python/Java 代碼** | 生產主幹 | 核心 RAG、MoA agent、客製 skills、要 scale、要完全控制 | 快速 demo |
| **n8n** | 自動化 glue | ingest 觸發、cron 抓 JD、通知、webhook 串接、非工程同事用 | 複雜 agent 編排 |
| **Dify** | 低代碼 LLMOps 平台 | 快速原型、內部自助工具、model 實驗、非工程同事 | 深度客製、大規模生產（封裝死、scale 受限） |

#### 🔗 整合模式（並存示意圖）

```
         ┌─────────────────────────────────────────┐
         │           你的 Production Stack           │
         │   Java 閘道 → Python AI Core (LangGraph)  │  ← 核心，寫 code
         │   MoA chatbot + 客製 agent skills         │
         └──────────────────┬──────────────────────┘
                            │ 暴露 REST API
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
          [ n8n ]        [ Dify ]       [ Claude/Cursor ]
        (排程 ingest、   (原型、內部     (MCP 直連)
         通知、webhook)   自助工具)
```

#### 💻 整合代碼概念

```python
# 1) n8n / Dify 作為 client 呼叫你嘅 AI Core（你開放 REST API 就得）
#    n8n HTTP Request Node → POST http://ai-core/query
#    Dify Custom Tool → 填你嘅 OpenAPI schema

# 2) n8n 排程觸發 ingest（cron 每日抓 JD）
#    n8n Cron Node → HTTP 抓 JD 網頁 → POST /ingest 到你嘅 Python Core

# 3) 你嘅核心只暴露乾淨 API，邊個嚟調都歡迎：
from fastapi import FastAPI
app = FastAPI()

@app.post("/query")     # n8n / Dify / Web / Bot 共用
async def query(req: dict): ...
```

#### 📖 名詞速記

| 名詞 | 白話解釋 |
| :--- | :--- |
| **n8n** | 通用自動化工具（視覺化拉線），專門「事件觸發」串起唔同服務。 |
| **Dify** | 低代碼 LLM 應用平台，視覺化拼 RAG/agent，啱快速 demo 同非工程同事。 |
| **LLMOps** | 專注 LLM 應用嘅開發／部署／監控運維實踐。 |

---

### 6.13 Nemotron-4 Instruct/Reward 微調與蒸餾進階路線（V4+）

> ⚠️ **定位**：呢個係**研究級 / 重 GPU 任務**，放去 roadmap 後期。個人專題**先做好 retrieval + agent**，先唔好一上來就燒錢燒卡。

#### 🎯 NVIDIA Nemotron 方法論

* **`Llama-3.1-Nemotron-70B-Instruct`**：NVIDIA 微調過嘅強基座模型。
* **`Nemotron-4 340B Reward`**：獎勵模型（Reward Model），用嚟評分答案好壞。
* **`HelpSteer2`**：高質素偏好資料集。
* **`NeMo Aligner`**：對齊訓練框架，支援 **SteerLM / RLAIF / DPO**。

#### 🔬 典型流程

```
Base Model
   │
   ▼ [SFT：用 Nemotron-4 340B Instruct 生成 instruction data]
Instruct Model
   │
   ▼ [Reward Model：Nemotron-4 340B Reward 評分]
   │
   ▼ [SteerLM / DPO 對齊]
Aligned Model
   │
   ▼ [蒸餾 Distill：Minitron / knowledge distillation 壓縮]
小模型 (7-8B) 用於部署
```

#### 💡 對個人專題嘅務實建議

* **一上來唔好碰 70B SFT**（要幾張 A100/H100）。
* 先用 **QLoRA** fine-tune 細 model（7-8B）做 **domain adaptation**（例：粵語語氣、特定輸出格式）——一張消費級卡就得。
* distill 用 **Minitron（prune + distill）** 壓縮，兼顧質素同部署成本。
* 放去 **V4+**，等 RAG + MoA 穩定、有明確質素指標（RAGAS）之後，先知要微調咩。

#### 📖 名詞速記

| 名詞 | 白話解釋 |
| :--- | :--- |
| **SFT** | Supervised Fine-Tuning，用「問題-答案」樣本教模型聽話。 |
| **Reward Model** | 專門打分嘅模型，話知答案「有幾好」，用嚟訓練更強模型。 |
| **DPO** | Direct Preference Optimization，直接用好／壞答案配對訓練，較省。 |
| **RLAIF** | 用 AI 反饋代替人標註嘅對齊方法。 |
| **QLoRA** | 慳記憶體微調法，一張細卡都能微調大模型。 |
| **Distillation（蒸餾）** | 叫大模型「教」細模型，令細模型學到大模型本事但跑得快。 |
| **Minitron** | NVIDIA 剪枝 + 蒸餾組合，壓縮模型保質素。 |

---


## 7. 非專業人員必讀：AI 開發專用名詞速查字典

這裡用最平實的大白話與日常生活比喻，為你解釋面試與開發時常聽到的高深名詞：

| 專用名詞 | 英文術語 | 生活化通俗解釋 |
| :--- | :--- | :--- |
| **詞嵌入 / 向量** | **Embedding / Vector** | **文字的數位身分證 / 思想座標**。電腦看不懂中文或英文，但懂數字。Embedding 模型把一句話轉化為 1536 個數字（座標）。意思越接近的話，在幾何空間中靠得越近。 |
| **餘弦相似度** | **Cosine Similarity** | **衡量兩句話有多像的角度規**。取值在 -1 到 1 之間。如果兩句話夾角為 0 度（餘弦值為 1），代表兩句話語意完全一致；夾角 90 度代表毫不相關。 |
| **分塊** | **Chunking** | **把整本書切成小便利貼**。因為 LLM 一次讀不完整本書，必須切成易於檢索的小塊。 |
| **元數據** | **Metadata / Payload** | **便利貼背後的標籤備註**。例如這張便利貼出自哪份文件、第幾頁、哪一年寫的、是工作經歷還是證照。可以用來做精確過濾。 |
| **幻覺** | **Hallucination** | **一本正經地胡說八道**。LLM 不知道答案時，根據語言機率編造出看似極為真實的假事實。 |
| **密集檢索** | **Dense Retrieval** | **懂意思但對字面不敏感的搜尋**。利用語意向量搜尋，懂「貓」和「小動物」相關。 |
| **稀疏檢索** | **Sparse Retrieval (BM25)** | **不管意思但字字必校的搜尋**。傳統關鍵字搜尋，精確匹配字串，人名和料號一字不差。 |
| **重排序** | **Reranking** | **決賽面試官**。向量搜尋像初試，海選挑出前 20 名；Reranker 是主考官，把前 20 名拿來一道一道題目仔細深究，選出最頂尖的 3-5 名。 |
| **提示詞注入 / 接地** | **Prompt Augmentation / Grounding** | **把參考書綁在考卷上**。在 Prompt 裡寫明「根據以下檢索到的個人資料回答，禁止憑空想像」。這叫 Grounding（腳踏實地）。 |
| **狀態機** | **State Graph (LangGraph)** | **有記憶、會走回頭路思考的決策大腦**。傳統程式是一條路走到底（Chain）；狀態機可以在發現答案不滿意時，退回上一步重新搜尋（Self-Correction 迴圈）。 |
| **模型上下文協議** | **MCP (Model Context Protocol)** | **AI 世界的通用 USB 插座**。定義了一套標準，讓外部的 AI 客戶端可以直接隨插即用調用你的資料庫。 |
| **可觀測性** | **Observability (LangSmith)** | **系統的行車記錄器兼黑盒子**。記錄每一次提問到底經過了哪些步驟、花多少錢、哪裡出錯。 |
| **確定性資料契約** | **Data Contract (Pydantic)** | **嚴格的進出口海關檢查**。保證傳進來和送出去的資料型別、長度、欄位絕對合格，不合格立即攔截報錯。 |
| **倒數排名融合** | **RRF (Reciprocal Rank Fusion)** | **公正的計分綜合法**。當語意搜尋給出排名，關鍵字搜尋也給出排名，RRF 透過數學倒數公式把兩張榜單綜合成一張最客觀的總排名榜單。 |
| **虛擬線程** | **Virtual Thread (Java Loom)** | **Java 嘅輕量分身**。傳統一條系統線程佔 1MB 記憶體，虛擬線程只佔幾百 bytes，可開幾百萬條，專治大量阻塞式 I/O 嘅高並行。 |
| **非阻塞 Web 框架** | **WebFlux (Java)** | **Spring 嘅高速閘道**。唔會一個請求卡住整條隊列，適合擋在最前面分流。 |
| **後端為前端** | **BFF (Backend-for-Frontend)** | **前線打包員**。為前端量身整理、組合、把關資料的中間層。 |
| **多智能體混合** | **Mixture-of-Agents (MoA)** | **團審代替獨審**。多個專家 AI 接力答同一題再綜合，答案更穩妥。 |
| **導演 / 指揮官** | **Orchestrator** | **唔做苦功嘅包工頭**。負責拆解問題、分派比邊個 agent 做，自己唔親自答題。 |
| **紅隊 / 質疑者** | **Challenger / Red Team** | **專門唱反調**。攻擊假設、逼出漏洞，係防幻覺嘅煞車皮。 |
| **假設性文檔嵌入** | **HyDE** | **先作個假答案去搜尋**。叫 AI 作條假答案，再用假答案搵真料，命中率更高。 |
| **自我反思檢索** | **Self-RAG** | **搜完自己驗貨**。檢索後自我評分，唔合格就改題目重搜，一條龍自我修復。 |
| **上下文增強檢索** | **Contextual RAG** | **每塊料補句前文**。為每塊資料預先補一句背景，單拎出嚟都讀得明。 |
| **RAG 評分器** | **RAGAS** | **RAG 專用考試官**。量化答案有幾忠實、有幾切題、撈料有幾精準，唔靠感覺。 |
| **語意快取** | **Semantic Cache** | **問題相近就拎舊答案**。慳 LLM 錢、降延遲，唔使重複問 AI。 |
| **安全護欄** | **Guardrails** | **安全帶同護欄**。防止惡意 prompt 攻擊、敏感資料外洩同越界回答。 |
| **監督式微調** | **SFT (Supervised Fine-Tuning)** | **用樣本教模型聽話**。用「問題-答案」樣本調整模型行為。 |
| **獎勵模型** | **Reward Model** | **專門打分嘅裁判**。話知答案有幾好，用嚟訓練更強模型。 |
| **量化低秩微調** | **QLoRA** | **慳記憶體微調法**。一張細顯卡都能微調大模型，個人玩家福音。 |
| **蒸餾** | **Distillation** | **叫大師教徒弟**。令大模型「教」細模型，徒弟跑得快又學到大師本事。 |


