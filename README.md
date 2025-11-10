# LLM-Based Database Management System 💬

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: In-Development](https://img.shields.io/badge/Status-In_Development-green.svg)

[cite_start]This repository contains the code for an intelligent Database Management System (DBMS) that translates **natural language questions into secure SQL queries**[cite: 16].

[cite_start]This system is designed to make data accessible to non-technical users, removing the barrier of needing to know SQL[cite: 17, 163]. [cite_start]It is the subject of a 4th-year Electrical and Electronics Engineering Design Project at Eskişehir Technical University  [cite_start]and a TÜBİTAK 2209-A research project.

## 🎯 Core Features

* [cite_start]**Natural Language to SQL:** Uses advanced LLMs (like Llama 3, GPT-4, and Mistral [cite: 19, 86, 163]) to understand user intent and generate corresponding SQL queries.
* [cite_start]**Security Firewall:** A key feature is the **Rule-Based Query Validator**[cite: 22, 93, 163]. [cite_start]This layer intercepts and blocks unsafe SQL (e.g., `DROP`, `UPDATE`) to prevent errors or malicious commands, addressing a primary risk of LLM-based systems[cite: 26, 124].
* [cite_start]**Smart Orchestration:** Leverages `LangChain` to manage the end-to-end process: user input -> LLM prompting -> validation -> database execution[cite: 23, 63, 92].
* [cite_start]**Lightweight & Portable:** Built on a `SQLite3` database backend, making it easy to set up and test[cite: 21, 67, 94].
* [cite_start]**Interactive UI:** Provides a simple web interface for query input and result visualization[cite: 90, 95].

## 🏛️ System Architecture

[cite_start]The data flow is designed for accuracy and security, based on the project's architectural diagram[cite: 96]:

1.  [cite_start]**User Interface:** The user enters a query in natural language (e.g., "How many sales did we have last month?")[cite: 90].
2.  [cite_start]**LLM Model:** The query, along with the database schema, is sent to the LLM (e.g., Llama 3)[cite: 91]. The model generates a SQL query.
3.  [cite_start]**LangChain Middle Layer:** Manages this interaction and orchestrates the flow[cite: 92].
4.  [cite_start]**Rule-Based Query Validator:** The generated SQL is intercepted and checked for safety and consistency (e.g., no `DELETE`, `DROP`, etc.)[cite: 93, 124].
5.  [cite_start]**Database Execution:** If the query is safe, it's run against the `SQLite3` database[cite: 94].
6.  [cite_start]**Results / Visualization:** The data is returned to the user, often as a table or a visual chart[cite: 95].

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| Core Logic | Python 3.10+ |
| LLM & Orchestration | LangChain, Hugging Face `transformers`, PyTorch |
| Database | [cite_start]`SQLite3` [cite: 21, 47, 67] |
| Web Interface | `Streamlit` |
| Data Handling | `Pandas` |
| Dev & Test | `pytest`, `python-dotenv` |

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.10 or higher
* An API key for an LLM provider (e.g., OpenAI for GPT-4).

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/llm-dbms.git](https://github.com/your-username/llm-dbms.git)
    cd llm-dbms
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Setup

1.  **Set up environment variables:**
    Create a file named `.env` in the root directory. This file is ignored by Git. Add your secret keys here:
    ```.env
    # Store your secret keys here
    # Example for using OpenAI's GPT-4
    OPENAI_API_KEY="sk-..."
    ```

2.  **Populate the database:**
    [cite_start]This project uses a "sales products" dataset[cite: 21, 77]. Run the following command *once* to create the `sales.sqlite3` database and populate it with data:
    ```bash
    python -m src.database --populate
    ```

### 4. Running the Application

Run the Streamlit web app:
```bash
streamlit run app.py

📁 Project Structure

.
├── app.py              # The main Streamlit application
├── .env                # Secret keys (e.g., API keys)
├── .gitignore          # Files to be ignored by Git
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── data/               # Holds raw data and the SQLite DB
│   └── sales.sqlite3
├── docs/               # Project proposals and design documents
│   └── Derya_Umut_Kulali_LLM_based_DBMS.pdf
│   └── EEEPRJ13.pdf
├── notebooks/          # Jupyter notebooks for experiments
│   ├── 01-baseline-test.ipynb
│   └── 02-fine-tuning.ipynb
├── src/                # Core Python modules
│   ├── __init__.py
│   ├── database.py       # DB connection, schema, and data loading
│   ├── llm_chain.py      # LangChain prompts and model logic
│   └── validator.py      # The security firewall (Rule-Based Validator)
└── tests/              # Unit tests
    └── test_validator.py