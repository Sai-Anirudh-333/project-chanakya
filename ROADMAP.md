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

## 🚀 v2.0 Roadmap

### Phase 11: Standing Orders UI
**Goal:** Let users CRUD their intelligence topics from the War Room UI — no code edits needed.
**Mentee Architect Challenge:**
1. What new PostgreSQL table(s) are needed for this?
2. What REST API endpoints does the backend need? (`GET`, `POST`, `DELETE`)
3. What does the React UI component look like? (A form? A modal? A sidebar panel?)
4. How does the scheduler dynamically pick up the new orders from the DB?

**Key Concepts To Learn:** REST CRUD, database-driven configurations, React state management.

---

### Phase 12: User Authentication (JWT)
**Goal:** Protect the War Room with a login screen. Store hashed passwords in PostgreSQL.
**Mentee Architect Challenge:**
1. What new `users` table schema do you need?
2. What is JWT? How does the frontend prove to FastAPI that the user is logged in?
3. Where do you store the JWT on the frontend - `localStorage` or a cookie? Why?
4. Which FastAPI endpoints should be protected? How do you protect them?

**Key Concepts To Learn:** Hashing (bcrypt), JWT tokens, Auth middleware, protected routes.

---

### Phase 13: Real-Time WebSocket Feed
**Goal:** Replace 15-second HTTP polling with an instant WebSocket push. The War Room updates the moment the Autopilot finishes a briefing.
**Mentee Architect Challenge:**
1. What is the difference between HTTP and WebSocket?
2. Where does the WebSocket channel get opened - in the Scheduler? In the `/api/chat` route? Somewhere else?
3. How does the React frontend "listen" for the push notification?
4. What happens if the frontend disconnects? How does the backend handle that?

**Key Concepts To Learn:** WebSocket protocol, FastAPI WebSocket, React `useEffect` cleanup, Connection management.

---

### Phase 14: Entity Knowledge Graph (Neo4j & D3.js)
**Goal:** Migrate from PostgreSQL to Neo4j to build true Knowledge Graphs, pushing beyond basic military intel into corporate, financial, and multi-domain OSINT (inspired by OSINTFramework). Replace the flat Entity Timeline with an interactive, force-directed D3.js graph showing deep entity-to-entity relationships.
**Mentee Architect Challenge:**
1. What is the fundamental difference between relational tables (SQL) and nodes/edges (Graph DB)?
2. How do you integrate Neo4j into the FastAPI backend alongside ChromaDB and Postgres?
3. How do we expand the Analyst Agent to track "Relationships" (e.g., "Company A -> Owns -> Company B") instead of just "Entities"?
4. How do you embed a gravity-simulated D3.js graph inside a Next.js component to visualize these connections?

**Key Concepts To Learn:** D3.js, SVG manipulation, graph data structures (nodes + edges), co-occurrence matrices.

---

### Phase 15: Alert System (Telegram Bot)
**Goal:** When the Autopilot generates a high-urgency briefing (containing keywords like "retaliation", "ceasefire", "mobilization"), push a Telegram notification.
**Mentee Architect Challenge:**
1. How do you create and register a Telegram Bot?
2. How does the Synthesizer Agent detect "urgency" in its output?
3. Where in the LangGraph pipeline does the Telegram notification get triggered?
4. How do you prevent the bot from spamming you if the Autopilot runs twice a day?

**Key Concepts To Learn:** Telegram Bot API, LLM keyword extraction, Webhook vs polling for Telegram.

---

### Phase 16: Cloud Deployment (Vercel + Render)
**Goal:** Deploy the live project to the internet so anyone with a URL can access the War Room.
- Frontend → **Vercel** (Free Tier)
- Backend + Database → **Render** (Free Tier / $7/month for always-on)
- Set up GitHub CI/CD so every `git push` auto-deploys.

**What will need to change before deployment:**
1. CORS settings in FastAPI to allow traffic from the Vercel domain.
2. PostgreSQL database connection string must point to the Render managed database.
3. Environment variables must be configured in the Vercel and Render dashboards.

---

## 🌟 Future Vision (v3.0+)

### 🔧 V2: Intelligence Hardening
These are relatively small improvements that would make the system dramatically more production-ready:
- **Real-time WebSocket Feed:** Replace the current HTTP polling (every 15 seconds) with a proper WebSocket connection. The War Room would update instantly the moment the Autopilot finishes a briefing, no polling lag.
- **Custom Standing Orders UI:** Instead of hardcoding your 3 intelligence topics in `scheduler.py`, add a settings panel to the frontend where you can type in new standing orders without touching any code.
- **User Authentication:** Protect the War Room with a login screen (JWT-based). Since this is geopolitical intelligence, you don't want the Autopilot briefings to be publicly accessible to anyone who finds your URL!
- **PDF Export:** Add a "Download Briefing as PDF" button that converts the synthesized report into a formatted intelligence document.

### 🧠 V3: Deeper AI Capabilities
These would make the AI significantly smarter:
- **Knowledge Graph Visualization:** Instead of just the linear Entity Timeline, build a proper force-directed D3.js graph that shows relationships between entities. (India ↔ Russia: Arms Deal, India ↔ USA: Tech Partnership)
- **Source Credibility Scoring:** Teach the Scout to automatically rate the reliability of each news source (e.g., Reuters = High Confidence, Random Blog = Low Confidence) and display a credibility badge on the Intel Feed.
- **Multi-source Ingestion:** Connect RSS feeds from AFP, Reuters, and Al Jazeera directly—instead of just DuckDuckGo—so the Scout always has fresh, high-quality input.
- **Voice Briefings:** Use a Text-to-Speech API (like ElevenLabs) to auto-generate audio versions of each briefing so you can listen to your morning intelligence report.

### 🌐 V4: Strategic AI Escalation
These are ambitious, impressive features that would make this a genuinely unique platform:
- **Autonomous Red-vs-Blue Simulation:** Two competing LangGraph agents—one playing an adversarial nation, one playing India—engage in an automated simulated policy debate over a given crisis. The Strategist scores the arguments.
- **Real-time Satellite Data:** Integrate with the Sentinel Hub or NASA Earthdata API to pull actual satellite imagery of geographical hotspots, then use a Vision LLM (like Gemini Vision) to detect military buildups or infrastructure changes.
- **Alert System (Telegram/Discord Bot):** When the Autopilot detects a high-urgency briefing (based on keywords like "retaliation", "ceasefire", "mobilization"), automatically push a notification to your phone via Telegram.
