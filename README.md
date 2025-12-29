# 💬 ChatSphere – Real-Time Chat Application

**ChatSphere** is a **production-ready real-time chat web application** built using **Flask, WebSocket (Flask-SocketIO), MySQL, and modern frontend technologies**.

This application enables users to **create accounts, securely authenticate, and exchange messages instantly** using **real-time WebSocket communication**, similar to modern chat platforms like WhatsApp or Messenger.

The project demonstrates **real-world backend architecture**, **JWT-based authentication**, **persistent chat history**, **user presence tracking**, and **secure socket communication**.

---

## 📸 Project Preview

![Preview](https://github.com/niveshbansal07/PRODIGY_FS_04/blob/main/Real-time%20Chat%20-%20Google%20Chrome%2012_29_2025%207_28_08%20AM.png)
![Preview](https://github.com/niveshbansal07/PRODIGY_FS_04/blob/main/Real-time%20Chat%20-%20Brave%2012_29_2025%207_28_22%20AM.png)


---

## 🚀 Features

### ✅ Core Features

* User Signup & Login system
* Secure authentication using **JWT (JSON Web Tokens)**
* Password hashing with **bcrypt**
* **Real-time messaging** using WebSocket (Flask-SocketIO)
* One-to-one private chat system
* **Persistent chat history** stored in MySQL
* Secure token-based socket connections
* REST APIs + WebSocket integration
* Clean, responsive & user-friendly UI
* Protected routes for authenticated users

### ⭐ Advanced / Optional Features

* Live **user online/offline presence**
* Message timestamps
* Scalable backend architecture
* Modular API design
* Ready for future enhancements like:

  * Group chats
  * Message notifications
  * File & media sharing
  * Read receipts
  * Typing indicators

---

## 🛠 Tech Stack

### **Frontend**

* HTML5
* CSS3 (Responsive & clean UI)
* JavaScript (Fetch API + Socket Events)

### **Backend**

* Python (Flask)
* Flask-SocketIO (WebSocket)
* JWT Authentication
* bcrypt (Password hashing)
* REST APIs

### **Database**

* MySQL (Relational database)

### **Other Tools & Libraries**

* Flask-CORS
* PyMySQL
* python-dotenv

---

## 📁 Project Structure

```
ChatSphere/
│
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── chat.js
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── chat.html
│
├── config.py
├── app.py
├── requirements.txt
└── venv/
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_SECRET_KEY=your_flask_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

⚠️ **Important:**
Always add `.env` to `.gitignore` to keep sensitive credentials secure.

---

## 🗄 Database Structure (MySQL)

```sql
-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255)
);

-- Messages Table
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Database

Update **MySQL credentials** inside `config.py`.

### ▶ Run the Application

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## 🧠 What I Learned

* Real-time communication using WebSockets
* Flask-SocketIO architecture
* Secure JWT-based authentication
* Managing socket connections securely
* MySQL relational database design
* Storing & retrieving chat history
* Handling user presence (online/offline)
* REST API + WebSocket integration
* Writing scalable backend code
* Building real-world messaging systems

---

## 📌 Project Purpose

This project was built to:

* Understand **real-time system design**
* Implement **secure messaging platforms**
* Practice backend & database workflows
* Build an **industry-level chat application**
* Strengthen full-stack development skills

---

## 📬 Contact

**Nivesh Bansal**
Aspiring Full Stack Developer

📧 Email: **[niveshbansal52@gmail.com](mailto:niveshbansal52@gmail.com)**
🌐 Portfolio: [https://nivesh-bansal.vercel.app](https://nivesh-bansal.vercel.app)
🔗 GitHub: [https://github.com/niveshbansal07](https://github.com/niveshbansal07)

