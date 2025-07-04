from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import uuid
import os
import json
import subprocess
from datetime import datetime
import shutil
from typing import Optional
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sqlite3
from contextlib import asynccontextmanager

# Import functions from other modules
from AI_feeds.predict import run_prediction
from pinata_uploader import upload_to_ipfs

# Global variables for real-time tracking
connected_clients = set()
prediction_stats = {
    "total_predictions": 0,
    "approved_predictions": 0,
    "accuracy": 96
}

# Real-time analytics data - Infrastructure and Operational Focus
analytics_data = {
    # Historical water consumption from uploaded CSV files
    "actual_consumption": {
        "monthly_trends": [
            {"month": "Jan", "consumption": 0, "year": 2025},
            {"month": "Feb", "consumption": 0, "year": 2025},
            {"month": "Mar", "consumption": 0, "year": 2025},
            {"month": "Apr", "consumption": 0, "year": 2025},
            {"month": "May", "consumption": 0, "year": 2025},
            {"month": "Jun", "consumption": 0, "year": 2025},
            {"month": "Jul", "consumption": 0, "year": 2025},
            {"month": "Aug", "consumption": 0, "year": 2025},
            {"month": "Sep", "consumption": 0, "year": 2025},
            {"month": "Oct", "consumption": 0, "year": 2025},
            {"month": "Nov", "consumption": 0, "year": 2025},
            {"month": "Dec", "consumption": 0, "year": 2025}
        ],
        "borough_totals": {
            "BRONX": 0,
            "BROOKLYN": 0,
            "MANHATTAN": 0,
            "QUEENS": 0,
            "STATEN_ISLAND": 0
        }
    },
    
    # System infrastructure metrics
    "infrastructure": {
        "system_uptime": 99.8,  # Percentage
        "data_processing_rate": 0,  # Files processed per hour
        "database_size_mb": 0,
        "api_response_time_ms": 0,
        "file_upload_success_rate": 100,
        "blockchain_connectivity": True,
        "ipfs_connectivity": True,
        "ai_model_status": "healthy"
    },
    
    # Data quality and processing metrics
    "data_quality": {
        "completeness_score": 95,  # Percentage of complete data
        "accuracy_score": 98,      # Data validation accuracy
        "timeliness_score": 92,    # How recent the data is
        "consistency_score": 97,   # Data consistency across sources
        "processed_files_count": 0,
        "failed_uploads_count": 0
    },
    
    # Water conservation and efficiency metrics (not prediction-based)
    "conservation": {
        "monthly_conservation_rate": [2.1, 1.8, 2.5, 3.2, 2.9, 3.1, 2.7, 2.4, 3.0, 2.8, 3.3, 3.5],  # Percentage reduction
        "conservation_targets_met": 8,  # Out of 12 months
        "total_water_saved_mgd": 15.7,  # Million gallons per day saved
        "efficiency_improvements": [
            {"category": "Infrastructure Upgrades", "savings_mgd": 5.2},
            {"category": "Leak Detection", "savings_mgd": 3.8},
            {"category": "Smart Meters", "savings_mgd": 4.1},
            {"category": "Public Awareness", "savings_mgd": 2.6}
        ]
    },
    
    # System operational metrics
    "operations": {
        "daily_processing_volume": [],  # Daily data processing volumes
        "system_alerts": {
            "critical": 0,
            "warning": 2,
            "info": 5
        },
        "service_health": {
            "api_server": "healthy",
            "database": "healthy", 
            "ai_engine": "healthy",
            "blockchain_oracle": "healthy",
            "file_storage": "healthy"
        },
        "performance_trends": {
            "avg_response_time": [45, 42, 38, 41, 39, 37, 40, 38, 35, 36, 34, 33],  # Last 12 hours in ms
            "throughput": [250, 265, 280, 275, 290, 305, 295, 310, 325, 315, 340, 335]  # Requests per hour
        }
    },
    
    # Real-time consumption monitoring (from actual data uploads)
    "real_time_consumption": [],
    "last_updated": datetime.now().isoformat(),
    "data_sources": ["csv_uploads", "manual_input", "system_monitoring"]
}

# Database initialization
def init_db():
    """Initialize SQLite database for tracking predictions"""
    conn = sqlite3.connect('dashboard_stats.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_stats (
            id INTEGER PRIMARY KEY,
            total_predictions INTEGER DEFAULT 0,
            approved_predictions INTEGER DEFAULT 0,
            accuracy REAL DEFAULT 96,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analytics data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            borough TEXT,
            consumption_value REAL,
            quality_metric TEXT,
            quality_value REAL,
            efficiency_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create real-time consumption tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS real_time_consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            borough TEXT NOT NULL,
            consumption REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analytics persistence table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_data_persistent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_json TEXT NOT NULL,
            source TEXT DEFAULT 'simulation',
            has_real_data BOOLEAN DEFAULT FALSE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create recent activities table for real-time activity feed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recent_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            metadata JSON,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT DEFAULT 'system',
            severity TEXT DEFAULT 'info'
        )
    ''')
    
    # Insert initial stats if table is empty
    cursor.execute('SELECT COUNT(*) FROM prediction_stats')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO prediction_stats (total_predictions, approved_predictions, accuracy)
            VALUES (0, 0, 96)
        ''')
    
    conn.commit()
    conn.close()

# Background task for keeping SSE connections alive (no data updates)
async def keep_connections_alive():
    """Background task to send heartbeat messages to keep SSE connections alive"""
    while True:
        try:
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            # Only send heartbeat, no data updates
            await broadcast_heartbeat()
        except Exception as e:
            print(f"Error in heartbeat task: {e}")

async def broadcast_heartbeat():
    """Send heartbeat to keep SSE connections alive without updating data"""
    if connected_clients:
        disconnected = []
        heartbeat_data = {
            "type": "heartbeat",
            "timestamp": datetime.now().isoformat(),
            "message": "Connection alive - waiting for prediction data"
        }
        
        for client in connected_clients:
            try:
                await client.put(f"data: {json.dumps(heartbeat_data)}\n\n")
            except Exception as e:
                print(f"Error sending heartbeat: {e}")
                disconnected.append(client)
        
        # Remove disconnected connections
        for conn in disconnected:
            connected_clients.remove(conn)

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    load_stats_from_db()
    # Load persisted analytics data from previous sessions
    has_persisted_data = load_analytics_from_db()
    if not has_persisted_data:
        print("📊 No persisted analytics data found - using default values")
    # Start background task for keeping connections alive (heartbeat only)
    task = asyncio.create_task(keep_connections_alive())
    print("✅ Analytics will ONLY update when predictions are generated")
    yield
    # Shutdown - cancel background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# Create FastAPI app with lifespan handler
