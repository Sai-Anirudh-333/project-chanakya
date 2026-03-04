from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.entities import Entity

def save_entities(db: Session, entities_dict: dict):
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
    existing_ents = db.query(Entity).filter(Entity.name.in_(unique_names)).all()
    existing_names = {ent.name for ent in existing_ents}
    
    # Add already-existing entities
    entity_objects.extend(existing_ents)
    
    # 4. For any entity that didn't exist, create a new object safely
    for e_name in unique_names:
        if e_name not in existing_names:
            new_ent = Entity(name=e_name, type=unique_entities[e_name])
            
            # OPTIMISTIC LOCKING: Same savepoint trap we built for locations
            try:
                with db.begin_nested():
                    db.add(new_ent)
                    db.flush()
                entity_objects.append(new_ent)
            except IntegrityError:
                concurrent_ent = db.query(Entity).filter(Entity.name == e_name).first()
                if concurrent_ent:
                    entity_objects.append(concurrent_ent)
                    
    return entity_objects
