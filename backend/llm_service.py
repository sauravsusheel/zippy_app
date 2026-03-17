"""
LLM Service - Google Gemini API Integration with Advanced Optimization
Handles SQL generation with aggressive caching and rate limiting
Minimizes API calls to prevent quota exhaustion
"""

import google.generativeai as genai
import os
import hashlib
import json
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Query cache with timestamps
query_cache = {}
last_api_call = 0
MIN_API_CALL_INTERVAL = 2  # Minimum 2 seconds between API calls

def _get_cache_key(query: str, table_name: str) -> str:
    """Generate cache key for a query"""
    key_str = f"{query}:{table_name}".lower()
    return hashlib.md5(key_str.encode()).hexdigest()

def _try_pattern_match(user_query: str, table_name: str) -> Optional[str]:
    """
    Lightweight pattern match for very simple queries only.
    Avoids hardcoded column names — those are handled by the LLM with schema context.
    """
    query_lower = user_query.lower()

    # Only match the most generic, schema-agnostic patterns
    if ("count" in query_lower or "how many" in query_lower) and not any(
        w in query_lower for w in ["by", "group", "category", "product", "per"]
    ):
        return f"SELECT COUNT(*) as total_count FROM {table_name}"

    return None

def initialize_llm() -> Dict[str, Any]:
    """
    Initialize LLM service and configure Gemini API
    
    Returns:
        Status dictionary
    """
    try:
        if not GEMINI_API_KEY:
            print("⚠️  WARNING: GEMINI_API_KEY not found in .env file")
            print("Please create backend/.env with: GEMINI_API_KEY=your_key_here")
            return {
                "connected": False,
                "status": "API key not configured"
            }
        
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"✅ Gemini API configured successfully")
        print(f"   API Key length: {len(GEMINI_API_KEY)}")
        print(f"   Optimization: Caching + Pattern Matching + Rate Limiting")
        
        return {
            "connected": True,
            "status": "Connected"
        }
    
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {e}")
        return {
            "connected": False,
            "status": f"Error: {str(e)}"
        }

def generate_sql(user_query: str, schema_info: str, table_name: str) -> Dict[str, Any]:
    """
    Generate SQL query from natural language using Gemini API
    Uses caching, pattern matching, and rate limiting to minimize API calls
    
    Args:
        user_query: Natural language query
        schema_info: Database schema information
        table_name: Target table name
    
    Returns:
        Dictionary with success status and SQL query
    """
    global last_api_call
    
    try:
        if not GEMINI_API_KEY:
            return {
                "success": False,
                "error": "Gemini API key not configured"
            }
        
        # Check cache first
        cache_key = _get_cache_key(user_query, table_name)
        if cache_key in query_cache:
            print(f"✓ Using cached result for query")
            return query_cache[cache_key]
        
        # Try pattern matching first (no API call)
        pattern_sql = _try_pattern_match(user_query, table_name)
        if pattern_sql:
            print(f"✓ Using pattern-matched SQL (no API call)")
            result = {
                "success": True,
                "sql": pattern_sql,
                "source": "pattern_match"
            }
            query_cache[cache_key] = result
            return result
        
        # Rate limiting: wait if needed
        time_since_last_call = time.time() - last_api_call
        if time_since_last_call < MIN_API_CALL_INTERVAL:
            wait_time = MIN_API_CALL_INTERVAL - time_since_last_call
            print(f"⏳ Rate limiting: waiting {wait_time:.1f}s before API call")
            time.sleep(wait_time)
        
        # Create schema context
        schema_context = schema_info
        
        prompt = f"""You are a SQL expert working with a SQLite database. Convert the user's question into a precise SQL query.

{schema_context}

User Question: {user_query}

Rules:
- Return ONLY the raw SQL query — no markdown, no backticks, no explanation
- Use ONLY the exact column names listed in the schema above
- The query must directly and completely answer the user's question
- Use GROUP BY + COUNT/SUM/AVG for aggregation questions (e.g. "most used", "total by", "average per")
- Use ORDER BY ... DESC LIMIT 10 for "top", "best", "highest", "most" questions
- Use ORDER BY ... ASC LIMIT 10 for "lowest", "worst", "least" questions
- Use GROUP BY date_column for trend/over-time questions
- Never generate SELECT 1 or placeholder queries
- If unsure about a column name, pick the closest match from the schema"""

        try:
            print(f"🔄 Calling Gemini API for SQL generation...")
            last_api_call = time.time()
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            
            if response and response.text:
                sql_query = response.text.strip()
                
                # Clean up the response
                if sql_query.startswith('```'):
                    sql_query = sql_query.split('```')[1]
                    if sql_query.startswith('sql'):
                        sql_query = sql_query[3:]
                sql_query = sql_query.strip()
                
                result = {
                    "success": True,
                    "sql": sql_query,
                    "source": "gemini_api"
                }
                
                # Cache the result
                query_cache[cache_key] = result
                return result
            
            return {
                "success": False,
                "error": "Failed to generate SQL query from Gemini"
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a quota error
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠️  Quota exceeded. Using fallback SQL generation.")
                fallback_sql = f"SELECT * FROM {table_name} LIMIT 100"
                return {
                    "success": True,
                    "sql": fallback_sql,
                    "source": "fallback",
                    "note": "Using fallback query due to API quota limit. Enable billing for unlimited access."
                }
            
            return {
                "success": False,
                "error": f"SQL generation error: {error_msg}"
            }
    
    except Exception as e:
        error_msg = str(e)
        return {
            "success": False,
            "error": f"SQL generation error: {error_msg}"
        }

def generate_insights(user_query: str, query_result: list) -> Optional[str]:
    """
    Generate natural language business insights from query results
    
    Args:
        user_query: Original user query
        query_result: Query results as list of dictionaries
    
    Returns:
        Generated insights or None
    """
    try:
        if not GEMINI_API_KEY or not query_result:
            return None
        
        # Check cache first
        cache_key = _get_cache_key(f"insights:{user_query}", "insights")
        if cache_key in query_cache:
            return query_cache[cache_key]
        
        # Convert results to formatted string (limit to first 20 rows)
        result_text = json.dumps(query_result[:20], indent=2, default=str)
        
        prompt = f"""You are a business analyst. Analyze the following data and provide a natural language response to the user's question.

User's Question: {user_query}

Data Results:
{result_text}

Provide a conversational, natural language response that:
1. Directly answers the user's question in 2-3 sentences
2. Highlights key findings and specific numbers
3. Mentions patterns or trends if visible
4. Provides actionable insights if relevant
5. Avoids technical jargon, bullet points, and emojis
6. Sounds like you're talking to a business colleague

Keep it concise and conversational."""
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        if response and response.text:
            insights = response.text.strip()
            query_cache[cache_key] = insights
            return insights
        
        return None
    
    except Exception as e:
        print(f"Error generating insights: {e}")
        return None


def clear_cache():
    """Clear the query cache"""
    global query_cache
    query_cache.clear()
    print("✓ Query cache cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return {
        "cached_queries": len(query_cache),
        "cache_size": len(str(query_cache))
    }


