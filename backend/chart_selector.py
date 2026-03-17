def select_chart_type(data: list, columns: list, user_query: str = "") -> dict:
    """Automatically select appropriate chart type based on data structure and query intent"""
    
    if not data or not columns:
        return {"type": "none", "reason": "No data available"}
    
    num_columns = len(columns)
    num_rows = len(data)
    
    # Analyze column types
    has_date = any("date" in col.lower() or "month" in col.lower() or "year" in col.lower() for col in columns)
    has_numeric = any(isinstance(data[0].get(col), (int, float)) for col in columns if col in data[0])
    has_category = any(isinstance(data[0].get(col), str) for col in columns if col in data[0])
    
    # Check query intent
    query_lower = user_query.lower()
    
    # Keywords that suggest user wants a chart/visualization
    chart_keywords = ["show", "visualize", "chart", "graph", "trend", "compare", "distribution", 
                      "breakdown", "analysis", "pattern", "growth", "decline", "performance", "by category", "by product"]
    
    # Keywords that suggest user wants just data/numbers (no chart)
    no_chart_keywords = ["list", "get", "fetch", "retrieve", "tell me", "what are", "how many", 
                         "count", "total", "sum", "average", "details", "show me"]
    
    # Check for explicit chart requests
    wants_chart = any(keyword in query_lower for keyword in chart_keywords)
    wants_data_only = any(keyword in query_lower for keyword in no_chart_keywords)
    
    # If user explicitly asks for data only, don't show chart
    if wants_data_only and not wants_chart:
        return {"type": "none", "reason": "User requested data summary only"}
    
    # If no numeric data, can't show meaningful chart
    if not has_numeric:
        return {"type": "none", "reason": "No numeric data for visualization"}
    
    # Decision logic for chart type
    if num_columns == 2 and has_date and has_numeric:
        return {
            "type": "line",
            "reason": "Time series data detected",
            "xAxis": columns[0],
            "yAxis": columns[1]
        }
    
    elif num_columns == 2 and has_category and has_numeric:
        if num_rows <= 15:
            return {
                "type": "bar",
                "reason": "Categorical comparison",
                "xAxis": columns[0],
                "yAxis": columns[1]
            }
        else:
            return {
                "type": "bar",
                "reason": "Categorical comparison",
                "xAxis": columns[0],
                "yAxis": columns[1]
            }
    
    elif num_columns == 2 and has_numeric:
        if num_rows <= 8:
            return {
                "type": "pie",
                "reason": "Distribution data",
                "nameKey": columns[0],
                "dataKey": columns[1]
            }
        else:
            return {
                "type": "bar",
                "reason": "Comparison data",
                "xAxis": columns[0],
                "yAxis": columns[1]
            }
    
    elif num_columns >= 3:
        numeric_cols = [col for col in columns if isinstance(data[0].get(col), (int, float))]
        if len(numeric_cols) >= 2 and num_rows <= 20:
            return {
                "type": "multibar",
                "reason": "Multiple metrics comparison",
                "xAxis": columns[0],
                "yAxis": numeric_cols
            }
        else:
            return {
                "type": "none",
                "reason": "Complex data structure - showing summary only"
            }
    
    else:
        return {
            "type": "none",
            "reason": "Data summary view",
            "columns": columns
        }

def prepare_chart_data(data: list, chart_config: dict) -> dict:
    """Prepare data in the format required by the frontend chart library"""
    
    chart_type = chart_config.get("type")
    
    if chart_type == "none":
        return {
            "type": "none",
            "data": data,
            "reason": chart_config.get("reason", "No chart needed")
        }
    
    elif chart_type in ["bar", "line"]:
        return {
            "type": chart_type,
            "data": data,
            "xAxis": chart_config.get("xAxis"),
            "yAxis": chart_config.get("yAxis")
        }
    
    elif chart_type == "pie":
        return {
            "type": "pie",
            "data": data,
            "nameKey": chart_config.get("nameKey"),
            "dataKey": chart_config.get("dataKey")
        }
    
    elif chart_type == "multibar":
        return {
            "type": "multibar",
            "data": data,
            "xAxis": chart_config.get("xAxis"),
            "yAxis": chart_config.get("yAxis")
        }
    
    return {"type": "none", "data": data}
