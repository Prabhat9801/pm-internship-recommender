# backend/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from recommender import load_internships, load_embeddings, save_embeddings, precompute_doc_embeddings_new, recommend, check_and_update_embeddings, recommend_with_validation
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

DATA_PATH = "internships.json"
EMBEDDINGS_PATH = "embeddings.json"

app = FastAPI(title="PM Internship Recommender API", version="2.0")

# CORS for frontend local dev (adjust origin for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ProfileRequest(BaseModel):
    education: str
    skills: str
    location: str
    top_k: int = 5

class ProfileRequestWithValidation(BaseModel):
    education: str
    skills: str
    location: str
    top_k: Optional[int] = 5
    use_validation: Optional[bool] = False

# Global variables to cache data and embeddings
cached_internships = None
cached_embeddings = None
last_check_time = 0

def get_current_data():
    """Get current internships and embeddings, updating if necessary"""
    global cached_internships, cached_embeddings, last_check_time
    
    internships, embeddings, updated = check_and_update_embeddings(
        DATA_PATH, EMBEDDINGS_PATH, cached_internships, cached_embeddings
    )
    
    if updated or cached_internships is None:
        cached_internships = internships
        cached_embeddings = embeddings
        print("✅ Data and embeddings updated/loaded")
    
    return cached_internships, cached_embeddings

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "PM Internship Recommender API is running",
        "version": "2.0",
        "internships_loaded": len(cached_internships) if cached_internships else 0,
        "status": "healthy"
    }

@app.post("/api/recommend")
def api_recommend(req: ProfileRequest):
    try:
        internships, embeddings = get_current_data()
        
        if not internships:
            raise HTTPException(status_code=404, detail="No internships data available")
        
        if not embeddings:
            raise HTTPException(status_code=500, detail="Embeddings not available")
        
        # Merge internships with their embeddings for recommendation
        internships_with_embeddings = []
        for internship in internships:
            internship_id = internship.get('id') or internship.get('title', '') + internship.get('org', '')
            if internship_id in embeddings:
                internship_copy = internship.copy()
                internship_copy['embedding'] = embeddings[internship_id]
                internships_with_embeddings.append(internship_copy)
        
        results = recommend(internships_with_embeddings, req.education, req.skills, req.location, top_k=req.top_k)
        
        return {
            "query": {
                "education": req.education, 
                "skills": req.skills, 
                "location": req.location
            }, 
            "recommendations": results,
            "metadata": {
                "total_internships": len(internships),
                "internships_with_embeddings": len(internships_with_embeddings),
                "returned_recommendations": len(results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend/validated")
def api_recommend_with_validation(req: ProfileRequestWithValidation):
    """Recommendation endpoint with enhanced input validation"""
    try:
        internships, embeddings = get_current_data()
        
        # Merge internships with their embeddings
        internships_with_embeddings = []
        for internship in internships:
            internship_id = internship.get('id') or internship.get('title', '') + internship.get('org', '')
            if internship_id in embeddings:
                internship_copy = internship.copy()
                internship_copy['embedding'] = embeddings[internship_id]
                internships_with_embeddings.append(internship_copy)
        
        if req.use_validation:
            results = recommend_with_validation(
                internships_with_embeddings,
                req.education,
                req.skills, 
                req.location,
                req.top_k
            )
        else:
            results = recommend(
                internships_with_embeddings,
                req.education,
                req.skills,
                req.location, 
                req.top_k
            )
        
        return {
            "query": {
                "education": req.education,
                "skills": req.skills,
                "location": req.location,
                "validation_used": req.use_validation
            },
            "recommendations": results
        }
        
    except Exception as e:
        print(f"Error in validated recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/internships")
def api_internships():
    try:
        internships, _ = get_current_data()
        return {"count": len(internships), "internships": internships}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
def api_stats():
    """Get API statistics and internship data insights"""
    try:
        internships, _ = get_current_data()
        
        if not internships:
            return {"message": "No internships loaded"}
        
        # Calculate statistics
        total_internships = len(internships)
        
        # Get unique values for filtering
        locations = set()
        skills = set()
        education_levels = set()
        organizations = set()
        
        for internship in internships:
            if internship.get("location"):
                locations.add(internship["location"])
            if internship.get("skills"):
                for skill in internship["skills"].split(","):
                    skills.add(skill.strip())
            if internship.get("required_education"):
                education_levels.add(internship["required_education"])
            if internship.get("org"):
                organizations.add(internship["org"])
        
        return {
            "total_internships": total_internships,
            "unique_locations": len(locations),
            "unique_skills": len(skills),
            "unique_education_levels": len(education_levels),
            "unique_organizations": len(organizations),
            "sample_locations": list(locations)[:10],
            "sample_skills": list(skills)[:15],
            "sample_education_levels": list(education_levels),
            "api_version": "2.0"
        }
        
    except Exception as e:
        print(f"Error generating stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/embeddings/status")
def api_embeddings_status():
    """Get status of embeddings"""
    try:
        internships, embeddings = get_current_data()
        
        total_internships = len(internships) if internships else 0
        total_embeddings = len(embeddings) if embeddings else 0
        
        # Check which internships have embeddings
        internships_with_embeddings = 0
        if internships and embeddings:
            for internship in internships:
                internship_id = internship.get('id') or internship.get('title', '') + internship.get('org', '')
                if internship_id in embeddings:
                    internships_with_embeddings += 1
        
        return {
            "total_internships": total_internships,
            "total_embeddings": total_embeddings,
            "internships_with_embeddings": internships_with_embeddings,
            "coverage_percentage": (internships_with_embeddings / total_internships * 100) if total_internships > 0 else 0,
            "embeddings_file_exists": os.path.exists(EMBEDDINGS_PATH),
            "internships_file_exists": os.path.exists(DATA_PATH)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/embeddings/recompute")
def api_recompute_embeddings():
    """Force recomputation of all embeddings"""
    try:
        global cached_internships, cached_embeddings
        
        print("🔄 Force recomputing embeddings...")
        internships, _ = get_current_data()
        
        if not internships:
            raise HTTPException(status_code=404, detail="No internships data found")
        
        # Force recompute by clearing existing embeddings
        cached_embeddings = precompute_doc_embeddings_new(internships, {})
        save_embeddings(cached_embeddings, EMBEDDINGS_PATH)
        
        return {
            "message": "Embeddings recomputed successfully",
            "total_internships": len(internships),
            "total_embeddings": len(cached_embeddings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "available_endpoints": [
        "/api/recommend",
        "/api/recommend/validated", 
        "/api/internships",
        "/api/stats",
        "/api/embeddings/status",
        "/api/embeddings/recompute"
    ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)