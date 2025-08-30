# backend/compute_embeddings.py
from recommender import load_internships, load_embeddings, save_embeddings, precompute_doc_embeddings_new, get_internship_id
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Configuration
INTERNSHIPS_PATH = "internships.json"
EMBEDDINGS_PATH = "embeddings.json"
BACKUP_PATH = "embeddings_backup.json"

def main():
    """
    Enhanced embedding computation script with separate embeddings file
    """
    print("=" * 60)
    print("PM Internship Recommender - Embedding Computer v3.0")
    print("=" * 60)
    
    # Check if input file exists
    if not os.path.exists(INTERNSHIPS_PATH):
        print(f"❌ Error: {INTERNSHIPS_PATH} not found!")
        print("Please ensure your internships JSON file exists.")
        sys.exit(1)
    
    print(f"📂 Loading internships from: {INTERNSHIPS_PATH}")
    internships = load_internships(INTERNSHIPS_PATH)
    
    if not internships:
        print("❌ Error: No internships loaded or file is empty!")
        sys.exit(1)
    
    print(f"📂 Loading existing embeddings from: {EMBEDDINGS_PATH}")
    existing_embeddings = load_embeddings(EMBEDDINGS_PATH)
    
    total_internships = len(internships)
    existing_embeddings_count = len(existing_embeddings) if existing_embeddings else 0
    
    # Count how many internships already have embeddings
    internships_with_embeddings = 0
    for internship in internships:
        internship_id = get_internship_id(internship)
        if existing_embeddings and internship_id in existing_embeddings:
            internships_with_embeddings += 1
    
    print(f"📊 Statistics:")
    print(f"   • Total internships: {total_internships}")
    print(f"   • Existing embeddings: {existing_embeddings_count}")
    print(f"   • Internships with embeddings: {internships_with_embeddings}")
    print(f"   • Need embeddings: {total_internships - internships_with_embeddings}")
    
    # Create backup before processing
    if existing_embeddings_count > 0:
        print(f"💾 Creating backup at: {BACKUP_PATH}")
        try:
            save_embeddings(existing_embeddings, BACKUP_PATH)
            print("✅ Backup created successfully")
        except Exception as e:
            print(f"⚠️  Warning: Backup failed: {e}")
            response = input("Continue without backup? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                sys.exit(1)
    
    # Compute embeddings
    print("\n🔄 Computing embeddings...")
    print("   This may take time and cost API credits depending on:")
    print("   • Number of internships without embeddings")
    print("   • Google API rate limits")
    print("   • Network latency")
    
    try:
        # Use existing embeddings as base and compute missing ones
        updated_embeddings = precompute_doc_embeddings_new(internships, existing_embeddings or {})
        
        # Validate embeddings were computed
        new_embeddings_count = len(updated_embeddings)
        
        if new_embeddings_count > existing_embeddings_count:
            print(f"✅ Successfully computed {new_embeddings_count - existing_embeddings_count} new embeddings")
        elif new_embeddings_count == existing_embeddings_count and internships_with_embeddings == total_internships:
            print("✅ All internships already have embeddings - nothing to compute")
        else:
            print(f"⚠️  Warning: Got {new_embeddings_count} total embeddings")
        
    except Exception as e:
        print(f"❌ Error computing embeddings: {e}")
        if existing_embeddings_count > 0 and os.path.exists(BACKUP_PATH):
            print(f"💾 Backup available at: {BACKUP_PATH}")
        sys.exit(1)
    
    # Save results
    print(f"\n💾 Saving embeddings to: {EMBEDDINGS_PATH}")
    try:
        save_embeddings(updated_embeddings, EMBEDDINGS_PATH)
        
        # Verify save was successful
        verification = load_embeddings(EMBEDDINGS_PATH)
        verified_embeddings_count = len(verification) if verification else 0
        
        if verified_embeddings_count == new_embeddings_count:
            print("✅ Embeddings saved and verified successfully")
        else:
            print(f"⚠️  Warning: Verification failed. Expected {new_embeddings_count}, got {verified_embeddings_count}")
            
    except Exception as e:
        print(f"❌ Error saving embeddings file: {e}")
        if os.path.exists(BACKUP_PATH):
            print(f"💾 Backup available at: {BACKUP_PATH}")
        sys.exit(1)
    
    # Final verification with internships
    final_internships_with_embeddings = 0
    for internship in internships:
        internship_id = get_internship_id(internship)
        if internship_id in verification:
            final_internships_with_embeddings += 1
    
    print("\n" + "=" * 60)
    print("🎉 EMBEDDING COMPUTATION COMPLETED!")
    print("=" * 60)
    print(f"📊 Final Statistics:")
    print(f"   • Total internships: {len(internships)}")
    print(f"   • Total embeddings: {verified_embeddings_count}")
    print(f"   • Internships with embeddings: {final_internships_with_embeddings}")
    print(f"   • Coverage: {(final_internships_with_embeddings/len(internships)*100):.1f}%")
    
    if os.path.exists(EMBEDDINGS_PATH):
        embeddings_size = os.path.getsize(EMBEDDINGS_PATH)/1024/1024
        print(f"   • Embeddings file size: {embeddings_size:.1f} MB")
    
    if os.path.exists(BACKUP_PATH):
        backup_size = os.path.getsize(BACKUP_PATH)/1024/1024
        print(f"   • Backup size: {backup_size:.1f} MB")
    
    print("\n🚀 Your recommendation system is now ready!")
    print("   Run: python app.py")

def validate_embeddings():
    """
    Utility function to validate existing embeddings
    """
    print("🔍 Validating embeddings...")
    internships = load_internships(INTERNSHIPS_PATH)
    embeddings = load_embeddings(EMBEDDINGS_PATH)
    
    if not internships:
        print("❌ No internships found")
        return False
    
    if not embeddings:
        print("❌ No embeddings found")
        return False
    
    valid_embeddings = 0
    invalid_embeddings = 0
    missing_embeddings = 0
    
    for internship in internships:
        internship_id = get_internship_id(internship)
        
        if internship_id not in embeddings:
            missing_embeddings += 1
            continue
            
        try:
            emb = embeddings[internship_id]
            if isinstance(emb, list) and len(emb) > 0 and all(isinstance(x, (int, float)) for x in emb):
                valid_embeddings += 1
            else:
                invalid_embeddings += 1
                print(f"⚠️  Invalid embedding for {internship_id}: {type(emb)}")
        except Exception as e:
            invalid_embeddings += 1
            print(f"⚠️  Error validating embedding for {internship_id}: {e}")
    
    print(f"📊 Validation Results:")
    print(f"   • Valid embeddings: {valid_embeddings}")
    print(f"   • Invalid embeddings: {invalid_embeddings}")
    print(f"   • Missing embeddings: {missing_embeddings}")
    print(f"   • Total internships: {len(internships)}")
    print(f"   • Total embeddings in file: {len(embeddings)}")
    
    if invalid_embeddings > 0:
        print("❌ Some embeddings are invalid and need recomputation")
        return False
    elif missing_embeddings > 0:
        print("⚠️  Some embeddings are missing")
        return False
    else:
        print("✅ All embeddings are valid!")
        return True

def clean_orphaned_embeddings():
    """
    Remove embeddings that don't correspond to any internship
    """
    print("🧹 Cleaning orphaned embeddings...")
    
    internships = load_internships(INTERNSHIPS_PATH)
    embeddings = load_embeddings(EMBEDDINGS_PATH)
    
    if not internships or not embeddings:
        print("❌ Cannot clean - missing internships or embeddings data")
        return
    
    # Get all valid internship IDs
    valid_ids = set()
    for internship in internships:
        internship_id = get_internship_id(internship)
        valid_ids.add(internship_id)
    
    # Find orphaned embeddings
    orphaned_ids = set(embeddings.keys()) - valid_ids
    
    if orphaned_ids:
        print(f"🗑️  Found {len(orphaned_ids)} orphaned embeddings")
        
        # Create backup
        backup_path = f"{EMBEDDINGS_PATH}.pre_clean_backup"
        save_embeddings(embeddings, backup_path)
        print(f"💾 Created backup at: {backup_path}")
        
        # Remove orphaned embeddings
        for orphaned_id in orphaned_ids:
            del embeddings[orphaned_id]
        
        # Save cleaned embeddings
        save_embeddings(embeddings, EMBEDDINGS_PATH)
        print(f"✅ Cleaned embeddings saved. Removed {len(orphaned_ids)} orphaned entries")
    else:
        print("✅ No orphaned embeddings found")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--validate":
            validate_embeddings()
        elif sys.argv[1] == "--clean":
            clean_orphaned_embeddings()
        else:
            print("Usage: python compute_embeddings.py [--validate|--clean]")
    else:
        main()