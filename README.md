# LLM-Based Database Management System 💬

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: In-Development](https://img.shields.io/badge/Status-In_Development-green.svg)

This repository contains the code for an intelligent Database Management System (DBMS) that translates **natural language questions into secure SQL queries**.

The system is designed to make data accessible to non-technical users, removing the barrier of needing to know SQL. It is the subject of a 4th-year Electrical and Electronics Engineering Design Project at Eskişehir Technical University and a TÜBİTAK 2209-A research project.

## 🎯 Core Features

* **Natural Language to SQL:** Uses advanced LLMs (like Llama 3, GPT-4, and Mistral) to understand user intent and generate corresponding SQL queries.
* **Security Firewall:** A key feature is the **Rule-Based Query Validator**. This layer intercepts and blocks unsafe SQL (e.g., `DROP`, `UPDATE`) to prevent errors or malicious commands, addressing a primary risk of LLM-based systems.
* **Smart Orchestration:** Leverages `LangChain` to manage the end-to-end process: user input -> LLM prompting -> validation -> database execution.
* **Lightweight & Portable:** Built on a `SQLite3` database backend, making it easy to set up and test.
* **Interactive UI:** Provides a simple web interface for query input and result visualization.

## 🏛️ System Architecture

The data flow is designed for accuracy and security:

1.  **User Interface:** The user enters a query in natural language (e.g., "How many sales did we have last month?").
2.  **LLM Model:** The query, along with the database schema, is sent to the LLM (e.g., Llama 3). The model generates a SQL query.
3.  **LangChain Middle Layer:** Manages this interaction and orchestrates the flow.
4.  **Rule-Based Query Validator:** The generated SQL is intercepted and checked for safety and consistency (e.g., no `DELETE`, `DROP`, etc.).
5.  **Database Execution:** If the query is safe, it's run against the `SQLite3` database.
6.  **Results / Visualization:** The data is returned to the user, often as a table or a visual chart.

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| Core Logic | Python 3.10+ |
| LLM & Orchestration | LangChain, Hugging Face `transformers`, PyTorch |
| Database | `SQLite3` |
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
    This project uses a "sales products" dataset. Run the following command *once* to create the `sales.sqlite3` database and populate it with data:
    ```bash
    python -m src.database --populate
    ```

### 4. Running the Application

Run the Streamlit web app:
```bash
streamlit run app.py
```

### 📁 Project Structure

```
.
├── app.py               # Streamlit entrypoint
├── notebooks/           # Jupyter notebooks for experiments
│   ├── 01-baseline-test.ipynb
│   └── 02-fine-tuning.ipynb
├── requirements.txt     # Python dependencies
├── src/                 # Core Python modules
│   ├── __init__.py
│   ├── app/             # User-facing interfaces (APIs, CLI, Streamlit UI)
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── cli_nl.py
│   │   ├── cli_sql.py
│   │   └── ui_streamlit.py
│   ├── config.py        # Application configuration
│   ├── database.py      # Database bootstrap utilities
│   ├── db/              # Database access helpers
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── inspect_db.py
│   ├── llm/             # LLM provider abstraction
│   │   ├── __init__.py
│   │   └── provider.py
│   ├── llm_chain.py     # LangChain prompts and orchestration
│   ├── nl2sql/          # Natural language → SQL engine
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── prompt_templates.py
│   ├── training/        # Dataset creation utilities
│   │   ├── __init__.py
│   │   └── dataset_builder.py
│   ├── validation/      # Rule-based SQL validation
│   │   ├── __init__.py
│   │   └── sql_validator.py
│   └── validator.py     # Legacy validation entrypoint
└── tests/               # Unit tests
    ├── __init__.py
    ├── test_db.py
    ├── test_nl2sql.py
    └── test_validator.py
```
