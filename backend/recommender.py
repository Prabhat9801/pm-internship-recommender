# backend/recommender.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os, json, numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
from datetime import datetime

load_dotenv()

# Initialize embeddings using your provided API wrapper
EMBED_MODEL_NAME = "models/embedding-001"
embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL_NAME, dimensions=32)

def load_internships(path="internships.json"):
    """Load internships from JSON file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading internships: {e}")
        return []

def save_internships(data, path="internships.json"):
    """Save internships to JSON file (kept for backward compatibility)"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving internships: {e}")

def load_embeddings(path="embeddings.json"):
    """Load embeddings from separate JSON file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("embeddings", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Info: No existing embeddings file found: {e}")
        return {}

def save_embeddings(embeddings_dict, path="embeddings.json"):
    """Save embeddings to separate JSON file with metadata"""
    try:
        data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_embeddings": len(embeddings_dict),
                "embedding_model": EMBED_MODEL_NAME
            },
            "embeddings": embeddings_dict
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving embeddings: {e}")

def get_internship_id(internship):
    """Generate consistent ID for internship"""
    # Use provided ID if available, otherwise generate from title + org
    if internship.get('id'):
        return str(internship['id'])
    
    # Generate ID from title and organization
    title = internship.get('title', '')
    org = internship.get('org', '')
    return f"{title}_{org}".replace(' ', '_').lower()

def get_file_hash(path):
    """Get hash of file content for change detection"""
    try:
        with open(path, "rb") as f:
            file_content = f.read()
            return hashlib.md5(file_content).hexdigest()
    except Exception:
        return None

def get_internship_text(internship):
    """Generate text representation of internship for embedding"""
    sectors = internship.get('sector', '')
    if isinstance(sectors, list):
        sectors = ', '.join(sectors)
    
    return (
        f"Position: {internship.get('title', '')} "
        f"Company: {internship.get('org', '')} "
        f"Education Required: {internship.get('required_education', '')} "
        f"Required Skills: {internship.get('skills', '')} "
        f"Industry Sector: {sectors} "
        f"Work Location: {internship.get('location', '')} "
        f"Description: {internship.get('description', '')[:200]}"  # Include description if available
    ).strip()

def precompute_doc_embeddings_new(internships, existing_embeddings=None):
    """
    Compute embeddings for internships and return updated embeddings dict.
    Only computes embeddings for internships that don't already have them.
    
    Args:
        internships: List of internship dictionaries
        existing_embeddings: Dict of existing embeddings {internship_id: embedding_vector}
    
    Returns:
        Dict of embeddings {internship_id: embedding_vector}
    """
    if not internships:
        return existing_embeddings or {}
    
    if existing_embeddings is None:
        existing_embeddings = {}
    
    # Find internships that need embeddings
    docs_to_compute = []
    ids_to_compute = []
    
    for internship in internships:
        if not isinstance(internship, dict):
            continue
        
        internship_id = get_internship_id(internship)
        
        # Skip if embedding already exists
        if internship_id in existing_embeddings:
            continue
        
        text = get_internship_text(internship)
        
        if text:  # Only process non-empty text
            docs_to_compute.append(text)
            ids_to_compute.append(internship_id)
    
    # Compute new embeddings
    if docs_to_compute:
        print(f"Computing {len(docs_to_compute)} new embeddings...")
        try:
            new_embeddings = embeddings.embed_documents(docs_to_compute)
            
            # Add new embeddings to existing ones
            for i, embedding_vector in enumerate(new_embeddings):
                existing_embeddings[ids_to_compute[i]] = embedding_vector
            
            print(f"✅ Successfully computed {len(new_embeddings)} new embeddings")
            
        except Exception as e:
            print(f"Error computing embeddings: {e}")
            raise
    else:
        print("All internships already have embeddings")
    
    return existing_embeddings

def check_and_update_embeddings(internships_path, embeddings_path, cached_internships=None, cached_embeddings=None):
    """
    Check if internships file has changed and update embeddings if necessary.
    
    Returns:
        tuple: (internships, embeddings, updated_flag)
    """
    # Check if internships file has changed
    current_hash = get_file_hash(internships_path)
    
    # Load metadata from embeddings file to check last processed hash
    embeddings_metadata = {}
    if os.path.exists(embeddings_path):
        try:
            with open(embeddings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                embeddings_metadata = data.get("metadata", {})
        except Exception:
            pass
    
    last_processed_hash = embeddings_metadata.get("source_file_hash")
    
    # If file hasn't changed and we have cached data, return it
    if (current_hash == last_processed_hash and 
        cached_internships is not None and 
        cached_embeddings is not None):
        return cached_internships, cached_embeddings, False
    
    # File has changed or no cache - reload and recompute
    print("🔄 Internships file changed or cache empty, updating embeddings...")
    
    # Load internships
    internships = load_internships(internships_path)
    if not internships:
        print("❌ No internships loaded")
        return [], {}, False
    
    # Load existing embeddings
    existing_embeddings = load_embeddings(embeddings_path)
    
    # Compute any missing embeddings
    updated_embeddings = precompute_doc_embeddings_new(internships, existing_embeddings)
    
    # Save updated embeddings with metadata
    try:
        data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_embeddings": len(updated_embeddings),
                "embedding_model": EMBED_MODEL_NAME,
                "source_file_hash": current_hash,
                "source_file_path": internships_path
            },
            "embeddings": updated_embeddings
        }
        with open(embeddings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated embeddings saved to {embeddings_path}")
        
    except Exception as e:
        print(f"Error saving updated embeddings: {e}")
        # Continue with in-memory embeddings even if save fails
    
    return internships, updated_embeddings, True

# Legacy function kept for backward compatibility
def precompute_doc_embeddings(internships):
    """
    Legacy function that adds embeddings directly to internships dicts.
    Maintained for backward compatibility but not recommended for new code.
    """
    if not internships:
        return []
    
    # Convert to new format and back
    embeddings_dict = precompute_doc_embeddings_new(internships, {})
    
    # Add embeddings back to internship objects
    for internship in internships:
        if isinstance(internship, dict):
            internship_id = get_internship_id(internship)
            if internship_id in embeddings_dict:
                internship["embedding"] = embeddings_dict[internship_id]
    
    return internships

def calculate_skill_relevance(user_skills, internship_skills):
    """
    Calculate skill relevance score between user and internship
    Returns: (exact_matches, partial_matches, relevance_score)
    """
    user_skill_tokens = set([s.strip().lower() for s in user_skills.split(",") if s.strip()])
    intern_skill_tokens = set([s.strip().lower() for s in internship_skills.split(",") if s.strip()])
    
    if not user_skill_tokens or not intern_skill_tokens:
        return 0, 0, 0.0
    
    # Exact matches
    exact_matches = user_skill_tokens & intern_skill_tokens
    
    # Partial matches (substring matching for related skills)
    partial_matches = 0
    for user_skill in user_skill_tokens:
        for intern_skill in intern_skill_tokens:
            if len(user_skill) > 2 and len(intern_skill) > 2:
                if (user_skill in intern_skill or intern_skill in user_skill) and user_skill not in exact_matches:
                    partial_matches += 1
                    break  # Only count once per user skill
    
    # Calculate relevance score
    exact_weight = len(exact_matches) * 1.0
    partial_weight = partial_matches * 0.6
    total_user_skills = len(user_skill_tokens)
    
    relevance_score = (exact_weight + partial_weight) / total_user_skills if total_user_skills > 0 else 0.0
    
    return len(exact_matches), partial_matches, relevance_score

def recommend(internships, education, skills, location, top_k=5):
    """
    Enhanced recommendation function with skill-first filtering
    
    internships: list of internship dicts (each with 'embedding' list)
    education, skills, location: strings
    top_k: number of recommendations (clamped between 3-7)
    returns: list of top_k internship dicts with added 'score' and 'match_details'
    """
    # Input validation
    if not internships or not isinstance(internships, list):
        return []
    
    education = str(education).strip() if education else ""
    skills = str(skills).strip() if skills else ""
    location = str(location).strip() if location else ""
    
    # Ensure top_k is within desired range (3-7)
    top_k = max(3, min(7, top_k))
    
    # Step 1: Filter internships by skill relevance
    skill_relevant_internships = []
    skill_relevance_data = []
    
    for i, internship in enumerate(internships):
        if not isinstance(internship, dict):
            continue
            
        internship_skills = internship.get("skills", "")
        exact_matches, partial_matches, relevance_score = calculate_skill_relevance(skills, internship_skills)
        
        # Only include internships with some skill relevance
        # Threshold: at least 1 exact match OR 2 partial matches OR relevance score > 0.2
        if exact_matches > 0 or partial_matches >= 2 or relevance_score > 0.2:
            skill_relevant_internships.append(internship)
            skill_relevance_data.append({
                'original_index': i,
                'exact_matches': exact_matches,
                'partial_matches': partial_matches,
                'relevance_score': relevance_score
            })
    
    # If no skill-relevant internships, use semantic similarity fallback
    if not skill_relevant_internships:
        return semantic_fallback_recommendation(internships, education, skills, location, top_k)
    
    # Adjust top_k based on available skill-relevant internships
    top_k = min(top_k, len(skill_relevant_internships))
    
    # Step 2: Compute semantic similarity for skill-relevant internships
    query = f"Skills: {skills} {skills} {skills}, Education: {education} {education}, Position: {location}"
    
    try:
        q_emb = embeddings.embed_query(query)
        q_vec = np.array(q_emb).reshape(1, -1)
    except Exception as e:
        print(f"Error computing query embedding: {e}")
        return []
    
    semantic_scores = []
    for internship in skill_relevant_internships:
        doc_emb = np.array(internship.get("embedding", []))
        if doc_emb.size == 0:
            semantic_scores.append(0.0)
            continue
        try:
            sim = cosine_similarity(q_vec, doc_emb.reshape(1, -1))[0][0]
            semantic_scores.append(float(sim))
        except Exception:
            semantic_scores.append(0.0)
    
    # Step 3: Calculate boosted scores
    user_edu = education.lower()
    user_loc = location.lower()
    
    final_scores = []
    for i, internship in enumerate(skill_relevant_internships):
        base_score = semantic_scores[i]
        boost = 0.0
        relevance_data = skill_relevance_data[i]
        
        # Education boost - HIGH priority
        req_edu = str(internship.get("required_education", "")).lower()
        edu_match = False
        if req_edu and user_edu:
            if req_edu == user_edu or req_edu in user_edu or user_edu in req_edu:
                boost += 0.25
                edu_match = True
        
        # Skill boosts - HIGHEST priority
        exact_matches = relevance_data['exact_matches']
        partial_matches = relevance_data['partial_matches']
        
        boost += 0.30 * exact_matches  # Heavy weight for exact skill matches
        boost += 0.15 * min(partial_matches, 3)  # Moderate weight for partial matches
        
        # Location boost - MINIMAL priority
        intern_loc = str(internship.get("location", "")).lower()
        location_match = False
        if user_loc and intern_loc:
            if (user_loc == intern_loc or 
                "remote" in intern_loc or 
                user_loc == "remote" or
                any(loc in intern_loc for loc in user_loc.split()) or
                any(loc in user_loc for loc in intern_loc.split())):
                boost += 0.08
                location_match = True
        
        final_score = base_score + boost
        final_scores.append({
            'score': final_score,
            'internship': internship,
            'match_details': {
                'exact_skill_matches': exact_matches,
                'partial_skill_matches': partial_matches,
                'skill_relevance_score': relevance_data['relevance_score'],
                'education_match': edu_match,
                'location_match': location_match,
                'semantic_similarity': base_score
            }
        })
    
    # Step 4: Sort and return top results
    final_scores.sort(key=lambda x: x['score'], reverse=True)
    
    results = []
    for item in final_scores[:top_k]:
        internship_copy = item['internship'].copy()
        internship_copy['score'] = float(item['score'])
        internship_copy['match_details'] = item['match_details']
        
        # Remove embedding to keep response lightweight
        if 'embedding' in internship_copy:
            del internship_copy['embedding']
        
        results.append(internship_copy)
    
    return results

def semantic_fallback_recommendation(internships, education, skills, location, top_k):
    """
    Fallback recommendation based purely on semantic similarity
    Used when no skill-relevant internships are found
    """
    query = f"Skills: {skills} {skills} {skills} {skills}, Education: {education} {education}"
    
    try:
        q_emb = embeddings.embed_query(query)
        q_vec = np.array(q_emb).reshape(1, -1)
    except Exception:
        return []
    
    semantic_scores = []
    valid_internships = []
    
    for internship in internships:
        if not isinstance(internship, dict):
            continue
            
        doc_emb = np.array(internship.get("embedding", []))
        if doc_emb.size == 0:
            continue
            
        try:
            sim = cosine_similarity(q_vec, doc_emb.reshape(1, -1))[0][0]
            if sim > 0.4:  # Only include reasonably similar internships
                semantic_scores.append(sim)
                valid_internships.append(internship)
        except Exception:
            continue
    
    if not valid_internships:
        return []
    
    # Get top semantic matches
    top_k = min(top_k, len(valid_internships))
    idx_sorted = np.argsort(semantic_scores)[-top_k:][::-1]
    
    results = []
    for idx in idx_sorted:
        internship_copy = valid_internships[idx].copy()
        internship_copy['score'] = float(semantic_scores[idx])
        internship_copy['match_details'] = {
            'exact_skill_matches': 0,
            'partial_skill_matches': 0,
            'skill_relevance_score': 0.0,
            'education_match': False,
            'location_match': False,
            'semantic_similarity': semantic_scores[idx],
            'fallback_recommendation': True
        }
        
        if 'embedding' in internship_copy:
            del internship_copy['embedding']
        
        results.append(internship_copy)
    
    return results

# Backward compatibility functions
def get_recommendations(internships, education, skills, location, num_recommendations=5):
    """Alternative function name for backward compatibility"""
    return recommend(internships, education, skills, location, num_recommendations)

def recommend_with_validation(internships, education, skills, location, top_k=5):
    """Recommendation function with enhanced input validation"""
    return recommend(internships, education, skills, location, top_k)