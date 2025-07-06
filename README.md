# CSV InsightHub 💼

CSV InsightHub is a secure, AI-powered CSV analytics platform that combines automated dashboards with a real-time, CSV-aware chatbot. It simplifies employee data analysis and supports dynamic question answering using LangChain’s LLMChain and Google’s Gemini Pro API.

---

## 🚀 Features

- 🔐 Secure login/signup with token-based authentication
- 📤 Upload and manage large CSV files (up to 200MB)
- 📊 Auto-generated HR analytics dashboard with KPIs and visualizations
- 🤖 Real-time chatbot powered by LangChain LLMChain and Google Gemini API
- 🧠 Intelligent CSV-aware responses across any uploaded dataset
- 📁 Displays recent uploads and interactive tables

---

## 🎥 Demo Access

▶️ Check out the project in action:  
[Download Demo Video](demo.mp4)

The demo showcases the complete user flow from login, CSV upload, dashboard generation, and chatbot interaction.

---

## 🛠️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/csv-insighthub.git
cd csv-insighthub
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_gemini_api_key
MAX_DF_ROWS=10000
```

### 4. Run Backend (FastAPI)
```bash
uvicorn app.main:app --reload
```

### 5. Run Frontend (Streamlit)
```bash
streamlit run app.py
```

---

## 💡 Example Prompts

- "Who has taken the most leaves?"
- "Which employee has the highest training hours?"
- "What is the average tenure of employees?"
- "List employees eligible for promotion."
- "Show attrition rate by department."

---

## 📁 Project Structure

```
├── app.py                  # Streamlit frontend
├── chat.py                 # FastAPI chatbot logic
├── app/
│   ├── main.py             # FastAPI entry point
│   ├── models/             # User model schema
│   ├── utils/              # Auth token utilities
├── uploads/                # Uploaded CSV files
├── demo.mp4                # Demo video
├── requirements.txt
└── README.md
```

---

## 🧠 Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [LangChain LLMChain](https://www.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Pandas](https://pandas.pydata.org/)
- [st-aggrid](https://github.com/PablocFonseca/streamlit-aggrid)

---

## 🌱 Future Scope

- UI enhancements for smoother user experience  
- Chat history storage for persistent sessions  
- Additional advanced plots and visualizations  
- File selection for multi-dataset switching  
- Streamlit Cloud deployment for global access  
- Session management and logout functionality

---

## 🛡️ Disclaimer

CSV InsightHub is intended for educational and internal analytics use only. Always validate insights before making critical decisions.