app = FastAPI(
    title="BIWMS API",
             description="Blockchain Integrated Water Management System API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("data_uploads", exist_ok=True)
os.makedirs("AI_feeds/outputs", exist_ok=True)

# Database helper functions
def load_stats_from_db():
    """Load current stats from database"""
    global prediction_stats
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        cursor.execute('SELECT total_predictions, approved_predictions, accuracy FROM prediction_stats ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            prediction_stats["total_predictions"] = result[0]
            prediction_stats["approved_predictions"] = result[1]
            prediction_stats["accuracy"] = result[2]
            print(f"📂 Loaded prediction stats from DB: {prediction_stats}")
        else:
            print("⚠️ No prediction stats found in database - using default values")
        conn.close()
    except Exception as e:
        print(f"❌ Error loading stats from DB: {e}")

def save_analytics_to_db():
    """Save current analytics data to database for persistence"""
    global analytics_data
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        
        # Check if we have real prediction data
        has_real_data = False
        source = "simulation"
        if analytics_data.get("real_time_consumption"):
            has_real_data = any(item.get("source") == "real_prediction" for item in analytics_data["real_time_consumption"])
            if has_real_data:
                source = "real_prediction"
        
        # Clear old data and insert new
        cursor.execute('DELETE FROM analytics_data_persistent')
        cursor.execute('''
            INSERT INTO analytics_data_persistent (data_json, source, has_real_data)
            VALUES (?, ?, ?)
        ''', (json.dumps(analytics_data), source, has_real_data))
        
        conn.commit()
        conn.close()
        print(f"💾 Analytics data saved to database (source: {source}, real_data: {has_real_data})")
    except Exception as e:
        print(f"Error saving analytics to DB: {e}")

def load_analytics_from_db():
    """Load persisted analytics data from database"""
    global analytics_data
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        cursor.execute('SELECT data_json, source, has_real_data FROM analytics_data_persistent ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            data_json, source, has_real_data = result
            loaded_data = json.loads(data_json)
            analytics_data.update(loaded_data)
            print(f"📂 Loaded persisted analytics data (source: {source}, real_data: {has_real_data})")
            return True
        conn.close()
        return False
    except Exception as e:
        print(f"Error loading analytics from DB: {e}")
        return False

def update_stats_in_db():
    """Update stats in database"""
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE prediction_stats 
            SET total_predictions = ?, approved_predictions = ?, accuracy = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM prediction_stats ORDER BY id DESC LIMIT 1)
        ''', (prediction_stats["total_predictions"], prediction_stats["approved_predictions"], prediction_stats["accuracy"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating stats in DB: {e}")

def add_activity(activity_type: str, title: str, description: str = None, metadata: dict = None, severity: str = "info"):
    """Add a new activity to the real-time activity feed"""
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recent_activities (activity_type, title, description, metadata, severity)
            VALUES (?, ?, ?, ?, ?)
        ''', (activity_type, title, description, json.dumps(metadata) if metadata else None, severity))
        
        conn.commit()
        conn.close()
        
        print(f"📝 Activity logged: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Error logging activity: {e}")
        return False

def get_recent_activities(limit: int = 20):
    """Get recent activities for the activity feed"""
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT activity_type, title, description, metadata, timestamp, severity
            FROM recent_activities 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        activities = []
        for row in cursor.fetchall():
            activity_type, title, description, metadata, timestamp, severity = row
            
            activities.append({
                "type": activity_type,
                "title": title,
                "description": description,
                "metadata": json.loads(metadata) if metadata else {},
                "timestamp": timestamp,
                "severity": severity,
                "time_ago": get_time_ago(timestamp),
                "raw_timestamp": timestamp  # Send raw timestamp for frontend calculation
            })
        
        conn.close()
        return activities
        
    except Exception as e:
        print(f"❌ Error fetching activities: {e}")
        return []

def get_time_ago(timestamp_str: str) -> str:
    """Convert timestamp to human-readable time ago format"""
    try:
        from datetime import datetime
        # Parse the timestamp as local time (remove timezone info for consistency)
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '').replace('+00:00', ''))
        now = datetime.now()
        diff = now - timestamp
        
        total_seconds = diff.total_seconds()
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif total_seconds >= 3600:
            hours = int(total_seconds // 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif total_seconds >= 60:
            minutes = int(total_seconds // 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Unknown"

def reset_all_analytics():
    """Reset all analytics data and prediction stats to zero"""
    global analytics_data, prediction_stats
    
    try:
        # Reset in-memory analytics data to default values
        analytics_data = {
            "actual_consumption": {
                "monthly_trends": [
                    {"month": "Jan", "consumption": 0, "year": 2025},
                    {"month": "Feb", "consumption": 0, "year": 2025},
                    {"month": "Mar", "consumption": 0, "year": 2025},
                    {"month": "Apr", "consumption": 0, "year": 2025},
                    {"month": "May", "consumption": 0, "year": 2025},
                    {"month": "Jun", "consumption": 0, "year": 2025},
                    {"month": "Jul", "consumption": 0, "year": 2025},
                    {"month": "Aug", "consumption": 0, "year": 2025},
                    {"month": "Sep", "consumption": 0, "year": 2025},
                    {"month": "Oct", "consumption": 0, "year": 2025},
                    {"month": "Nov", "consumption": 0, "year": 2025},
                    {"month": "Dec", "consumption": 0, "year": 2025}
                ],
                "borough_totals": {
                    "BRONX": 0,
                    "BROOKLYN": 0,
                    "MANHATTAN": 0,
                    "QUEENS": 0,
                    "STATEN_ISLAND": 0
                }
            },
            
            # System infrastructure metrics
            "infrastructure": {
                "system_uptime": 99.8,  # Percentage
                "data_processing_rate": 0,  # Files processed per hour
                "database_size_mb": 0,
                "api_response_time_ms": 0,
                "file_upload_success_rate": 100,
                "blockchain_connectivity": True,
                "ipfs_connectivity": True,
                "ai_model_status": "healthy"
            },
            
            # Data quality and processing metrics
            "data_quality": {
                "completeness_score": 95,  # Percentage of complete data
                "accuracy_score": 98,      # Data validation accuracy
                "timeliness_score": 92,    # How recent the data is
                "consistency_score": 97,   # Data consistency across sources
                "processed_files_count": 0,
                "failed_uploads_count": 0
            },
            
            # Water conservation and efficiency metrics (not prediction-based)
            "conservation": {
                "monthly_conservation_rate": [2.1, 1.8, 2.5, 3.2, 2.9, 3.1, 2.7, 2.4, 3.0, 2.8, 3.3, 3.5],  # Percentage reduction
                "conservation_targets_met": 8,  # Out of 12 months
                "total_water_saved_mgd": 15.7,  # Million gallons per day saved
                "efficiency_improvements": [
                    {"category": "Infrastructure Upgrades", "savings_mgd": 5.2},
                    {"category": "Leak Detection", "savings_mgd": 3.8},
                    {"category": "Smart Meters", "savings_mgd": 4.1},
                    {"category": "Public Awareness", "savings_mgd": 2.6}
                ]
            },
            
            # System operational metrics
            "operations": {
                "daily_processing_volume": [],  # Daily data processing volumes
                "system_alerts": {
                    "critical": 0,
                    "warning": 2,
                    "info": 5
                },
                "service_health": {
                    "api_server": "healthy",
                    "database": "healthy", 
                    "ai_engine": "healthy",
                    "blockchain_oracle": "healthy",
                    "file_storage": "healthy"
                },
                "performance_trends": {
                    "avg_response_time": [45, 42, 38, 41, 39, 37, 40, 38, 35, 36, 34, 33],  # Last 12 hours in ms
                    "throughput": [250, 265, 280, 275, 290, 305, 295, 310, 325, 315, 340, 335]  # Requests per hour
                }
            },
            
            # Real-time consumption monitoring (from actual data uploads)
            "real_time_consumption": [],
            "last_updated": datetime.now().isoformat(),
            "data_sources": ["csv_uploads", "manual_input", "system_monitoring"]
        }
        
        # Reset prediction stats
        prediction_stats = {
            "total_predictions": 0,
            "approved_predictions": 0,
            "accuracy": 95.0
        }
        
        # Clear database tables
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        
        # Clear all analytics-related tables
        cursor.execute('DELETE FROM analytics_events')
        cursor.execute('DELETE FROM real_time_consumption')
        cursor.execute('DELETE FROM analytics_data_persistent')
        cursor.execute('DELETE FROM recent_activities')  # Clear activity feed too
        
        # Reset prediction stats in database
        cursor.execute('DELETE FROM prediction_stats')
        cursor.execute('''
            INSERT INTO prediction_stats (total_predictions, approved_predictions, accuracy)
            VALUES (0, 0, 95.0)
        ''')
        
        conn.commit()
        conn.close()
        
        # Log the reset activity
        add_activity("system", "System Reset", "Analytics system was reset to zero", 
                    {"reset_type": "full_reset"}, "warning")
        
        print("🔄 FULL ANALYTICS RESET COMPLETED")
        print("📊 All analytics data reset to default values")
        print("📈 Prediction stats reset to zero")
        print("🗃️  All database tables cleared")
        print("✨ System ready for fresh start")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analytics reset: {e}")
        return False

def extract_real_data_from_csv(file_path):
    """Extract real water consumption data from uploaded CSV file"""
    import pandas as pd
    import os
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Get file stats for system metrics
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        # Extract borough data (looking for common column patterns)
        borough_data = {}
        borough_columns = ['BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN_ISLAND']
        
        for borough in borough_columns:
            # Look for borough columns (case insensitive)
            matching_cols = [col for col in df.columns if borough.lower() in col.lower()]
            if matching_cols:
                borough_data[borough] = df[matching_cols[0]].sum() if not df[matching_cols[0]].isna().all() else 0
            else:
                borough_data[borough] = 0
        
        # Calculate monthly patterns from the data
        monthly_patterns = [0] * 12
        if len(df) >= 12:
            # If we have 12 or more rows, assume they represent months
            for i in range(min(12, len(df))):
                # Sum all numeric columns for each month
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    monthly_patterns[i] = df.iloc[i][numeric_cols].sum()
        else:
            # If less than 12 rows, distribute the data across current and recent months
            current_month = datetime.now().month - 1
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                total_consumption = df[numeric_cols].sum().sum()
                monthly_patterns[current_month] = total_consumption
        
        # Calculate data quality metrics
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isna().sum().sum()
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        quality_metrics = {
            "completeness_score": ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0,
            "accuracy_score": 95 + (len(numeric_columns) / len(df.columns) * 5) if len(df.columns) > 0 else 95,
            "timeliness_score": 100,  # Assume uploaded data is current
            "consistency_score": 90 + (10 * (1 - (df.duplicated().sum() / len(df)))) if len(df) > 0 else 90,
            "processed_files_count": 1,
            "failed_uploads_count": 0
        }
        
        # Infrastructure metrics from file processing
        infrastructure_metrics = {
            "data_processing_rate": max(1, len(df) / 60),  # Rows per minute as proxy
            "database_size_mb": file_size_mb,
            "api_response_time_ms": 35 + (file_size_mb * 2),  # Estimated based on file size
            "file_upload_success_rate": 100,
            "blockchain_connectivity": True,
            "ipfs_connectivity": True,
            "ai_model_status": "healthy"
        }
        
        # Conservation metrics (derived from consumption patterns)
        # Calculate conservation as percentage reduction from average consumption
        avg_consumption = sum(monthly_patterns) / 12 if monthly_patterns else 1
        conservation_data = {
            "monthly_conservation_rate": [
                max(0, min(5, ((avg_consumption - val) / avg_consumption * 100) * 0.05)) if avg_consumption > 0 else 0 
                for val in monthly_patterns
            ],
            "total_water_saved_mgd": sum(monthly_patterns) * 0.001,  # Convert to million gallons
            "conservation_targets_met": sum(1 for rate in monthly_patterns if rate > 0)
        }
        
        return {
            "borough_data": borough_data,
            "monthly_patterns": monthly_patterns,
            "data_quality_metrics": quality_metrics,
            "infrastructure_metrics": infrastructure_metrics,
            "conservation_data": conservation_data,
            "file_stats": {
                "size_mb": file_size_mb,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
        }
        
    except Exception as e:
        print(f"Error extracting data from CSV: {e}")
        return {
            "borough_data": {"BRONX": 0, "BROOKLYN": 0, "MANHATTAN": 0, "QUEENS": 0, "STATEN_ISLAND": 0},
            "monthly_patterns": [0] * 12,
            "data_quality_metrics": {"completeness_score": 0, "accuracy_score": 0, "timeliness_score": 0, "consistency_score": 0},
            "infrastructure_metrics": {},
            "conservation_data": {},
            "file_stats": {"size_mb": 0, "row_count": 0, "column_count": 0}
        }

def update_analytics_with_real_prediction(prediction_file_path, uploaded_file_path=None):
    """Update analytics data with real prediction results and uploaded data"""
    global analytics_data
    
    try:
        # Load the actual prediction results
        with open(prediction_file_path, 'r') as f:
            prediction_data = json.load(f)
        
        # Extract real data from uploaded CSV if available
        real_csv_data = None
        if uploaded_file_path and uploaded_file_path.endswith('.csv'):
            real_csv_data = extract_real_data_from_csv(uploaded_file_path)
        
        # Update actual consumption with REAL prediction data
        if "predicted_allocation" in prediction_data:
            for borough, data in prediction_data["predicted_allocation"].items():
                borough_upper = borough.upper()
                # Use actual predicted consumption values
                analytics_data["actual_consumption"]["borough_totals"][borough_upper] = data["consumption_hcf"]
        
        # Update monthly consumption trends with real data if available
        if real_csv_data and real_csv_data["monthly_patterns"]:
            monthly_data = real_csv_data["monthly_patterns"]
            current_year = datetime.now().year
            
            for i, value in enumerate(monthly_data):
                if i < len(analytics_data["actual_consumption"]["monthly_trends"]):
                    analytics_data["actual_consumption"]["monthly_trends"][i]["consumption"] = round(value, 2)
                    analytics_data["actual_consumption"]["monthly_trends"][i]["year"] = current_year
        
        # Update data quality metrics with real data
        if real_csv_data and real_csv_data["data_quality_metrics"]:
            for metric, value in real_csv_data["data_quality_metrics"].items():
                if metric in analytics_data["data_quality"]:
                    analytics_data["data_quality"][metric] = round(value, 2)
        
        # Update infrastructure metrics with real file processing data
        if real_csv_data and real_csv_data["infrastructure_metrics"]:
            for metric, value in real_csv_data["infrastructure_metrics"].items():
                if metric in analytics_data["infrastructure"]:
                    analytics_data["infrastructure"][metric] = value
        
        # Update conservation data with real patterns
        if real_csv_data and real_csv_data["conservation_data"]:
            if "monthly_conservation_rate" in real_csv_data["conservation_data"]:
                analytics_data["conservation"]["monthly_conservation_rate"] = real_csv_data["conservation_data"]["monthly_conservation_rate"][:12]
            if "total_water_saved_mgd" in real_csv_data["conservation_data"]:
                analytics_data["conservation"]["total_water_saved_mgd"] = real_csv_data["conservation_data"]["total_water_saved_mgd"]
        
        # Update system performance based on prediction confidence
        if "confidence_score" in prediction_data:
            confidence = prediction_data["confidence_score"]
            # Update system metrics based on AI performance
            analytics_data["infrastructure"]["system_uptime"] = min(99.9, max(95.0, confidence))
            analytics_data["infrastructure"]["ai_model_status"] = "healthy" if confidence >= 90 else "degraded"
            
            # Update data quality accuracy based on prediction confidence
            analytics_data["data_quality"]["accuracy_score"] = round(confidence, 2)
        
        # Update operational metrics
        current_time = datetime.now()
        analytics_data["operations"]["daily_processing_volume"].append({
            "timestamp": current_time.isoformat(),
            "files_processed": 1,
            "data_size_mb": real_csv_data["file_stats"]["size_mb"] if real_csv_data else 0
        })
        
        # Keep only last 24 hours of processing data
        cutoff_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        analytics_data["operations"]["daily_processing_volume"] = [
            entry for entry in analytics_data["operations"]["daily_processing_volume"]
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
        ]
        
        # Add real-time consumption data based on actual predictions
        if "predicted_allocation" in prediction_data:
            total_consumption = sum(data["consumption_hcf"] for data in prediction_data["predicted_allocation"].values())
            analytics_data["real_time_consumption"].append({
                "timestamp": prediction_data.get("timestamp", datetime.now().isoformat()),
                "total_consumption": total_consumption,
                "source": "real_prediction",
                "prediction_id": prediction_data.get("prediction_id")
            })
            
            # Keep only recent consumption data (last 100 entries)
            if len(analytics_data["real_time_consumption"]) > 100:
                analytics_data["real_time_consumption"] = analytics_data["real_time_consumption"][-100:]
        
        # Update system alerts based on data quality
        if real_csv_data:
            quality_score = real_csv_data["data_quality_metrics"]["completeness_score"]
            if quality_score < 80:
                analytics_data["operations"]["system_alerts"]["warning"] += 1
            elif quality_score < 60:
                analytics_data["operations"]["system_alerts"]["critical"] += 1
        
        # Update last_updated timestamp
        analytics_data["last_updated"] = datetime.now().isoformat()
        
        # Store the data in database
        save_analytics_to_db()
        
        print(f"🎯 Analytics updated with REAL prediction data from {prediction_file_path}")
        print(f"📊 Real borough consumption: {[f'{k}: {v:.1f} HCF' for k, v in analytics_data['actual_consumption']['borough_totals'].items()]}")
        print(f"🔍 Analytics data last_updated: {analytics_data['last_updated']}")
        print(f"💾 Analytics data saved to database successfully")
        
    except Exception as e:
        print(f"Error updating analytics with real prediction: {e}")
        # Fallback to simulation mode if real data update fails
        update_analytics_data_fallback()

def update_analytics_data_fallback():
    """Fallback method with simulated infrastructure data"""
    import random
    global analytics_data
    
    # Update infrastructure metrics with realistic variations
    analytics_data["infrastructure"]["system_uptime"] = min(99.9, max(95.0, 
        analytics_data["infrastructure"]["system_uptime"] + random.uniform(-0.1, 0.2)))
    
    analytics_data["infrastructure"]["api_response_time_ms"] = max(25, min(150,
        analytics_data["infrastructure"]["api_response_time_ms"] + random.uniform(-5, 10)))
    
    analytics_data["infrastructure"]["data_processing_rate"] = max(0.5, min(20,
        analytics_data["infrastructure"]["data_processing_rate"] + random.uniform(-1, 2)))
    
    # Update data quality metrics with small variations
    quality_metrics = ["completeness_score", "accuracy_score", "timeliness_score", "consistency_score"]
    for metric in quality_metrics:
        if metric in analytics_data["data_quality"]:
            current = analytics_data["data_quality"][metric]
            variation = random.uniform(-1, 2)  # Small improvements over time
            analytics_data["data_quality"][metric] = max(80, min(100, current + variation))
    
    # Update conservation rates with seasonal patterns
    current_month_idx = datetime.now().month - 1
    if current_month_idx < len(analytics_data["conservation"]["monthly_conservation_rate"]):
        base_rate = analytics_data["conservation"]["monthly_conservation_rate"][current_month_idx]
        variation = random.uniform(-0.2, 0.3)  # Conservation generally improves
        analytics_data["conservation"]["monthly_conservation_rate"][current_month_idx] = max(0, min(5, base_rate + variation))
    
    # Update system alerts occasionally
    if random.random() < 0.1:  # 10% chance of new alert
        alert_type = random.choice(["warning", "info"])
        analytics_data["operations"]["system_alerts"][alert_type] += 1
    
    # Update performance trends (last 12 data points)
    if len(analytics_data["operations"]["performance_trends"]["avg_response_time"]) >= 12:
        analytics_data["operations"]["performance_trends"]["avg_response_time"].pop(0)
        analytics_data["operations"]["performance_trends"]["throughput"].pop(0)
    
    # Add new performance data points
    last_response = analytics_data["operations"]["performance_trends"]["avg_response_time"][-1] if analytics_data["operations"]["performance_trends"]["avg_response_time"] else 35
    last_throughput = analytics_data["operations"]["performance_trends"]["throughput"][-1] if analytics_data["operations"]["performance_trends"]["throughput"] else 300
    
    new_response = max(25, min(60, last_response + random.uniform(-3, 2)))
    new_throughput = max(200, min(400, last_throughput + random.uniform(-15, 20)))
    
    analytics_data["operations"]["performance_trends"]["avg_response_time"].append(round(new_response))
    analytics_data["operations"]["performance_trends"]["throughput"].append(round(new_throughput))
    
    # Simulate processing volume updates
    current_hour = datetime.now().hour
    processing_entry = {
        "timestamp": datetime.now().isoformat(),
        "files_processed": random.randint(0, 3),
        "data_size_mb": round(random.uniform(0.1, 5.0), 2)
    }
    analytics_data["operations"]["daily_processing_volume"].append(processing_entry)
    
    # Keep only last 24 hours of processing data
    cutoff_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    analytics_data["operations"]["daily_processing_volume"] = [
        entry for entry in analytics_data["operations"]["daily_processing_volume"]
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
    ]
    
    analytics_data["last_updated"] = datetime.now().isoformat()

# Keep the old function name for simulation endpoint
def update_analytics_data(prediction_data=None):
    """Update analytics data - calls the appropriate method"""
    if prediction_data:
        # If we have real prediction data, use it
        update_analytics_with_real_prediction(prediction_data)
    else:
        # Otherwise use fallback simulation
        update_analytics_data_fallback()

def store_analytics_event(event_type, borough=None, consumption_value=None, quality_metric=None, quality_value=None, efficiency_score=None):
    """Store analytics events in database"""
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analytics_events (event_type, borough, consumption_value, quality_metric, quality_value, efficiency_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, borough, consumption_value, quality_metric, quality_value, efficiency_score))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing analytics event: {e}")

async def broadcast_stats_update():
    """Broadcast stats update to all connected clients"""
    if connected_clients:
        update_data = {
            "type": "stats_update",
            "stats": prediction_stats,
            "analytics": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
        message = f"data: {json.dumps(update_data)}\n\n"
        disconnected_clients = set()
        
        print(f"🔄 Broadcasting to {len(connected_clients)} connected clients")
        print(f"📊 Analytics data preview: Borough allocations: {list(analytics_data['actual_consumption']['borough_totals'].items())[:2]}...")
        
        for client in connected_clients:
            try:
                await client.put(message)
                print("✅ Message sent to client")
            except Exception as e:
                print(f"❌ Failed to send message to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        connected_clients.difference_update(disconnected_clients)
        
        if disconnected_clients:
            print(f"🧹 Removed {len(disconnected_clients)} disconnected clients")
    else:
        print("⚠️  No connected clients to broadcast to")

async def broadcast_analytics_update():
    """Broadcast analytics updates to all connected clients"""
    if connected_clients:
        disconnected = []
        update_data = {
            "type": "analytics_update",
            "analytics": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
        
        for client in connected_clients:
            try:
                await client.put(f"data: {json.dumps(update_data)}\n\n")
                print("📈 Analytics data broadcasted to client")
            except Exception as e:
                print(f"Error broadcasting analytics: {e}")
                disconnected.append(client)
        
        # Remove disconnected connections
        for conn in disconnected:
            connected_clients.remove(conn)

async def broadcast_activity_update():
    """Broadcast activity updates to all connected clients"""
    if connected_clients:
        disconnected = []
        recent_activities = get_recent_activities(10)  # Get latest 10 activities
        update_data = {
            "type": "activity_update",
            "activities": recent_activities,
            "timestamp": datetime.now().isoformat()
        }
        
        for client in connected_clients:
            try:
                await client.put(f"data: {json.dumps(update_data)}\n\n")
                print("🔔 Activity update broadcasted to client")
            except Exception as e:
                print(f"Error broadcasting activity: {e}")
                disconnected.append(client)
        
        # Remove disconnected connections
        for conn in disconnected:
            connected_clients.remove(conn)

def validate_file_extension(filename: str) -> bool:
    """Validate that the file has an allowed extension"""
    allowed_extensions = [".csv", ".json"]
    return any(filename.endswith(ext) for ext in allowed_extensions)

@app.post("/predict", response_class=JSONResponse)
async def predict(file: UploadFile = File(...), stakeholder_address: str = Form("")):
    """
    Upload a file with water consumption data, run predictions, 
    upload results to IPFS, and submit to the AIPredictionMultisig contract.
    
    Args:
        file: CSV or JSON file with water consumption data
        stakeholder_address: Ethereum address of the authenticated stakeholder
    
    Returns:
        JSON response with prediction details
    """
    
    # Debug logging
    print(f"📝 Received stakeholder_address: '{stakeholder_address}' (length: {len(stakeholder_address)})")
    
    # Validate stakeholder authorization
    if not stakeholder_address:
        print("❌ No stakeholder address provided")
        raise HTTPException(
            status_code=403, 
            detail="Access denied: Stakeholder wallet address required. Please connect your wallet and verify stakeholder status."
        )
    
    # Basic address format validation (40 hex characters after 0x)
    if not stakeholder_address.startswith('0x') or len(stakeholder_address) != 42:
        raise HTTPException(
            status_code=400,
            detail="Invalid stakeholder address format. Must be a valid Ethereum address."
        )
    
    print(f"🔐 Authorized stakeholder prediction request from: {stakeholder_address}")
    
    # Generate a unique prediction ID
    prediction_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="Only CSV or JSON files are allowed")
    
    # Create unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{prediction_id}{file_extension}"
    file_path = os.path.join("data_uploads", unique_filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run prediction on the uploaded file
        prediction_file_path = run_prediction(file_path)
        
        # Load the prediction JSON file to extract confidence score
        with open(prediction_file_path, "r") as f:
            prediction_data = json.load(f)
            confidence_score = prediction_data.get("confidence_score", 0)
            
        # Convert confidence score to integer between 0-100
        # AIPredictionMultisig contract expects uint8 (0-255)
        confidence_int = int(round(confidence_score))
        # Ensure it's within valid range
        confidence_int = max(0, min(100, confidence_int))
        
        # Upload prediction to IPFS
        ipfs_hash = upload_to_ipfs(prediction_file_path)
        
        # Submit to AIPredictionMultisig contract (with timeout for network reliability)
        oracle_result = subprocess.run(
            ["node", "oracle_submit.js", ipfs_hash, str(confidence_int)],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout for blockchain operations
        )
        
        # Update prediction stats
        prediction_stats["total_predictions"] += 1
        
        # Calculate new accuracy (simulated improvement with each successful prediction)
        current_accuracy = prediction_stats["accuracy"]
        new_accuracy = min(96, current_accuracy + 0.01)  # Gradual improvement
        prediction_stats["accuracy"] = round(new_accuracy, 2)
        
        # Update analytics data with REAL prediction data
        update_analytics_with_real_prediction(prediction_file_path, file_path)
        
        # Store analytics event with real data
        store_analytics_event("prediction_generated", consumption_value=confidence_int)
        
        # Update database
        update_stats_in_db()
        
        # Log prediction generation activity
        prediction_id = prediction_data.get("prediction_id", "N/A")
        borough_count = len(prediction_data.get("predicted_allocation", {}))
        add_activity(
            "prediction", 
            "New prediction generated",
            f"Stakeholder {stakeholder_address[:8]}... generated prediction {prediction_id} with {borough_count} borough allocations",
            {
                "prediction_id": prediction_id,
                "borough_count": borough_count,
                "oracle_hash": ipfs_hash,
                "confidence": confidence_int,
                "stakeholder_address": stakeholder_address
            },
            "success"
        )
        
        # Broadcast combined update to all connected clients
        await broadcast_stats_update()
        await broadcast_analytics_update()
        await broadcast_activity_update()
        
        print("🚀 PREDICTION CYCLE COMPLETED WITH REAL-TIME UPDATES")
        
        tx_result = None
        if oracle_result.returncode != 0:
            # Log the error but don't fail the request
            print(f"Contract submission warning: {oracle_result.stderr}")
        else:
            # Try to extract transaction ID or prediction ID from output
            output_lines = oracle_result.stdout.split('\n')
            for line in output_lines:
                if 'Transaction submitted:' in line:
                    tx_result = line.split('Transaction submitted:')[1].strip()
                elif 'Prediction submitted with ID:' in line:
                    prediction_blockchain_id = line.split('Prediction submitted with ID:')[1].strip()
        
        # Return successful response
        response = {
            "status": "success",
            "prediction_id": prediction_id,
            "ipfsHash": ipfs_hash,
            "confidence_score": confidence_int,
            "timestamp": timestamp,
            "prediction_file": os.path.basename(prediction_file_path),
            "oracle_address": os.environ.get("ORACLE_ADDRESS", "Not configured")
        }
        
        # Add transaction info if available
        if tx_result:
            response["transaction_hash"] = tx_result
            
        return response
        
    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=408,
            content={
                "status": "timeout",
                "message": "Oracle submission timed out after 60 seconds",
                "prediction": prediction_data if 'prediction_data' in locals() else None
            }
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    finally:
        # Cleanup: remove uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Cleaned up uploaded file: {file_path}")

@app.get("/stats/stream")
async def stream_stats():
    """Server-Sent Events endpoint for real-time dashboard updates"""
    async def event_generator():
        client_queue = asyncio.Queue()
        connected_clients.add(client_queue)
        
        try:
            # Load latest persisted analytics data before sending initial data
            load_analytics_from_db()
            
            # Send initial stats and analytics
            initial_data = {
                "type": "initial_data",
                "stats": prediction_stats,
                "analytics": analytics_data,
                "timestamp": datetime.now().isoformat()
            }
            initial_message = f"data: {json.dumps(initial_data)}\n\n"
            yield initial_message
            
            # Keep connection alive and send updates
            while True:
                try:
                    # Wait for new messages or send heartbeat every 30 seconds
                    message = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                    yield message
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield "data: {\"heartbeat\": true}\n\n"
                    
        except Exception as e:
            print(f"SSE client disconnected: {e}")
        finally:
            connected_clients.discard(client_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@app.get("/stats")
async def get_stats():
    """Get current dashboard statistics (always loads latest persisted data)"""
    # Always try to load the most recent persisted data to ensure consistency
    load_stats_from_db()
    return {"status": "success", "stats": prediction_stats}

@app.post("/stats/approve")
async def approve_prediction(request: dict):
    """Endpoint to track finalized prediction approvals (multi-signature complete)"""
    prediction_id = request.get("prediction_id")
    is_finalized = request.get("finalized", False)
    
    if not is_finalized:
        # This was an individual approval but prediction not yet finalized
        return {"status": "success", "message": "Individual approval recorded, waiting for finalization", "finalized": False}
    
    # Prediction is now finalized (2/2 approvals reached)
    prediction_stats["approved_predictions"] += 1
    update_stats_in_db()
    
    # Log finalization activity
    add_activity(
        "approval",
        "Prediction finalized", 
        f"Prediction #{prediction_id} reached required approvals and was finalized",
        {
            "prediction_id": prediction_id,
            "approval_count": prediction_stats["approved_predictions"],
            "approval_rate": round((prediction_stats["approved_predictions"] / prediction_stats["total_predictions"]) * 100, 1) if prediction_stats["total_predictions"] > 0 else 0
        },
        "success"
    )
    
    # Store finalization event (don't update analytics data as approvals don't change consumption)
    store_analytics_event("prediction_finalized")
    
    # Broadcast updates to all connected clients
    await broadcast_stats_update()
    await broadcast_activity_update()
    
    return {"status": "success", "message": "Prediction finalized", "finalized": True, "stats": prediction_stats}

@app.get("/analytics")
async def get_analytics():
    """Get current analytics data (always loads latest persisted data)"""
    # Always try to load the most recent persisted data to ensure consistency
    load_analytics_from_db()
    return {"analytics": analytics_data}

@app.post("/analytics/reset")
async def reset_analytics(clear_files: bool = False):
    """Reset all analytics data and prediction stats to zero"""
    print("🔄 ANALYTICS RESET REQUESTED")
    
    # Optionally clear prediction output files
    if clear_files:
        try:
            import glob
            # Clear prediction output files
            prediction_files = glob.glob("outputs/prediction_*.json")
            for file_path in prediction_files:
                os.remove(file_path)
                print(f"🗑️  Deleted: {file_path}")
            
            # Clear uploaded data files (optional)
            upload_files = glob.glob("data_uploads/*")
            for file_path in upload_files:
                os.remove(file_path)
                print(f"🗑️  Deleted: {file_path}")
            
            print(f"🧹 Cleared {len(prediction_files)} prediction files and {len(upload_files)} upload files")
        except Exception as e:
            print(f"⚠️  Error clearing files: {e}")
    
    success = reset_all_analytics()
    
    if success:
        # Broadcast the reset data to all connected clients
        await broadcast_stats_update()
        return {
            "message": f"Analytics system reset to zero successfully{' (files cleared)' if clear_files else ''}", 
            "analytics": analytics_data,
            "stats": prediction_stats,
            "files_cleared": clear_files,
            "status": "reset_complete"
        }
    else:
        return {
            "message": "Failed to reset analytics system",
            "status": "reset_failed"
        }

@app.post("/analytics/simulate")
async def simulate_analytics_update():
    """Simulate analytics data change (TESTING ONLY - normally only prediction generation updates analytics)"""
    print("⚠️  Manual simulation triggered - this is for testing only")
    update_analytics_data_fallback()
    store_analytics_event("simulation_update")
    await broadcast_analytics_update()
    return {"message": "Analytics data updated (SIMULATION - for testing only)", "analytics": analytics_data}

@app.post("/analytics/consumption")
async def add_consumption_data(borough: str, consumption: float):
    """Add real-time consumption data for a specific borough"""
    try:
        # Store in database
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO real_time_consumption (borough, consumption)
            VALUES (?, ?)
        ''', (borough.upper(), consumption))
        conn.commit()
        conn.close()
        
        # Update analytics data with real consumption
        analytics_data["actual_consumption"]["borough_totals"][borough.upper()] += consumption * 0.1  # Small cumulative effect
        
        # Add to real-time consumption tracking
        current_time = datetime.now()
        analytics_data["real_time_consumption"].append({
            "borough": borough.upper(),
            "consumption": consumption,
            "timestamp": current_time.isoformat(),
            "hour": current_time.hour,
            "source": "manual_input"
        })
        
        # Keep only recent data
        if len(analytics_data["real_time_consumption"]) > 100:
            analytics_data["real_time_consumption"] = analytics_data["real_time_consumption"][-100:]
        
        analytics_data["last_updated"] = current_time.isoformat()
        store_analytics_event("consumption_data", borough=borough.upper(), consumption_value=consumption)
        
        await broadcast_analytics_update()
        return {"message": "Consumption data added", "borough": borough, "consumption": consumption}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding consumption data: {str(e)}")

@app.get("/analytics/real-time")
async def get_real_time_consumption():
    """Get real-time consumption data"""
    try:
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT borough, consumption, timestamp
            FROM real_time_consumption
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        data = []
        for row in cursor.fetchall():
            borough, consumption, timestamp = row
            data.append({
                "borough": borough,
                "consumption": consumption,
                "timestamp": timestamp
            })
        
        conn.close()
        return {
            "status": "success",
            "data": data,
            "total_records": len(data)
        }
    except Exception as e:
        print(f"Error fetching real-time data: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/activities")
async def get_activities(limit: int = 20):
    """Get recent activities for the activity feed"""
    try:
        activities = get_recent_activities(limit)
        return {
            "status": "success",
            "activities": activities,
            "total": len(activities)
        }
    except Exception as e:
        print(f"Error fetching activities: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.post("/activities/add")
async def add_new_activity(
    activity_type: str,
    title: str,
    description: str = None,
    severity: str = "info"
):
    """Add a new activity (admin use)"""
    try:
        success = add_activity(activity_type, title, description, None, severity)
        if success:
            # Broadcast the activity update to all connected clients
            await broadcast_activity_update()
            return {"status": "success", "message": "Activity added"}
        else:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to add activity"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/prediction/{prediction_id}")
async def get_prediction(prediction_id: str):
    """
    Fetch prediction data by prediction ID or filename
    
    Args:
        prediction_id: Either the UUID prediction_id or the filename
    
    Returns:
        JSON prediction data with allocation details
    """
    try:
        # If it's a filename with .json extension, use it directly
        if prediction_id.endswith('.json'):
            file_path = os.path.join("outputs", prediction_id)
        else:
            # Search for the prediction file by ID or IPFS hash
            outputs_dir = "outputs"
            if not os.path.exists(outputs_dir):
                raise HTTPException(status_code=404, detail="Outputs directory not found")
            
            # Look for prediction files containing this ID or IPFS hash
            found_file = None
            for filename in os.listdir(outputs_dir):
                if filename.startswith('prediction_') and filename.endswith('.json'):
                    file_path = os.path.join(outputs_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            # Check if it matches by prediction ID
                            if data.get('prediction_id') == prediction_id:
                                found_file = file_path
                                break
                            # Check if it matches by IPFS hash in metadata
                            if data.get('metadata', {}).get('ipfs_hash') == prediction_id:
                                found_file = file_path
                                break
                            # Check if the prediction_id is an IPFS hash format (starts with Qm or baf)
                            if (prediction_id.startswith(('Qm', 'baf')) and 
                                data.get('metadata', {}).get('ipfs_hash') == prediction_id):
                                found_file = file_path
                                break
                    except:
                        continue
            
            # If still not found, try to match by filename timestamp with IPFS hash
            if not found_file and len(prediction_id) > 10:
                # For IPFS hashes, try to get the most recent prediction as fallback
                # This is a temporary solution until we implement proper IPFS mapping
                prediction_files = [f for f in os.listdir(outputs_dir) 
                                  if f.startswith('prediction_') and f.endswith('.json')]
                if prediction_files:
                    # Sort by timestamp and get the most recent one
                    prediction_files.sort(reverse=True)
                    found_file = os.path.join(outputs_dir, prediction_files[0])
            
            if not found_file:
                raise HTTPException(status_code=404, detail=f"Prediction with ID or hash {prediction_id} not found")
            file_path = found_file
        
        # Read and return the prediction data
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Prediction file not found")
        
        with open(file_path, 'r') as f:
            prediction_data = json.load(f)
        
        # Add file metadata
        prediction_data['file_info'] = {
            'filename': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        }
        
        return {
            "status": "success",
            "prediction": prediction_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prediction: {str(e)}")

@app.get("/predictions/list")
async def list_predictions(limit: int = 20):
    """
    List recent predictions with basic metadata
    
    Args:
        limit: Maximum number of predictions to return (default 20)
    
    Returns:
        List of predictions with summary data
    """
    try:
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            return {"status": "success", "predictions": []}
        
        predictions = []
        
        # Get all prediction files
        for filename in sorted(os.listdir(outputs_dir), reverse=True):
            if filename.startswith('prediction_') and filename.endswith('.json'):
                file_path = os.path.join(outputs_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Extract summary information
                    prediction_summary = {
                        'filename': filename,
                        'prediction_id': data.get('prediction_id'),
                        'timestamp': data.get('timestamp'),
                        'confidence_score': data.get('confidence_score'),
                        'total_consumption': data.get('metadata', {}).get('total_consumption_hcf'),
                        'number_of_boroughs': data.get('metadata', {}).get('number_of_boroughs'),
                        'file_size': os.path.getsize(file_path),
                        'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    }
                    
                    predictions.append(prediction_summary)
                    
                    if len(predictions) >= limit:
                        break
                        
                except Exception as e:
                    print(f"Error reading prediction file {filename}: {e}")
                    continue
        
        return {
            "status": "success",
            "predictions": predictions,
            "total_count": len(predictions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing predictions: {str(e)}")

@app.get("/reports")
async def get_system_reports():
    """
    Get comprehensive BIWMS system reports
    
    Returns:
        Water allocation reports, prediction analytics, blockchain activity, and system usage
    """
    try:
        # Get current stats from database
        conn = sqlite3.connect('dashboard_stats.db')
        cursor = conn.cursor()
        
        # Get prediction statistics
        cursor.execute('SELECT * FROM prediction_stats ORDER BY last_updated DESC LIMIT 1')
        stats_row = cursor.fetchone()
        current_stats = {
            "total_predictions": stats_row[1] if stats_row else 0,
            "approved_predictions": stats_row[2] if stats_row else 0,
            "accuracy": stats_row[3] if stats_row else 96,
            "last_updated": stats_row[4] if stats_row else datetime.now().isoformat()
        }
        
        # Get recent activities for system usage analysis
        cursor.execute('''
            SELECT activity_type, COUNT(*) as count, MAX(timestamp) as last_activity
            FROM recent_activities 
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY activity_type
        ''')
        activity_summary = []
        for row in cursor.fetchall():
            activity_summary.append({
                "type": row[0],
                "count": row[1],
                "last_activity": row[2]
            })
        
        # Get recent predictions data
        predictions_data = []
        outputs_dir = "outputs"
        if os.path.exists(outputs_dir):
            prediction_files = [f for f in os.listdir(outputs_dir) 
                              if f.startswith('prediction_') and f.endswith('.json')]
            prediction_files.sort(reverse=True)
            
            for filename in prediction_files[:10]:  # Get last 10 predictions
                file_path = os.path.join(outputs_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    predictions_data.append({
                        "filename": filename,
                        "prediction_id": data.get('prediction_id'),
                        "timestamp": data.get('timestamp'),
                        "confidence_score": data.get('confidence_score'),
                        "total_consumption": data.get('metadata', {}).get('total_consumption_hcf'),
                        "boroughs": list(data.get('predicted_allocation', {}).keys()),
                        "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    })
                except:
                    continue
        
        # Get analytics data for trends
        cursor.execute('''
            SELECT borough, AVG(consumption_value) as avg_consumption, COUNT(*) as data_points
            FROM analytics_events 
            WHERE event_type = 'consumption' AND timestamp >= datetime('now', '-30 days')
            GROUP BY borough
        ''')
        borough_trends = []
        for row in cursor.fetchall():
            borough_trends.append({
                "borough": row[0],
                "avg_consumption": round(row[1], 2) if row[1] else 0,
                "data_points": row[2]
            })
        
        # Calculate prediction accuracy trend (last 30 days)
        accuracy_trend = []
        if predictions_data:
            for pred in predictions_data:
                if pred.get('confidence_score'):
                    accuracy_trend.append({
                        "date": pred['timestamp'],
                        "accuracy": pred['confidence_score']
                    })
        
        # System utilization metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_activities,
                COUNT(CASE WHEN activity_type = 'prediction' THEN 1 END) as predictions,
                COUNT(CASE WHEN activity_type = 'approval' THEN 1 END) as approvals,
                COUNT(CASE WHEN activity_type = 'blockchain' THEN 1 END) as blockchain_txs
            FROM recent_activities 
            WHERE timestamp >= datetime('now', '-30 days')
        ''')
        utilization_row = cursor.fetchone()
        system_utilization = {
            "total_activities": utilization_row[0] if utilization_row else 0,
            "predictions_generated": utilization_row[1] if utilization_row else 0,
            "approvals_processed": utilization_row[2] if utilization_row else 0,
            "blockchain_transactions": utilization_row[3] if utilization_row else 0
        }
        
        conn.close()
        
        # Compile comprehensive report
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_period": "Last 30 days",
                "report_type": "BIWMS System Report"
            },
            "prediction_analytics": {
                "current_stats": current_stats,
                "recent_predictions": predictions_data,
                "accuracy_trend": accuracy_trend,
                "total_predictions_30d": len(predictions_data)
            },
            "water_allocation": {
                "borough_trends": borough_trends,
                "total_boroughs_active": len(borough_trends),
                "avg_daily_allocations": round(len(predictions_data) / 30, 2) if predictions_data else 0
            },
            "system_utilization": system_utilization,
            "activity_summary": activity_summary,
            "blockchain_status": {
                "network": "BSC Testnet",
                "contract_address": os.environ.get("SMART_CONTRACT_ADDRESS", "Not configured"),
                "total_approvals": current_stats["approved_predictions"],
                "approval_rate": round((current_stats["approved_predictions"] / max(current_stats["total_predictions"], 1)) * 100, 2)
            },
            "recommendations": []
        }
        
        # Generate recommendations based on data
        recommendations = []
        
        if current_stats["total_predictions"] > 0:
            approval_rate = (current_stats["approved_predictions"] / current_stats["total_predictions"]) * 100
            if approval_rate < 50:
                recommendations.append("Low approval rate detected. Consider reviewing prediction accuracy or stakeholder engagement.")
            elif approval_rate > 90:
                recommendations.append("High approval rate indicates strong prediction confidence and stakeholder trust.")
        
        if len(predictions_data) < 5:
            recommendations.append("Consider increasing prediction frequency for better water allocation planning.")
        
        if not borough_trends:
            recommendations.append("No recent water allocation data found. Upload CSV files to generate borough-specific insights.")
        
        if system_utilization["blockchain_transactions"] == 0:
            recommendations.append("No blockchain transactions detected. Verify smart contract integration.")
        
        report["recommendations"] = recommendations
        
        return {
            "status": "success",
            "report": report
        }
        
    except Exception as e:
        print(f"Error generating system reports: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error", 
                "message": f"Failed to generate system reports: {str(e)}"
            }
        )

@app.get("/")
async def root():
    """Root endpoint to verify the API is running"""
    contract_address = os.environ.get("SMART_CONTRACT_ADDRESS", "Not configured")
    oracle_address = os.environ.get("ORACLE_ADDRESS", "Not configured")
    return {
        "message": "BIWMS API is running.",
        "smart_contract": contract_address,
        "oracle_address": oracle_address,
        "network": "BSC Testnet (Chain ID: 97)",
        "stats": prediction_stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 