# 🗺️ Project Chanakya: v2.0 Roadmap

## Mentorship Mode Rules
- **Mentee (User):** Designs the architecture, writes the code, proposes the file structure.
- **Mentor (AI):** Reviews, challenges, corrects worst-case bugs, proposes industry-standard improvements.

---

## ✅ v1.0 COMPLETE (Phases 0–10)
- [x] Multi-Agent LangGraph System (Scout, Scholar, Cartographer, Analyst, Strategist)
- [x] PostgreSQL Persistent Memory (Briefings, Entities, Locations)
- [x] APScheduler Autopilot (Running every 12 hours)
- [x] React War Room Dashboard (Map, Intel Feed, Entity Timeline, Scenario Cards)
- [x] Conversation Memory (Sliding Window + Summary)
- [x] Docker Compose Deployment
- [x] GitHub Open Source (github.com/Sai-Anirudh-333/project-chanakya)

---

## 🚀 v2.0 Roadmap: The Intelligence Engine (AI & Data Science Track)

We are pivoting from basic web development to building a DARPA-level intelligence engine. The focus is now entirely on advanced AI capabilities, knowledge graphs, and complex reasoning.

### Phase 11: The Knowledge Graph Foundation (Neo4j + GraphRAG)
**Goal:** Migrate from flat PostgreSQL entity tables to a Neo4j Graph Database to build true Knowledge Graphs (e.g., tracking "Company A -> Owns -> Company B").
**Mentee Architect Challenge:**
1. What is the fundamental difference between relational tables (SQL) and nodes/edges (Graph DB)?
2. How do you integrate Neo4j into the FastAPI backend alongside ChromaDB and Postgres?
3. How do we expand the `EntityExtractorAgent` to extract "Triplets" (Subject-Predicate-Object) instead of just single entities?
4. How do you write Cypher queries to uncover hidden connections (e.g., matching a defense contractor to a sanctioned individual)?

**Key Concepts To Learn:** Neo4j, Cypher, GraphRAG, Triple Extraction.

---

### Phase 12: Advanced RAG System (Scholar Agent 2.0)
**Goal:** Upgrade the `ScholarAgent` to read dense, unstructured military doctrines or treaties with extremely high accuracy, minimizing hallucination and lost context.
**Mentee Architect Challenge:**
1. Why is `RecursiveCharacterTextSplitter` insufficient for complex intelligence documents?
2. How do you implement **Semantic Chunking** using an embedding model to find natural breaks in the text?
3. What is **Small-to-Big Retrieval** (Parent-Child Chunks), and how does it balance search accuracy with LLM context?
4. How do you implement **Metadata Filtering (Self-Querying)** so an analyst can ask "Compare 2022 vs 2023 troop levels" without the Vector DB mixing the years?

**Key Concepts To Learn:** Semantic Chunking, Parent-Child Retrievers, Self-Querying, Re-ranking (Cross-Encoders).

---

### Phase 13: Temporal Reasoning & Event Sequence Analysis
**Goal:** Teach Chanakya to understand time and causality. Time is the most critical axis in intelligence.
**Mentee Architect Challenge:**
1. How do you build a **Time-Aware Knowledge Graph** where edges have `start_time` and `end_time` properties?
2. If Russia moves troops in Feb and sanctions hit in March, how does the system recognize the sequence?
3. How do you model "Sequence Decay" (older intel is less relevant than newer intel unless it is a foundational treaty)?

**Key Concepts To Learn:** Temporal Graphs, Time-Series Analysis on irregular events, Sequence Decay.

---

### Phase 14: Graph Neural Networks (GNNs) for Link Prediction
**Goal:** Move beyond what is *known* into what is *probable*. Given the structure of the Neo4j graph, mathematically predict if undocumented relationships exist.
**Mentee Architect Challenge:**
1. What is a Graph Neural Network, and how does it differ from a standard CNN or Transformer?
2. How do you use **PyTorch Geometric** on your Neo4j data?
3. How do you train a model to perform **Link Prediction** (e.g., predicting a hidden shell company network based on transaction patterns)?

**Key Concepts To Learn:** PyTorch Geometric, GNNs, Link Prediction, Structural Graph Properties.

---

### Phase 15: Causal Reasoning & Bayesian Inference
**Goal:** Distinguish between correlation and causation to evaluate the probability of escalation given conflicting intelligence reports.
**Mentee Architect Challenge:**
1. If the `ScoutAgent` reports X (60% confidence) and the `ScholarAgent` reports Y (80% confidence), how does the system fuse them into a single probability?
2. How do you construct **Causal Graphs (DAGs)** to run "What-If" counterfactuals (e.g., "If Israel had not struck facility X, would the retaliation have occurred?")?
3. Why do LLMs struggle with causal reasoning, and how do Bayesian Networks fix this?

**Key Concepts To Learn:** Bayesian Networks, Uncertainty Quantification, Directed Acyclic Graphs (DAGs), Causal Inference.

---

### Phase 16: End-Game Autonomy (Multi-Agent Swarms & Red Teaming)
**Goal:** Create autonomous, debating agents that simulate adversarial geopolitical scenarios.
**Mentee Architect Challenge:**
1. How do you structure a LangGraph workflow where one agent acts as "Red Team" (Adversary) and another as "Blue Team" (Defender)?
2. How do they simulate thousands of iterative moves to test a policy?
3. How do you apply **Monte Carlo Tree Search (MCTS)** to LangGraph workflows to let the system evaluate the best strategic path?

**Key Concepts To Learn:** Multi-Agent Debate, Red/Blue Teaming, Monte Carlo Tree Search (MCTS).

---

## 🌟 Future Vision (The Platform Track)
These features are parked for when we want to focus on web development, infrastructure, and deployment rather than core AI capabilities:

- **Real-Time WebSocket Feed:** Replace HTTP polling with real-time pushes.
- **Custom Standing Orders UI:** React forms to CRUD standing orders directly into PostgreSQL.
- **User Authentication:** JWT-based login to protect the War Room.
- **D3.js Graph Visualization:** A gravity-simulated interactive graph UI for the Neo4j backend.
- **Cloud Deployment:** Deploying the FastAPI backend to Render and Next.js frontend to Vercel (CI/CD).
- **Alert System:** Telegram/Discord bot notifications for high-urgency briefings.
