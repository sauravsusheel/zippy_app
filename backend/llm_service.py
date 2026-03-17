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

# Common SQL patterns to avoid API calls
COMMON_PATTERNS = {
    "total": "SELECT SUM({numeric_col}) as total FROM {table}",
    "average": "SELECT AVG({numeric_col}) as average FROM {table}",
    "count": "SELECT COUNT(*) as count FROM {table}",
    "max": "SELECT MAX({numeric_col}) as maximum FROM {table}",
    "min": "SELECT MIN({numeric_col}) as minimum FROM {table}",
    "top": "SELECT {col}, COUNT(*) as count FROM {table} GROUP BY {col} ORDER BY count DESC LIMIT 10",
    "by": "SELECT {group_col}, SUM({numeric_col}) as total FROM {table} GROUP BY {group_col}",
}

def _get_cache_key(query: str, table_name: str) -> str:
    """Generate cache key for a query"""
    key_str = f"{query}:{table_name}".lower()
    return hashlib.md5(key_str.encode()).hexdigest()

def _try_pattern_match(user_query: str, table_name: str) -> Optional[str]:
    """Try to match query to common patterns without API call"""
    query_lower = user_query.lower()
    
    # Pattern matching for common queries
    if "total" in query_lower and ("sum" in query_lower or "revenue" in query_lower or "sales" in query_lower):
        return f"SELECT SUM(revenue) as total FROM {table_name}"
    
    if "average" in query_lower or "avg" in query_lower:
        return f"SELECT AVG(revenue) as average FROM {table_name}"
    
    if "count" in query_lower or "how many" in query_lower:
        return f"SELECT COUNT(*) as count FROM {table_name}"
    
    if "top" in query_lower or "highest" in query_lower or "best" in query_lower:
        return f"SELECT * FROM {table_name} ORDER BY revenue DESC LIMIT 10"
    
    if "lowest" in query_lower or "worst" in query_lower:
        return f"SELECT * FROM {table_name} ORDER BY revenue ASC LIMIT 10"
    
    if "by region" in query_lower or "by category" in query_lower or "by product" in query_lower:
        return f"SELECT * FROM {table_name} LIMIT 100"
    
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
        schema_context = f"Database schema:\n{schema_info}\n\nFocus on table: {table_name}"
        
        prompt = f"""You are a SQL expert. Convert the following natural language question into a SQL query.

Database Schema:
{schema_context}

Question: {user_query}

Generate ONLY the SQL query without any explanation. The query should be valid SQL that can be executed directly.
Return only the SQL query, nothing else."""

        try:
            print(f"🔄 Calling Gemini API for SQL generation...")
            last_api_call = time.time()
            
            model = genai.GenerativeModel("gemini-2.0-flash")
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
    Generate business insights from query results
    DISABLED by default to save API quota
    
    Args:
        user_query: Original user query
        query_result: Query results as list of dictionaries
    
    Returns:
        Generated insights or None
    """
    # Insights generation is disabled to minimize API calls
    # Uncomment below to enable (uses API quota)
    
    # try:
    #     if not GEMINI_API_KEY:
    #         return None
    #     
    #     # Check cache first
    #     cache_key = _get_cache_key(f"insights:{user_query}", "insights")
    #     if cache_key in query_cache:
    #         return query_cache[cache_key]
    #     
    #     # Convert results to formatted string (limit to first 10 rows)
    #     result_text = ""
    #     for i, row in enumerate(query_result[:10]):
    #         result_text += f"Row {i+1}: {row}\n"
    #     
    #     prompt = f"""You are a business analyst. Analyze the following data and provide insights.
    # 
    # Original Question: {user_query}
    # 
    # Data Results:
    # {result_text}
    # 
    # Provide insights including:
    # 1. Key trends or patterns
    # 2. Highest and lowest values
    # 3. Business recommendations
    # 4. Notable observations
    # 
    # Keep the response concise and actionable."""
    #     
    #     model = genai.GenerativeModel("gemini-2.0-flash")
    #     response = model.generate_content(prompt)
    #     
    #     if response and response.text:
    #         insights = response.text.strip()
    #         query_cache[cache_key] = insights
    #         return insights
    #     
    #     return None
    # 
    # except Exception as e:
    #     print(f"Error generating insights: {e}")
    #     return None
    
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


