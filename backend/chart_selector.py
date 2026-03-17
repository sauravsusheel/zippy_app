def select_chart_type(data: list, columns: list) -> dict:
    """Automatically select appropriate chart type based on data structure"""
    
    if not data or not columns:
        return {"type": "table", "reason": "No data available"}
    
    num_columns = len(columns)
    num_rows = len(data)
    
    # Analyze column types
    has_date = any("date" in col.lower() or "month" in col.lower() or "year" in col.lower() for col in columns)
    has_numeric = any(isinstance(data[0].get(col), (int, float)) for col in columns if col in data[0])
    has_category = any(isinstance(data[0].get(col), str) for col in columns if col in data[0])
    
    # Decision logic
    if num_columns == 2 and has_date and has_numeric:
        return {
            "type": "line",
            "reason": "Time series data detected",
            "xAxis": columns[0],
            "yAxis": columns[1]
        }
    
    elif num_columns == 2 and has_category and has_numeric:
        if num_rows <= 10:
            return {
                "type": "bar",
                "reason": "Categorical comparison with few categories",
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
        if num_rows <= 6:
            return {
                "type": "pie",
                "reason": "Distribution data with few categories",
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
        # Multiple metrics - could use grouped bar or multiple charts
        numeric_cols = [col for col in columns if isinstance(data[0].get(col), (int, float))]
        if len(numeric_cols) >= 2:
            return {
                "type": "multibar",
                "reason": "Multiple metrics comparison",
                "xAxis": columns[0],
                "yAxis": numeric_cols
            }
        else:
            return {
                "type": "table",
                "reason": "Complex data structure",
                "columns": columns
            }
    
    else:
        return {
            "type": "table",
            "reason": "Default view for complex data",
            "columns": columns
        }

def prepare_chart_data(data: list, chart_config: dict) -> dict:
    """Prepare data in the format required by the frontend chart library"""
    
    chart_type = chart_config.get("type")
    
    if chart_type == "table":
        return {
            "type": "table",
            "data": data,
            "columns": chart_config.get("columns", [])
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
    
    return {"type": "table", "data": data}
