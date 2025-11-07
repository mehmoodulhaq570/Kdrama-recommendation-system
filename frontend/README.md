# SeoulMate Frontend

## 🚀 Quick Start (Streamlit)

### 1. Install Dependencies

```powershell
pip install -r frontend/requirements.txt
```

### 2. Start Backend (Terminal 1)

```powershell
python backend/app.py
```

### 3. Start Frontend (Terminal 2)

```powershell
streamlit run frontend/streamlit_app.py
```

### 4. Open Browser

- Frontend: http://localhost:8501
- Backend API: http://localhost:8001

---

## ✨ Features

- 🔍 **Search by Title:** Find similar dramas
- 🎯 **AI-Powered:** SBERT + BM25 + Cross-Encoder
- 📊 **System Stats:** View model performance
- 🎨 **Beautiful UI:** Gradient cards, responsive design
- ⚡ **Real-time:** Instant recommendations

---

## 🛠️ Troubleshooting

**Frontend won't start?**

```powershell
pip install streamlit --upgrade
```

**Backend connection error?**

- Make sure backend is running on port 8001
- Check `http://127.0.0.1:8001/` in browser

**Port already in use?**

```powershell
streamlit run frontend/streamlit_app.py --server.port 8502
```

---

## 🎯 Next Steps: Upgrade to Next.js

When ready for production, we'll create:

- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Vercel deployment ready
- Server-side rendering (SEO)

Stay tuned! 🚀
