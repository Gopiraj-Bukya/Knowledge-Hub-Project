# Knowledge-Hub-Project 📚

## Overview
The **Knowledge-Hub-Project** is a Streamlit-based **Learning Management System (LMS)** that allows administrators to manage book uploads (PDFs) and users to view them in an interactive panel. This system supports user authentication, a chatbot for assistance, and database integration for efficient data handling.

## Features ✨
- **Admin Panel** 📑  
  - Upload books (PDFs)
  - Manage content via the database  
- **User Panel** 👨‍🎓  
  - View and read books
  - Access personalized recommendations (future enhancement)
- **Authentication System** 🔐  
  - Admin and User login/registration
- **Database Integration** 🗄  
  - SQLite database (`your_database.db`) stores user and book data
- **Chatbot Support** 🤖  
  - A chatbot for user queries and support
- **Navigation System** 🧭  
  - Sidebar-based navigation for better UX

## Installation & Setup 🛠
1. **Clone the Repository**
   ```sh
   git clone https://github.com/Gopiraj-Bukya/Knowledge-Hub-Project.git
   cd Knowledge-Hub-Project
   ```
2. **Create & Activate Virtual Environment**
   ```sh
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the Application**
   ```sh
   streamlit run app.py
   ```

## Folder Structure 📂
```
Knowledge-Hub-Project/
│-- .streamlit/            # Streamlit config files
│-- Images/                # Static images (logos, banners, etc.)
│-- data/                  # Data files if needed
│-- app.py                 # Main Streamlit application
│-- lms.db                 # LMS Database file
│-- lms_backup.db          # Backup database
│-- your_database.db       # Primary database (SQLite)
│-- requirements.txt       # Dependencies
│-- README.md              # Documentation (this file)
```

## Future Enhancements 🚀
- **User-based book recommendations 📖**
- **Role-based access control 🔑**
- **Enhanced chatbot integration 🤖**
- **Better UI/UX improvements 🎨**

## Contributions 🤝
Want to contribute? Fork the repo, create a new branch, make your changes, and submit a pull request!



---
Made with ❤️ by **Gopiraj-Bukya** 🚀

