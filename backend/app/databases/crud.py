from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Any
from .models import Briefing, Location, Entity

class CRUD:
    def __init__(self, db: Session):
        self.db = db

    def save_briefing(self, topic: str, content: str, locations: List[Any], scout_data: str = None, scholar_data: str = None, entities: dict = None):
        briefing = Briefing(
            topic=topic, 
            content=content,
            scout_data=scout_data,
            scholar_data=scholar_data
        )
        briefing.locations = self.save_locations(locations)
        if entities:
            briefing.entities = self.save_entities(entities)
        
        # This updates the object with its new ID from PostgreSQL
        self.db.add(briefing)
        self.db.commit()
        self.db.refresh(briefing)
        return briefing

    def get_recent_briefings(self, limit: int = 10):
        # We use .order_by(Briefing.created_at.desc()) to get the newest ones first
        return self.db.query(Briefing).order_by(Briefing.created_at.desc()).limit(limit).all()

    def save_locations(self, locations: List[Any]):
        
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
        existing_locs = self.db.query(Location).filter(Location.name.in_(unique_locations)).all()
        
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
                    with self.db.begin_nested():
                        self.db.add(new_loc)
                        self.db.flush()
                    
                    # If we reach here, the insertion succeeded! Add the new object.
                    location_objects.append(new_loc)
                    
                except IntegrityError:
                    # The collision happened! Another thread beat us to it.
                    # The savepoint automatically rolls back just this tiny insert without killing the main transaction.
                    # We can now safely fetch the one the other thread just created!
                    concurrent_loc = self.db.query(Location).filter(Location.name == loc_name).first()
                    if concurrent_loc:
                        location_objects.append(concurrent_loc)
                
        return location_objects

    def save_entities(self, entities_dict: dict):
        entity_objects = []
        # 1. Flatten the dict into a list of (name, type) tuples
        flat_entities = []
        for entity_type, names in entities_dict.items():
            if entity_type == 'people': mapped_type = 'Person'
            elif entity_type == 'organizations': mapped_type = 'Organization'
            elif entity_type == 'countries': mapped_type = 'Country'
            else: mapped_type = 'Other'
            
            for name in names:
                if isinstance(name, str) and name.strip():
                    flat_entities.append((name.strip(), mapped_type))

        # 2. Deduplicate by name
        unique_entities = {}
        for name, typ in flat_entities:
            unique_entities[name] = typ
            
        unique_names = list(unique_entities.keys())
        if not unique_names:
            return []

        # 3. Ask Postgres for ALL existing entities in our list at once
        existing_ents = self.db.query(Entity).filter(Entity.name.in_(unique_names)).all()
        existing_names = {ent.name for ent in existing_ents}
        
        # Add already-existing entities
        entity_objects.extend(existing_ents)
        
        # 4. For any entity that didn't exist, create a new object safely
        for e_name in unique_names:
            if e_name not in existing_names:
                new_ent = Entity(name=e_name, type=unique_entities[e_name])
                
                # OPTIMISTIC LOCKING: Same savepoint trap we built for locations
                try:
                    with self.db.begin_nested():
                        self.db.add(new_ent)
                        self.db.flush()
                    entity_objects.append(new_ent)
                except IntegrityError:
                    concurrent_ent = self.db.query(Entity).filter(Entity.name == e_name).first()
                    if concurrent_ent:
                        entity_objects.append(concurrent_ent)
                        
        return entity_objects
