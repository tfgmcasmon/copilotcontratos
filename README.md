# ⚖️ Themis – LegalTech AI Toolkit for Contract Automation and Assistance

**Themis** is an AI-powered LegalTech toolkit designed to automate legal drafting, contract validation, and access to normative information. Built with lawyers in mind and powered by modern NLP techniques, Themis enables intelligent interaction with legal documents in real time.

> 🧠 Developed as a Final Degree Project (TFG) at Universidad Pontificia Comillas – ICAI  
> 🎓 Degree: Grado en Ingeniería en Tecnologías de Telecomunicación  
> 👩‍💻 Author: María Castilla Montes  
> 📅 Academic Year: 2024/2025  

---

## 🧰 Modules

### 📄 Contract Copilot
- Real-time legal autocompletion based on user input
- Context-aware clause suggestion
- Section recognition: "EXPONEN", "CLÁUSULAS", "REUNIDOS", etc.
- Automatic clause numbering and prompt adaptation

### 🧪 Semantic Data Verification
- Automatic detection of inconsistent or duplicated data (e.g., DNI, phone numbers)
- Validation using NLP and regex
- Issues and warnings returned as structured JSON

### 🔍 Legal Assistant (Q&A)
- Vectorized corpus of Spanish legal texts (BOE)
- Search via semantic similarity using SentenceTransformers and FAISS
- Normative fragment retrieval without keyword dependency

---

## ⚙️ Tech Stack

| Layer       | Technology                                     |
|-------------|------------------------------------------------|
| Backend     | Python · Flask · spaCy · SentenceTransformers  |
| Frontend    | React · jsPDF · TailwindCSS                    |
| Vector DB   | FAISS                                          |
| LLM         | Mistral 7B (via OpenRouter API)                |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/themis-legaltech.git
cd themis-legaltech
