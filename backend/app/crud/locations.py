from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Any
from app.models.locations import Location

def save_locations(db: Session, locations: List[Any]):
    # GUARDRAIL: The LLM occasionally ignores instructions and returns dicts: 
    # e.g., [{"location": "Paris"}, {"country": "France"}] instead of ["Paris", "France"].
    # We must sanitize the list into pure strings before deduplicating.
    sanitized_locations = []
    for loc in locations:
        if isinstance(loc, str):
            sanitized_locations.append(loc)
        elif isinstance(loc, dict) and len(loc) > 0:
            # Extract the first value from the dictionary
            sanitized_locations.append(str(list(loc.values())[0]))

    # CRITICAL FIX: The LLM might return ["United States", "China", "United States"].
    # We must deduplicate the list before passing it to SQLAlchemy.
    unique_locations = list(set(sanitized_locations))
    
    location_objects = []
    
    # 1. Ask Postgres for ALL existing locations in our list at once (Only 1 DB Query!)
    existing_locs = db.query(Location).filter(Location.name.in_(unique_locations)).all()
    
    # 2. Extract just the names into a fast Python set
    existing_names = {loc.name for loc in existing_locs}
    
    # 3. Add the already-existing locations to our array
    location_objects.extend(existing_locs)
    
    # 4. For any location that didn't exist, create a new object
    for loc_name in unique_locations:
        if loc_name not in existing_names:
            new_loc = Location(name=loc_name)
            
            # CRITICAL ADDITION: Concurrency Protection!
            # If two different background jobs try to insert "United States" concurrently,
            # one will crash. We use a "savepoint" (begin_nested) to safely catch it.
            try:
                with db.begin_nested():
                    db.add(new_loc)
                    db.flush()
                
                # If we reach here, the insertion succeeded! Add the new object.
                location_objects.append(new_loc)
                
            except IntegrityError:
                # The collision happened! Another thread beat us to it.
                # The savepoint automatically rolls back just this tiny insert without killing the main transaction.
                # We can now safely fetch the one the other thread just created!
                concurrent_loc = db.query(Location).filter(Location.name == loc_name).first()
                if concurrent_loc:
                    location_objects.append(concurrent_loc)
            
    return location_objects
