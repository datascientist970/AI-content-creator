# 🚀 AI Content Creator

A beginner-friendly AI-powered content creation web application built with Django and Google Gemini API.

This guide will help you install and run the project locally on your computer.

---

## 📌 Prerequisites

Before you begin, make sure you have:

* Python 3.10 or higher installed
* Git installed
* Internet connection (for API access)

---

## 🛠 Installation Guide

Follow the steps below carefully.

---

### 1️⃣ Install Python

Download and install Python from:

[https://www.python.org/downloads/](https://www.python.org/downloads/)

⚠ Important:

* During installation, make sure to check **"Add Python to PATH"**

After installation, verify:

```bash
python --version
```

---

### 2️⃣ Clone the Repository

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
git clone https://github.com/datascientist970/AI-content-creator.git
```

---

### 3️⃣ Navigate to the Project Directory

```bash
cd AI-content-creator
```

---

### 4️⃣ Create a Virtual Environment

#### Windows:

```bash
python -m venv venv
```

#### Mac/Linux:

```bash
python3 -m venv venv
```

---

### 5️⃣ Activate the Virtual Environment

#### Windows (Command Prompt):

```bash
venv\Scripts\activate
```

#### Windows (PowerShell):

```bash
.\venv\Scripts\Activate
```

#### Mac/Linux:

```bash
source venv/bin/activate
```

✅ You should now see `(venv)` at the beginning of your terminal line.

---

### 6️⃣ Install Project Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure Gemini API

This project uses Google Gemini API for AI content generation.

### 7️⃣ Get Your API Key

1. Go to: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **"Create API Key"**
3. Copy your API key

---

### 8️⃣ Add API Key to Environment File

1. Locate `.env.example` inside the project folder
2. Rename it to `.env`
3. Open `.env` and add:

```
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

4. Save the file

⚠ Do NOT share your `.env` file publicly.

---

## 🗄 Database Setup

Run database migrations:

```bash
python manage.py migrate
```

---

## ▶ Run the Development Server

```bash
python manage.py runserver
```

---

## 🌐 Access the Application

Open your browser and visit:

```
http://127.0.0.1:8000/
```

Your AI Content Creator app should now be running locally 🎉

---

## 🛑 Troubleshooting

* If `(venv)` is not visible → Activate the virtual environment again
* If `python` command not found → Reinstall Python and check "Add to PATH"
* If API errors occur → Make sure your Gemini API key is correct in `.env`

---

## 📂 Project Structure (Basic Overview)

```
AI-content-creator/
│
├── manage.py
├── requirements.txt
├── .env
├── app/
└── templates/
```

---

## 📄 License

This project is for educational purposes.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub!
