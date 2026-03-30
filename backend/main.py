from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
import shutil
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

# Verify Gemini API key is set
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  WARNING: GEMINI_API_KEY not found in .env file")
    print("Please create backend/.env with: GEMINI_API_KEY=your_key_here")

from database import execute_query, get_schema, init_database, DATABASE_PATH, upload_dataset, get_dataset_preview, list_tables, get_table_schema
from llm_service import generate_sql, generate_insights
from chart_selector import select_chart_type, prepare_chart_data
from auth_database import init_auth_database, register_user, get_user_by_employee_id, get_all_users
from face_recognition_service import encode_face_from_image, compare_faces, detect_face_in_image, find_best_match
from token_service import generate_token, verify_token

app = FastAPI(title="Zippy API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Query history storage
query_history = []

# Active dataset tracking
active_dataset = {
    "table_name": "sales",
    "uploaded": False,
    "file_name": None
}

class QueryRequest(BaseModel):
    query: str
    table_name: str = None

from typing import Optional

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[list] = None
    chart_config: Optional[dict] = None
    insights: Optional[str] = None
    error: Optional[str] = None

class SignupRequest(BaseModel):
    employee_id: str
    company_unique_id: str
    face_image: str  # Base64 encoded image

class LoginRequest(BaseModel):
    face_image: str  # Base64 encoded image

class AuthResponse(BaseModel):
    success: bool
    message: str = None
    token: str = None
    user_id: int = None
    employee_id: str = None
    error: str = None
    chart_config: dict = None
    insights: str = None
    error: str = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and LLM on startup"""
    print("\n" + "=" * 60)
    print("  ZIPPY - STARTING UP (GEMINI MODE)")
    print("=" * 60)
    
    # Initialize Gemini LLM
    from llm_service import initialize_llm
    llm_status = initialize_llm()
    
    # Initialize database
    if not os.path.exists(DATABASE_PATH):
        print("Initializing database...")
        init_database()
    else:
        print(f"✓ Database found: {DATABASE_PATH}")
    
    # Initialize authentication database
    init_auth_database()
    
    print("✓ Backend startup complete")
    print("=" * 60 + "\n")

@app.get("/")
async def root():
    return {"message": "Zippy API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Register a new user with face recognition"""
    try:
        # Validate inputs
        if not request.employee_id or not request.company_unique_id:
            raise HTTPException(status_code=400, detail="Employee ID and Company ID are required")
        
        if not request.face_image:
            raise HTTPException(status_code=400, detail="Face image is required")
        
        # Decode base64 image
        try:
            import base64
            image_data = base64.b64decode(request.face_image)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect face in image
        if not detect_face_in_image(image_data):
            return AuthResponse(
                success=False,
                error="No face detected in image. Please try again with a clear face photo."
            )
        
        # Encode face
        face_encoding = encode_face_from_image(image_data)
        if not face_encoding:
            return AuthResponse(
                success=False,
                error="Could not process face. Please try again."
            )
        
        # Register user
        result = register_user(request.employee_id, request.company_unique_id, face_encoding)
        
        if result["success"]:
            return AuthResponse(
                success=True,
                message="Registration successful! You can now login with your face.",
                user_id=result["user_id"]
            )
        else:
            return AuthResponse(
                success=False,
                error=result["error"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        return AuthResponse(
            success=False,
            error=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate user with face recognition"""
    try:
        if not request.face_image:
            raise HTTPException(status_code=400, detail="Face image is required")
        
        # Decode base64 image
        try:
            import base64
            image_data = base64.b64decode(request.face_image)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect face in image
        if not detect_face_in_image(image_data):
            return AuthResponse(
                success=False,
                error="No face detected. Please try again."
            )
        
        # Encode face
        test_encoding = encode_face_from_image(image_data)
        if not test_encoding:
            return AuthResponse(
                success=False,
                error="Could not process face. Please try again."
            )
        
        # Get all registered users
        users = get_all_users()
        if not users:
            return AuthResponse(
                success=False,
                error="No registered users found."
            )
        
        # Flatten all face encodings from all users
        all_encodings = []
        user_mapping = []  # Maps encoding index to user
        
        for user in users:
            for encoding in user.get("face_encodings", []):
                all_encodings.append(encoding)
                user_mapping.append(user)
        
        if not all_encodings:
            return AuthResponse(
                success=False,
                error="No face encodings found. Please register first."
            )
        
        # Find best match
        best_match_index, distance = find_best_match(test_encoding, all_encodings)
        
        if best_match_index is not None:
            matched_user = user_mapping[best_match_index]
            
            # Generate JWT token
            token = generate_token(matched_user["id"], matched_user["employee_id"])
            
            return AuthResponse(
                success=True,
                message="Face recognized! Welcome back.",
                token=token,
                user_id=matched_user["id"],
                employee_id=matched_user["employee_id"]
            )
        else:
            return AuthResponse(
                success=False,
                error="Face not recognized. Please try again or register first."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        return AuthResponse(
            success=False,
            error=f"Login failed: {str(e)}"
        )

@app.post("/api/auth/verify-token")
async def verify_token_endpoint(token: str):
    """Verify JWT token"""
    try:
        payload = verify_token(token)
        if payload:
            return {
                "success": True,
                "user_id": payload.get("user_id"),
                "employee_id": payload.get("employee_id")
            }
        else:
            return {"success": False, "error": "Invalid or expired token"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== END AUTHENTICATION ENDPOINTS ====================

@app.post("/api/upload-dataset")
async def upload_dataset_endpoint(file: UploadFile = File(...)):
    """Upload a CSV or Excel file and create a table"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls', '.json', '.pdf')):
            raise HTTPException(status_code=400, detail="Only CSV, XLSX, XLS, JSON and PDF files are supported")
        
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate table name from filename
        table_name = file.filename.split('.')[0].replace('-', '_').replace(' ', '_').lower()
        
        # Upload dataset to database
        result = upload_dataset(temp_path, table_name)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result.get("success"):
            # Update active dataset
            active_dataset["table_name"] = table_name
            active_dataset["uploaded"] = True
            active_dataset["file_name"] = file.filename
            
            return {
                "success": True,
                "table_name": table_name,
                "file_name": file.filename,
                "rows": result["rows"],
                "columns": result["columns"],
                "schema": result["schema"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to upload dataset"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dataset-preview")
async def get_preview(table_name: str = None):
    """Get preview of the active dataset"""
    try:
        table = table_name or active_dataset["table_name"]
        result = get_dataset_preview(table)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/active-dataset")
async def get_active_dataset():
    """Get information about the active dataset"""
    try:
        table_name = active_dataset["table_name"]
        schema = get_table_schema(table_name)
        preview = get_dataset_preview(table_name, limit=5)
        
        return {
            "success": True,
            "table_name": table_name,
            "file_name": active_dataset["file_name"],
            "uploaded": active_dataset["uploaded"],
            "schema": schema,
            "preview": preview
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/reset-dataset")
async def reset_dataset():
    """Reset to default sample dataset"""
    try:
        active_dataset["table_name"] = "sales"
        active_dataset["uploaded"] = False
        active_dataset["file_name"] = None
        
        return {"success": True, "message": "Dataset reset to default"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return dashboard data"""
    
    try:
        user_query = request.query.strip()
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Check if API key is configured
        if not os.getenv("GEMINI_API_KEY"):
            return QueryResponse(
                success=False,
                error="Gemini API key not configured. Please set GEMINI_API_KEY in .env file."
            )
        
        # Use specified table or active dataset
        table_name = request.table_name or active_dataset["table_name"]
        
        # Step 1: Get database schema — build rich context for the LLM
        table_schema = get_table_schema(table_name)
        
        # Build a detailed schema string with column names, types, and sample values
        if "columns" in table_schema:
            col_lines = "\n".join(
                f"  - {col['name']} ({col['type']})"
                for col in table_schema["columns"]
            )
            sample_rows = table_schema.get("sample_rows", [])
            sample_text = ""
            if sample_rows:
                sample_text = "\n\nSample rows:\n" + "\n".join(
                    str(row) for row in sample_rows
                )
            schema = f"Table: {table_name}\nColumns:\n{col_lines}{sample_text}"
        else:
            schema = get_schema()
        
        # Step 2: Generate SQL using Gemini
        sql_result = generate_sql(user_query, schema, table_name)
        
        if not sql_result["success"]:
            return QueryResponse(
                success=False,
                error=f"SQL generation failed: {sql_result['error']}"
            )
        
        sql_query = sql_result["sql"]
        
        # Step 3: Execute SQL query
        query_result = execute_query(sql_query)
        
        if not query_result["success"]:
            return QueryResponse(
                success=False,
                sql=sql_query,
                error=f"Query execution failed: {query_result['error']}"
            )
        
        data = query_result["data"]
        columns = query_result["columns"]
        
        # Step 4: Select appropriate chart type
        chart_config = select_chart_type(data, columns, user_query)
        chart_data = prepare_chart_data(data, chart_config)
        
        # Step 5: Generate insights
        insights = generate_insights(user_query, data)
        
        # Step 6: Save to history
        query_history.append({
            "query": user_query,
            "sql": sql_query,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(data),
            "table": table_name
        })
        
        return QueryResponse(
            success=True,
            sql=sql_query,
            data=data,
            chart_config=chart_data,
            insights=insights
        )
    
    except Exception as e:
        return QueryResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@app.post("/api/generate-insights")
async def generate_insights_endpoint(request: QueryRequest):
    """Generate AI insights for query results"""
    try:
        user_query = request.query.strip()
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Check if API key is configured
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=400, detail="Gemini API key not configured")
        
        # Use specified table or active dataset
        table_name = request.table_name or active_dataset["table_name"]
        
        # Get database schema
        schema = get_schema()
        
        # Generate SQL using Gemini
        sql_result = generate_sql(user_query, schema, table_name)
        
        if not sql_result["success"]:
            raise HTTPException(status_code=400, detail=f"SQL generation failed: {sql_result['error']}")
        
        sql_query = sql_result["sql"]
        
        # Execute SQL query
        query_result = execute_query(sql_query)
        
        if not query_result["success"]:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {query_result['error']}")
        
        data = query_result["data"]
        
        # Generate insights using Gemini
        insights = generate_insights(user_query, data)
        
        return {
            "success": True,
            "insights": insights,
            "data_summary": {
                "record_count": len(data),
                "columns": query_result["columns"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    """Get query history"""
    return {"history": query_history[-10:]}

@app.post("/api/reset-database")
async def reset_database():
    """Reset database with fresh sample data"""
    try:
        init_database()
        active_dataset["table_name"] = "sales"
        active_dataset["uploaded"] = False
        active_dataset["file_name"] = None
        return {"success": True, "message": "Database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
