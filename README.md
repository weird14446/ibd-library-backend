# 📚 IBD Library

> AI와 함께하는 Vibe Coding 프로젝트

도서관 관리 시스템을 **Vibe Coding** 방식으로 개발하는 프로젝트입니다.

---

## 🛠 Tech Stack

| 영역 | 기술 |
|------|------|
| **Frontend** | React + Vite |
| **Backend** | Python FastAPI |
| **Development** | Vibe Coding with AI Agents |

---

## 📂 Project Structure

```
├── frontend/            # React + Vite
├── backend/             # Python FastAPI
├── intents/             # 의도 정의서 (Intent Specifications)
├── .agent/              # AI Agent 설정
└── README.md
```

---

## 🚀 Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🎯 Vibe Coding

이 프로젝트는 **Vibe Coding** 방식을 채택합니다.

코드를 직접 작성하기보다 **의도(Intent)**를 명확히 전달하면, AI Agent가 구현을 담당합니다.

### 좋은 의도 작성법

```
✅ "사용자가 도서를 검색할 때 제목, 저자, ISBN으로 필터링할 수 있어야 해.
    검색 결과는 페이지네이션으로 표시하고, 한 페이지에 20권씩 보여줘."

❌ "검색 기능 만들어줘."
```

**What(목표)**, **Why(이유)**, **Constraint(제약)**을 포함하면 더 좋은 결과를 얻을 수 있습니다.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.