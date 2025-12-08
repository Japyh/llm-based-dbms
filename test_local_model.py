"""Quick test of the local fine-tuned model."""
from src.config import Settings
from src.llm.provider import get_llm_provider

def test_local_model():
    print("Initializing LocalHFLLMProvider...")
    settings = Settings()
    provider = get_llm_provider(settings)
    
    print(f"Using provider: {type(provider).__name__}")
    
    # Test with a sample question
    messages = [
        {
            "role": "system",
            "content": "You are a Text-to-SQL assistant for our SQLite sales database. "
                      "Return only a valid SQL SELECT query, with no explanation, no comments, "
                      "and no natural language. Never modify data or schema."
        },
        {
            "role": "user",
            "content": "Show me the top 10 customers by total sales."
        }
    ]
    
    print("\nGenerating SQL for: 'Show me the top 10 customers by total sales.'")
    print("(This will take a moment on first run to load the model...)\n")
    
    sql = provider.chat(messages)
    
    print("=" * 70)
    print("Generated SQL:")
    print(sql)
    print("=" * 70)
    
    # Test another query
    messages[1]["content"] = "How many products are in each product line?"
    print("\nGenerating SQL for: 'How many products are in each product line?'\n")
    
    sql = provider.chat(messages)
    
    print("=" * 70)
    print("Generated SQL:")
    print(sql)
    print("=" * 70)

if __name__ == "__main__":
    test_local_model()
