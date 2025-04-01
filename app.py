import sqlite3
import streamlit as st
import pandas as pd
import bcrypt
import base64
from PIL import Image
import io
import time
import google.generativeai as genai
import os
from functools import lru_cache
import re
# Set page config FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="SHAIGO - Library Assistant", 
    page_icon="📚"
)


# In code
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])



# ===== PROFESSIONAL BACKGROUND HANDLER =====
def set_background(image_path):
    """
    Enhanced background function with intelligent text contrast
    """
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        
        /* Dynamic text contrast */
        h1, h2, h3, h4, h5, h6, .stMarkdown {{
            color: rgba(255,255,255,0.95) !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8) !important;
        }}
        
        /* Transparent header */
        header {{
            background: transparent !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ===== PROFESSIONAL UI COMPONENTS =====
st.markdown("""
<style>
/* ===== GLOBAL STYLES ===== */
* {
    transition: all 0.3s ease;
}

/* ===== INPUT FIELDS ===== */
.stTextInput input,
.stTextArea textarea,
.stSelectbox select,
.stNumberInput input,
.stDateInput input {
    background: rgba(0,0,0,0.4) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #1e88e5 !important;
    box-shadow: 0 0 0 2px rgba(30,136,229,0.2), 
                inset 0 1px 3px rgba(0,0,0,0.3) !important;
}

/* ===== BUTTONS ===== */
.stButton>button,
.stDownloadButton>button {
    background: linear-gradient(135deg, #1e88e5 0%, #0d47a1 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    border: none !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    width: 100% !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

/* Danger buttons */
.stButton>button:contains('Clear'),
.stButton>button:contains('Delete') {
    background: linear-gradient(135deg, #e53935 0%, #b71c1c 100%) !important;
}

/* ===== SIDEBAR NAVIGATION ===== */
.stRadio>div {
    flex-direction: column;
    gap: 8px;
}

.stRadio label {
    background: rgba(0,0,0,0.4) !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(5px);
}

.stRadio label:hover {
    background: rgba(0,0,0,0.6) !important;
}

.stRadio label>div:first-child {
    justify-content: center;
    color: white !important;
}

/* ===== CARDS & CONTAINERS ===== */
.stForm {
    background: rgba(0,0,0,0.5) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

/* ===== CHAT INTERFACE ===== */
.stChatMessage {
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    border-radius: 12px !important;
    max-width: 85% !important;
    backdrop-filter: blur(5px);
}

.stChatMessage.user {
    background: rgba(30, 136, 229, 0.25) !important;
    border: 1px solid rgba(30, 136, 229, 0.4) !important;
}

.stChatMessage.assistant {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;S
}

.stChatInput textarea {
    background: rgba(0,0,0,0.5) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ===== APPLICATION LAYOUT =====
# Background setup
backgrounds = {
    "🏠 Home": r"C:\Users\GOPIRAJ\OneDrive\Desktop\lmsstreamlit\Images\rainlightbook.jpg",
    "📘 Library Manager": r"C:\Users\GOPIRAJ\OneDrive\Desktop\lmsstreamlit\Images\rainchair.jpg",
    "📖 Learning Den": r"C:\Users\GOPIRAJ\OneDrive\Desktop\lmsstreamlit\Images\cupwithbook.jpg"
}

# Sidebar navigation

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📘 Library Manager", "📖 Learning Den"],
    label_visibility="collapsed"
)

# Set background
set_background(backgrounds[page])






# Initialize the database


def create_tables():
    conn = sqlite3.connect('lms.db')
    c = conn.cursor()

    # Users table for admins and users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            role TEXT CHECK(role IN ('admin', 'user'))
        )
    ''')

    # Books table
    # Add the pdf_link column
   
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            genre TEXT,
            price REAL,
            pdf_link TEXT  -- New column for PDF link
        )
    ''')

    # Assigned books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assigned_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            user_id INTEGER,
            assigned_by INTEGER,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(assigned_by) REFERENCES users(id)
        )
    ''')

    # Borrowed books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            user_id INTEGER,
            borrowed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
     
    # New table for returned books
    c.execute('''
        CREATE TABLE IF NOT EXISTS returned_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            user_id INTEGER,
            returned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
 
     # Add this new table for book requests
    c.execute('''
        CREATE TABLE IF NOT EXISTS book_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            requested_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
   
    
    conn.close()
@st.cache_data
def get_returned_books():
    conn = sqlite3.connect('lms.db')
    returned_books = conn.execute('''
        SELECT b.title, u.username, r.returned_date
        FROM returned_books r
        JOIN books b ON r.book_id = b.id
        JOIN users u ON r.user_id = u.id
    ''').fetchall()
    conn.close()
    return returned_books    
    
create_tables()

# Fetch returned books data
returned_books = get_returned_books()
# Display returned books


# Initialize session state
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
if 'user_logged_in' not in st.session_state:
    st.session_state['user_logged_in'] = False
if 'admin_username' not in st.session_state:
    st.session_state['admin_username'] = None
if 'user_username' not in st.session_state:
    st.session_state['user_username'] = None
    

if 'returned_books' not in st.session_state:
    st.session_state['returned_books'] = get_returned_books()
# Function to log out admin
def logout_admin():
    st.session_state['admin_logged_in'] = False
    st.session_state['admin_username'] = None
    st.session_state['user_role'] = None
    st.success("✅ Admin logged out successfully!")
    st.rerun()  # Force a rerun to update the UI

    

# Function to log out user
def logout_user():
    st.session_state['user_logged_in'] = False
    st.session_state['user_username'] = None
    st.session_state['user_role'] = None
    st.success("✅ User logged out successfully!")
    st.rerun()  # Force a rerun to update the UI



# Check session timeout
if 'last_activity' not in st.session_state:
    st.session_state['last_activity'] = time.time()
if time.time() - st.session_state['last_activity'] > 1800:  # 30 minutes
    logout_user()
# Update last_activity on user interaction
st.session_state['last_activity'] = time.time()        
    

# Header
st.title("📚 Knowledge Hub")
st.write("Centralized Knowledge Management System")

def get_gemini_model():
    """Configure and return Gemini model"""
    return genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={
            "temperature": 0.3,
            "top_p": 0.7,
            "top_k": 20,
            "max_output_tokens": 512
        },
        safety_settings={
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
        }
    )

# SHAIGO's avatar path (replace with your actual path)
SHAIGO_AVATAR_PATH = r"C:\Users\GOPIRAJ\OneDrive\Desktop\lmsstreamlit\Images\shaigo.png"  # Path relative to your app.py

def load_shaigo_avatar():
    """Load SHAIGO's avatar image with error handling"""
    try:
        if os.path.exists(SHAIGO_AVATAR_PATH):
            return Image.open(SHAIGO_AVATAR_PATH)
        return None  # Will fall back to default avatar
    except Exception as e:
        st.warning(f"Couldn't load SHAIGO avatar: {str(e)}")
        return None
    
def handle_signup_question(user_role):
    """Provide appropriate signup information based on user role"""
    if user_role == "admin":
        return "🔒 You're already logged in as admin. " \
               "You can create user accounts in the Library Manager.\n\n- SHAIGO"
    elif user_role == "user":
        return "✅ You're already registered! " \
               "Visit the Learning Den to access your account.\n\n- SHAIGO"
    else:
        return """📝 Guest Registration:
1. Go to the Learning Den page
2. Select 'User Signup'
3. Fill in your details
4. Click 'Register'
        
Note: Admin approval may be required for full access.\n\n- SHAIGO"""

def handle_user_queries(query):
    """Handle user-specific queries (excluding requests which are handled separately)"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        return "Please login to access this information.\n\n- SHAIGO"
    
    query = query.lower()
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    
    try:
        # Handle borrowed books query
        if "my borrowed books" in query or "books i have" in query:
            cursor.execute('''
                SELECT b.title, bb.borrowed_date
                FROM borrowed_books bb
                JOIN books b ON bb.book_id = b.id
                WHERE bb.user_id = ?
                ORDER BY bb.borrowed_date DESC
            ''', (user_id,))
            books = cursor.fetchall()
            
            if books:
                response = "📚 Books You've Borrowed:\n" + "\n".join(
                    [f"- {title} (since {date})" for title, date in books])
            else:
                response = "You haven't borrowed any books yet."
            return response + "\n\n- SHAIGO"
        
        # Handle general user queries
        return generate_general_response(query)
    
    finally:
        conn.close()

def extract_book_title(query):
    """Extract book title from natural language queries"""
    # Remove common question phrases
    stop_phrases = [
        "tell me about", "what is", "summary of", "information about",
        "details of", "who wrote", "describe", "explain"
    ]
    clean_query = query.lower()
    for phrase in stop_phrases:
        clean_query = clean_query.replace(phrase, "")
    
    # Remove special characters and extra spaces
    clean_query = re.sub(r'[^\w\s]', '', clean_query).strip()
    return clean_query if clean_query else None

def get_book_summary(book_title):
    """Get book summary from Gemini with library-appropriate formatting"""
    prompt = f"""Provide a concise summary (3-4 sentences) of the book "{book_title}" 
    as a librarian would describe it to a patron. Include:
    - Author if known
    - Main themes/subject
    - Typical audience
    - Similar books in our collection
    
    Format response professionally and sign as '- SHAIGO'"""
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Couldn't retrieve information about '{book_title}'. " \
               f"Please check the title and try again.\n\n- SHAIGO"        


# SHAIGO Core Functions
def chatbot():
    """SHAIGO Chatbot - Shows only after login with 3 core functions"""
    
    # Only show if logged in (user or admin)
    if not st.session_state.get('user_logged_in') and not st.session_state.get('admin_logged_in'):
        return
    
    # Initialize session state variables
    if "shaigo_history" not in st.session_state:
        st.session_state.shaigo_history = []
        st.session_state.last_processed_input = None
    
    # Display chat UI
    st.sidebar.title("💬 I'm SHAIGO")
    st.sidebar.title("Your AI Chat Buddy, Ask Me Anything!")
    # Display conversation history
    for msg in st.session_state.shaigo_history:
        role = "You" if msg["role"] == "user" else "SHAIGO"
        st.sidebar.markdown(f"**{role}:** {msg['content']}")
    
    # Clear conversation button
    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.shaigo_history = []
        st.session_state.last_processed_input = None
        st.rerun()
    
    # Get user input with empty default
    user_input = st.sidebar.text_input("Ask about books or users:", 
                                     key="shaigo_input", 
                                     value="")
    
    # Process input when there's new text and Enter is pressed
    if user_input and user_input != st.session_state.get('last_processed_input'):
        process_query(user_input)

def process_query(query):
    """Process user query and generate response"""
    # Store the input being processed
    st.session_state.last_processed_input = query
    
    # Add user message to history
    st.session_state.shaigo_history.append({"role": "user", "content": query})
    
    # Generate appropriate response
    response = generate_response(query)
    
    # Add bot response to history
    st.session_state.shaigo_history.append({"role": "assistant", "content": response})
    
    # Clear the input field by forcing a rerun
    st.rerun()

def generate_response(query):
    """Generate response based on query type"""
    query = query.lower().strip()
    
    # 1. Handle greetings
    if query in ['hi', 'hello', 'hey']:
        return "Hello! How can I help with library resources today?\n\n- SHAIGO"
    
    # 2. Handle available books request
    if "available books" in query or "show books" in query:
        return get_books_status()
    
    # 3. Handle users list (admin only)
    if "users" in query and st.session_state.get('admin_logged_in'):
        return get_users_list()
    
    # 4. Handle book summary requests
    if any(keyword in query for keyword in ["summary", "about", "tell me", "what is"]):
        return get_book_summary(query)
    
    # Default response for unrecognized queries
    return ("I can help with:\n"
            "- Book availability ('show available books')\n"
            "- Book summaries ('tell me about [book]')\n"
            "- User lists for admins ('show users')\n\n"
            "- SHAIGO")

def get_books_status():
    """Get all books with availability status"""
    conn = sqlite3.connect('lms.db')
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.title, b.author, 
                   CASE WHEN bb.id IS NULL THEN 'Available' ELSE 'Borrowed' END as status
            FROM books b
            LEFT JOIN borrowed_books bb ON b.id = bb.book_id
            ORDER BY b.title
        ''')
        books = cursor.fetchall()
        
        if not books:
            return "No books found in the library.\n\n- SHAIGO"
            
        response = "📚 All Books in Library:\n\n"
        for title, author, status in books:
            response += f"- {title} by {author} ({status})\n"
        
        return response + "\n- SHAIGO"
    
    except Exception as e:
        return f"⚠️ Error accessing library: {str(e)}\n\n- SHAIGO"
    finally:
        conn.close()

def get_users_list():
    """Get list of all registered users (admin only)"""
    conn = sqlite3.connect('lms.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, role FROM users ORDER BY username")
        users = cursor.fetchall()
        
        if not users:
            return "No users registered yet.\n\n- SHAIGO"
            
        response = "👥 Registered Users:\n\n"
        for username, email, role in users:
            response += f"- {username} ({email}) - {role}\n"
        
        return response + "\n- SHAIGO"
    
    except Exception as e:
        return f"⚠️ Error accessing user records: {str(e)}\n\n- SHAIGO"
    finally:
        conn.close()

def get_book_summary(query):
    """Generate book summary using Gemini AI"""
    # Extract book title from query
    book_title = query.replace("summary of", "").replace("tell me about", "").replace("about", "").replace("what is", "").strip('"').strip()
    
    if not book_title:
        return "Please specify a book title.\n\n- SHAIGO"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"""As a librarian, provide a concise 3-sentence summary of "{book_title}":
            1. Author and main theme
            2. Why readers enjoy it
            3. Similar books in our collection
            
            Format: Professional tone, end with '- SHAIGO'"""
        )
        return response.text if response else f"Couldn't find information about {book_title}.\n\n- SHAIGO"
    except Exception as e:
        return f"⚠️ Error retrieving book information.\n\n- SHAIGO"

def get_books_status():
    """Retrieve all books with availability status"""
    conn = sqlite3.connect('lms.db')
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.title, b.author, 
                   CASE WHEN bb.id IS NULL THEN 'Available' ELSE 'Borrowed' END as status
            FROM books b
            LEFT JOIN borrowed_books bb ON b.id = bb.book_id
            ORDER BY b.title
        ''')
        books = cursor.fetchall()
        
        if not books:
            return "No books found in the library.\n\n- SHAIGO"
            
        response = "📚 Library Books Status:\n\n"
        for title, author, status in books:
            response += f"- {title} by {author} ({status})\n"
        
        return response + "\n- SHAIGO"
    
    except Exception as e:
        return f"⚠️ Error accessing library: {str(e)}\n\n- SHAIGO"
    finally:
        conn.close()

def get_users_list():
    """Retrieve all registered users (admin only)"""
    conn = sqlite3.connect('lms.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, role FROM users ORDER BY username")
        users = cursor.fetchall()
        
        if not users:
            return "No users registered yet.\n\n- SHAIGO"
            
        response = "👥 Registered Users:\n\n"
        for username, email, role in users:
            response += f"- {username} ({email}) - {role}\n"
        
        return response + "\n- SHAIGO"
    
    except Exception as e:
        return f"⚠️ Error accessing user records: {str(e)}\n\n- SHAIGO"
    finally:
        conn.close()

def get_book_summary(query):
    """Generate book summary using Gemini AI"""
    # Extract book title
    book_title = query.replace("summary of", "").replace("tell me about", "").strip('"').strip()
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"""As a professional librarian, provide a concise 3-sentence summary of "{book_title}":
            1. Author and main theme
            2. Why readers enjoy it
            3. Similar books we have
            
            Format: Bullet points, end with '- SHAIGO'"""
        )
        return response.text if response else f"Couldn't find information about {book_title}.\n\n- SHAIGO"
    except Exception as e:
        return f"⚠️ Error retrieving book information.\n\n- SHAIGO"

# ================ MAIN APPLICATION ================
def main():
    create_tables

# [Keep your existing check_book_availability() and get_gemini_model() functions]

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Helper function to verify passwords
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Function to register users
def register_user(username, email, password, role):
    conn = sqlite3.connect('lms.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)", (username, email, hashed_password, role))
        conn.commit()
        st.success(f"🎉 {username}, you are successfully registered as {role}!")
    except sqlite3.IntegrityError:
        st.error("❗ Username or email already exists!")
    finally:
        conn.close()

# Function to authenticate users
def login_user(username, password, role):
    conn = sqlite3.connect('lms.db')
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ? AND role = ?", (username, role))
    user = c.fetchone()
    conn.close()
    if user and verify_password(password, user[1]):
        st.session_state['user_id'] = user[0]  # Store user ID in session state
        st.session_state['user_role'] = role  # Update user role in session state
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.success(f"✅ Welcome {username}, you are logged in as {role.capitalize()}!")
        return True
    else:
        st.error("❌ Invalid username or password!")
        return False


# Logout functionality
def logout_user():
    # Clear all relevant session state variables
    st.session_state['user_logged_in'] = False
    st.session_state['user_username'] = None
    st.session_state['user_id'] = None
    st.session_state['user_role'] = None
    st.session_state['logged_in'] = False
    
    # Force a full page refresh
    st.rerun()
    
    # Show logout message (this will appear after the refresh)
    st.success("✅ You have been logged out!")

# Function to assign a book
def assign_book(book_title, username, assigned_by):
    conn = sqlite3.connect('lms.db')
    c = conn.cursor()
    c.execute("SELECT id FROM books WHERE title = ?", (book_title,))
    book = c.fetchone()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if book and user:
        book_id = book[0]
        user_id = user[0]
        c.execute("INSERT INTO assigned_books (book_id, user_id, assigned_by) VALUES (?, ?, ?)", (book_id, user_id, assigned_by))
        conn.commit()
        conn.close()
        st.success(f"📚 Book '{book_title}' assigned successfully to {username}!")
    else:
        st.error("❌ Book or user not found!")

# Function to borrow a book
def borrow_book(book_title, user_id):
    conn = sqlite3.connect('lms.db')
    c = conn.cursor()
    c.execute("SELECT id FROM books WHERE title = ?", (book_title,))
    book = c.fetchone()
    if book:
        book_id = book[0]
        c.execute("INSERT INTO borrowed_books (book_id, user_id) VALUES (?, ?)", (book_id, user_id))
        conn.commit()
        conn.close()
        st.success(f"📚 You have successfully borrowed '{book_title}'!")
    else:
        st.error("❌ Book not found!")


def check_book_availability(query):
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    
    # Extract search terms
    search_terms = []
    if "by" in query.lower():
        author = query.split("by")[1].strip()
        search_terms.append(f"author LIKE '%{author}%'")
    if "about" in query.lower():
        topic = query.split("about")[1].strip()
        search_terms.append(f"(title LIKE '%{topic}%' OR genre LIKE '%{topic}%')")
    
    # Build query
    where_clause = " AND ".join(search_terms) if search_terms else "1=1"
    sql = f"""
    SELECT title, author, genre, 
           CASE WHEN id IN (SELECT book_id FROM borrowed_books) THEN 'Checked Out' 
                ELSE 'Available' END as status
    FROM books
    WHERE {where_clause}
    LIMIT 5
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    
    if results:
        books_info = "\n".join([f"- {title} by {author} ({genre}) - {status}" 
                              for title, author, genre, status in results])
        return f"Here are some matching books:\n{books_info}"
    else:
        return "No matching books found in our database."

def get_available_actions():
    if st.session_state.get('user_role') == 'admin':
        return "Manage books, users, view reports"
    elif st.session_state.get('user_role') == 'user':
        return "Browse books, borrow, return"
    return "Browse books"

def get_last_update_time():
    conn = sqlite3.connect('lms.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(borrowed_date) FROM borrowed_books")
    last_update = cursor.fetchone()[0]
    conn.close()
    return last_update or "Today"

def generate_general_response(prompt):
    model = get_gemini_model()
    
    # Get current library context
    context = f"""
    Library System Context:
    - Current page: {page}
    - User role: {st.session_state.get('user_role', 'guest')}
    - Available actions: {get_available_actions()}
    
    Last database update: {get_last_update_time()}
    """
    
    response = model.generate_content(
        f"""You're a specialized library assistant. First check if this query requires 
        database lookup. If not, respond helpfully.
        
        Context: {context}
        Question: {prompt}
        
        Response guidelines:
        1. For book queries: check database first
        2. For account questions: verify user status
        3. Be concise and factual
        4. Never make up book information""",
        stream=True
    )
    
    return "".join([chunk.text for chunk in response])    

# ADD THIS LINE TO SHOW CHATBOT ON ALL PAGES
# =============================================
def main():
    
    
   
    
    # Show chatbot on all pages
    chatbot()
    
    # Your existing page content
    if page == "🏠 Home":
        # Home page content
        pass
    elif page == "📘 Library Manager":
        # Library Manager content
        pass
    elif page == "📖 Learning Den":
        # Learning Den content
        pass

if __name__ == "__main__":
    main()

if page == "🏠 Home":
    # Use a container to organize content
    with st.container():
        caption="Your digital library, reimagined.", 
        use_container_width=True,
        output_format="auto", 
        
        # Add more content here if needed
    st.write("Explore our features:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("📘 **Library Manager**")
        st.write("Manage books, users, and assignments.")
    with col2:
        st.write("📖 **Learning Den**")
        st.write("Borrow and read books seamlessly.")
    with col3:
        st.write("🖥️ **Admin Tools**")
        st.write("Advanced tools for administrators.")

# Admin Section (Library Manager)
elif page == "📘 Library Manager":
    st.title("Admin Command Center")
           
    # Check if admin is logged in
    if not st.session_state['admin_logged_in']:
        with st.form("admin_login_form"):
            st.subheader("Admin Login")
            username = st.text_input("👤 Admin Username")
            password = st.text_input("🔒 Admin Password", type="password")
            
            if st.form_submit_button("🚀 Login", use_container_width=True):
                if username and password:
                    with st.spinner("Authenticating..."):
                        if login_user(username, password, "admin"):
                            st.session_state['admin_logged_in'] = True
                            st.session_state['admin_username'] = username
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                else:
                    st.error("Please enter username and password")
        
        with st.expander("Create Admin Account"):
            with st.form("admin_signup_form"):
                st.subheader("Admin Signup")
                new_username = st.text_input("👤 Choose Admin Username")
                new_email = st.text_input("📧 Admin Email")
                new_password = st.text_input("🔒 Create Password", type="password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password")
                
                if st.form_submit_button("📝 Register", use_container_width=True):
                    if new_username and new_email and new_password and confirm_password:
                        if new_password == confirm_password:
                            with st.spinner("Creating admin account..."):
                                if register_user(new_username, new_email, new_password, "admin"):
                                    st.success("Admin account created! Please login")
                                    st.rerun()
                        else:
                            st.error("Passwords don't match!")
                    else:
                        st.error("Please fill all fields!")
    
    else:
        st.sidebar.subheader(f"🔧 Admin Dashboard")
        st.sidebar.markdown(f"Logged in as: **{st.session_state['admin_username']}**")
        
        # Navigation Buttons
        nav_col1, nav_col2 = st.sidebar.columns(2)
        with nav_col1:
            if st.button("🏠 Home"):
                st.session_state['admin_action'] = "home"
        with nav_col2:
            if st.button("📚 Books"):
                st.session_state['admin_action'] = "books"
        
        nav_col3, nav_col4 = st.sidebar.columns(2)
        with nav_col3:
            if st.button("👥 Users"):
                st.session_state['admin_action'] = "users"
        with nav_col4:
            if st.button("📖 Assign"):
                st.session_state['admin_action'] = "assign"
        
        # Logout Button (matches login button style)
        if st.sidebar.button("🚪 Logout", type="primary", use_container_width=True):
            with st.spinner("Logging out..."):
                logout_admin()
                st.rerun()

        # Main Content Area
        if st.session_state.get('admin_action') == "home":
            st.subheader("Admin Dashboard")
            st.write("Manage your library system using the options in the sidebar")
            
        elif st.session_state.get('admin_action') == "books":
            st.subheader("📚 Book Management")
            
            tab1, tab2, tab3 = st.tabs(["Add Book", "Remove Book", "View Books"])
            
            with tab1:
                with st.form("add_book_form"):
                    title = st.text_input("📚 Book Title")
                    author = st.text_input("✍️ Author")
                    genre = st.text_input("🎭 Genre")
                    price = st.number_input("💸 Price (₹)", min_value=0.0)
                    pdf_link = st.text_input("🔗 PDF Link (optional)")
                    
                    if st.form_submit_button("✅ Register Book"):
                        if title and author and genre and price:
                            conn = sqlite3.connect('lms.db')
                            c = conn.cursor()
                            c.execute('''
                                INSERT INTO books (title, author, genre, price, pdf_link)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (title, author, genre, price, pdf_link))
                            conn.commit()
                            conn.close()
                            st.success(f"📗 '{title}' registered successfully!")
                        else:
                            st.error("All fields except PDF link are required!")
            
            with tab2:
                with st.form("remove_book_form"):
                    book_to_remove = st.text_input("🔍 Enter Book Title to Remove")
                    if st.form_submit_button("❌ Remove Book"):
                        if book_to_remove:
                            conn = sqlite3.connect('lms.db')
                            c = conn.cursor()
                            c.execute("DELETE FROM books WHERE title = ?", (book_to_remove,))
                            conn.commit()
                            conn.close()
                            st.success(f"🗑️ '{book_to_remove}' removed successfully!")
            
            with tab3:
                st.subheader("All Books in Library")
                conn = sqlite3.connect('lms.db')
                books_data = conn.execute("SELECT id, title, author, genre, price, pdf_link FROM books").fetchall()
                conn.close()

                if books_data:
                    df = pd.DataFrame(books_data, columns=["ID", "Title", "Author", "Genre", "Price", "PDF Link"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No books available in the library")
        
        elif st.session_state.get('admin_action') == "users":
            st.subheader("👥 User Management")
            
            tab1, tab2 = st.tabs(["Add/Remove Users", "View Users"])
            
            with tab1:
                with st.form("add_user_form"):
                    st.write("### Add New User")
                    new_user = st.text_input("Username")
                    new_email = st.text_input("Email")
                    new_password = st.text_input("Password", type="password")
                    
                    if st.form_submit_button("➕ Create User"):
                        if new_user.strip() and new_email.strip() and new_password:
                            if register_user(new_user, new_email, new_password, "user"):
                                st.success(f"User '{new_user}' created successfully!")
                                st.rerun()
                
                with st.form("remove_user_form"):
                    st.write("### Remove User")
                    remove_user = st.text_input("Enter Username to Remove")
                    if st.form_submit_button("❌ Remove User"):
                        if remove_user:
                            conn = sqlite3.connect('lms.db')
                            c = conn.cursor()
                            c.execute("DELETE FROM users WHERE username = ?", (remove_user,))
                            conn.commit()
                            conn.close()
                            st.success(f"User '{remove_user}' removed successfully!")
            
            with tab2:
                st.subheader("All Registered Users")
                conn = sqlite3.connect('lms.db')
                users_data = conn.execute("SELECT id, username, email, role FROM users").fetchall()
                conn.close()

                if users_data:
                    df = pd.DataFrame(users_data, columns=["ID", "Username", "Email", "Role"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No users registered yet")
        
        elif st.session_state.get('admin_action') == "assign":
            st.subheader("📖 Book Assignments")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Assign Books", "View Assignments", "Borrowed Books", "Returned Books", "Book Requests"])
            
            with tab1:
                with st.form("assign_book_form"):
                    book_title = st.text_input("Book Title")
                    username = st.text_input("Assign To Username")
                    if st.form_submit_button("📩 Assign Book"):
                        if book_title and username:
                            assign_book(book_title, username, st.session_state['user_id'])
            
            with tab2:
                st.subheader("Current Assignments")
                conn = sqlite3.connect('lms.db')
                assigned_books = conn.execute('''
                    SELECT b.title, u.username, a.assigned_date
                    FROM assigned_books a
                    JOIN books b ON a.book_id = b.id
                    JOIN users u ON a.user_id = u.id
                ''').fetchall()
                conn.close()
                
                if assigned_books:
                    df = pd.DataFrame(assigned_books, columns=["Book", "Assigned To", "Date"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No books currently assigned")
            
            with tab3:
                st.subheader("📚 Currently Borrowed Books")
                conn = sqlite3.connect('lms.db')
                borrowed_books = conn.execute('''
                    SELECT 
                        b.title as "Book Title",
                        u.username as "Borrowed By",
                        bb.borrowed_date as "Borrowed Date",
                        (julianday('now') - julianday(bb.borrowed_date)) as "Days Borrowed"
                    FROM borrowed_books bb
                    JOIN books b ON bb.book_id = b.id
                    JOIN users u ON bb.user_id = u.id
                    ORDER BY bb.borrowed_date DESC
                ''').fetchall()
                conn.close()
                
                if borrowed_books:
                    df = pd.DataFrame(borrowed_books, 
                                    columns=["Book Title", "Borrowed By", "Borrowed Date", "Days Borrowed"])
                    st.dataframe(df, use_container_width=True)
                    
                    # Add summary statistics
                    st.subheader("📊 Borrowing Statistics")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Books Borrowed", len(borrowed_books))
                    with col2:
                        # Filter out None values before calculating average
                        days_borrowed = [book[3] for book in borrowed_books if book[3] is not None]
                        avg_days = sum(days_borrowed) / len(days_borrowed) if days_borrowed else 0
                        st.metric("Average Borrow Duration", f"{avg_days:.1f} days")
                else:
                    st.info("No books currently borrowed")

            with tab4:
                st.subheader("📚 Returned Books History")
                conn = sqlite3.connect('lms.db')
                returned_books = conn.execute('''
                    SELECT 
                        b.title as "Book Title",
                        u.username as "Returned By",
                        r.returned_date as "Returned Date",
                        (SELECT bb.borrowed_date 
                         FROM borrowed_books bb 
                         WHERE bb.book_id = r.book_id AND bb.user_id = r.user_id
                         ORDER BY bb.borrowed_date DESC LIMIT 1) as "Borrowed Date",
                        (julianday(r.returned_date) - 
                         (SELECT julianday(bb.borrowed_date)
                          FROM borrowed_books bb 
                          WHERE bb.book_id = r.book_id AND bb.user_id = r.user_id
                          ORDER BY bb.borrowed_date DESC LIMIT 1)) as "Days Kept"
                    FROM returned_books r
                    JOIN books b ON r.book_id = b.id
                    JOIN users u ON r.user_id = u.id
                    ORDER BY r.returned_date DESC
                ''').fetchall()
                conn.close()
                
                if returned_books:
                    df = pd.DataFrame(returned_books, 
                                    columns=["Book Title", "Returned By", "Returned Date", 
                                            "Borrowed Date", "Days Kept"])
                    st.dataframe(df, use_container_width=True)
                    
                    # Add summary statistics
                    st.subheader("📊 Return Statistics")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Books Returned", len(returned_books))
                    with col2:
                        # Filter out None values before calculating average
                        days_kept = [book[4] for book in returned_books if book[4] is not None]
                        avg_days = sum(days_kept) / len(days_kept) if days_kept else 0
                        st.metric("Average Keeping Duration", f"{avg_days:.1f} days")
                else:
                    st.info("No books have been returned yet")

            with tab5:
                st.subheader("Book Requests")
                conn = sqlite3.connect('lms.db')
                requested_books = conn.execute('''
                    SELECT br.id, br.book_title, u.username, br.requested_on, br.status
                    FROM book_requests br
                    JOIN users u ON br.user_id = u.id
                    ORDER BY br.requested_on DESC
                ''').fetchall()
                conn.close()
                
                if requested_books:
                    df = pd.DataFrame(requested_books, columns=["ID", "Book", "Requested By", "Date", "Status"])
                    st.dataframe(df, use_container_width=True)
                    
                    with st.form("update_request_form"):
                        request_id = st.number_input("Request ID to Update", min_value=1)
                        new_status = st.selectbox("New Status", ["Pending", "Approved", "Rejected", "Procured"])
                        
                        if st.form_submit_button("🔄 Update Status"):
                            conn = sqlite3.connect('lms.db')
                            try:
                                c = conn.cursor()
                                c.execute('''
                                    UPDATE book_requests
                                    SET status = ?
                                    WHERE id = ?
                                ''', (new_status, request_id))
                                conn.commit()
                                st.success("Status updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                            finally:
                                conn.close()
                else:
                    st.info("No book requests pending")
            

# User Section (Learning Den)
# User Section (Learning Den)
elif page == "📖 Learning Den":
    st.title("📖 Learning Den")
    
    # Check if user is logged in
    if not st.session_state['user_logged_in']:
        user_choice = st.radio("Choose action:", ["🔑 User Login", "📝 User Signup"])
        if user_choice == "📝 User Signup":
            username = st.text_input("👤 Create User Username")
            email = st.text_input("📧 Enter User Email")
            password = st.text_input("🔒 Create User Password", type="password")
            confirm_password = st.text_input("🔒 Confirm User Password", type="password")
            if st.button("🚀 User Signup"):
                if username and email and password and confirm_password:
                    if password == confirm_password:
                        register_user(username, email, password, "user")
                    else:
                        st.error("❗ Passwords do not match!")
                else:
                    st.error("⚠️ Please fill all fields!")
        elif user_choice == "🔑 User Login":
            username = st.text_input("👤 User Username")
            password = st.text_input("🔒 User Password", type="password")
            if st.button("🚀 User Login"):
                if username and password:
                    if login_user(username, password, "user"):
                        st.session_state['user_logged_in'] = True
                        st.session_state['user_username'] = username
                        st.rerun()
    
    else:
        st.sidebar.subheader("📚 User Options")
        
        # Navigation options
        if st.sidebar.button("🏠 Go to Home"):
            st.session_state['user_action'] = "home"
        
        if st.sidebar.button("📚 Available Books"):
            st.session_state['user_action'] = "books"
        
        if st.sidebar.button("📖 Return Book"):
            st.session_state['user_action'] = "return"
        
        # Updated logout button (now a regular button like login)
        if st.sidebar.button("🚪 Logout", type="primary"):
            logout_user()
            st.rerun()
        
        # Main content area
        if st.session_state.get('user_action') == "home":
            st.rerun()
            
        elif st.session_state.get('user_action') == "books":
            st.subheader("📚 Available Books")
            conn = sqlite3.connect('lms.db')
            books_data = conn.execute("SELECT id, title, author, genre, price, pdf_link FROM books").fetchall()
            conn.close()

            table_data = []
            for i, row in enumerate(books_data):
                book_entry = {
                    "Sr. No.": i + 1,
                    "Title": row[1],
                    "Author": row[2],
                    "Genre": row[3],
                    "Price (₹)": row[4],
                    "PDF Link": f'<a href="{row[5]}" target="_blank">View PDF</a>' if row[5] else "No PDF"
                }
                table_data.append(book_entry)

            st.markdown(
                """
                <style>
                .stTable a {
                    color: blue;
                    text-decoration: underline;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.write(pd.DataFrame(table_data).to_html(escape=False, index=False), unsafe_allow_html=True)

            st.subheader("📖 Borrow Book")
            book_title = st.text_input("📘 Enter Book Title to Borrow")
            if st.button("📩 Borrow Book"):
                if book_title:
                    borrow_book(book_title, st.session_state['user_id'])
        
        elif st.session_state.get('user_action') == "return":
            st.subheader("📖 Return Book")
            book_title = st.text_input("📘 Enter Book Title to Return")
            if st.button("📩 Return Book"):
                if book_title:
                    # Check if the book is borrowed by the user
                    conn = sqlite3.connect('lms.db')
                    c = conn.cursor()
                    c.execute("SELECT id FROM books WHERE title = ?", (book_title,))
                    book = c.fetchone()
                    if book:
                        book_id = book[0]
                        user_id = st.session_state['user_id']
                        # Check if the book is borrowed by the user
                        c.execute("SELECT id FROM borrowed_books WHERE book_id = ? AND user_id = ?", (book_id, user_id))
                        borrowed_book = c.fetchone()
                        if borrowed_book:
                            # Move the book to returned_books
                            c.execute("INSERT INTO returned_books (book_id, user_id) VALUES (?, ?)", (book_id, user_id))
                            # Remove the book from borrowed_books
                            c.execute("DELETE FROM borrowed_books WHERE book_id = ? AND user_id = ?", (book_id, user_id))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ You have successfully returned '{book_title}'!")
                        else:
                            st.error(f"❌ You have not borrowed '{book_title}'.")
                    else:
                        st.error(f"❌ Book '{book_title}' not found.")
            
            st.subheader("📖 Request a Book")
            with st.form("request_book_form"):
                book_title = st.text_input("Enter book title to request")
                if st.form_submit_button("Submit Request"):
                    if book_title.strip():
                        conn = sqlite3.connect('lms.db')
                        try:
                            c = conn.cursor()
                            c.execute('''
                                INSERT INTO book_requests (book_title, user_id)
                                VALUES (?, ?)
                            ''', (book_title, st.session_state['user_id']))
                            conn.commit()
                            st.success(f"📖 Your request for '{book_title}' has been submitted!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error submitting request: {str(e)}")
                        finally:
                            conn.close()
                    else:
                        st.warning("Please enter a book title")
            
            st.subheader("Your Book Requests")
            conn = sqlite3.connect('lms.db')
            user_requests = conn.execute('''
                SELECT 
                    id,
                    book_title,
                    requested_on,
                    status
                FROM book_requests
                WHERE user_id = ?
                ORDER BY requested_on DESC
            ''', (st.session_state['user_id'],)).fetchall()
            conn.close()

            if user_requests:
                st.table(pd.DataFrame(user_requests,
                        columns=["Request ID", "Book Title", "Requested On", "Status"]))
            else:
                st.info("You haven't requested any books yet")
        

        