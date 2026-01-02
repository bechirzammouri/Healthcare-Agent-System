"""
Vector Embedding Tool - Create and manage embeddings for graph nodes
Uses sentence-transformers for high-quality semantic embeddings
"""
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import config
from typing import List, Dict
import numpy as np


class VectorEmbeddingManager:
    """Manages vector embeddings for Neo4j graph nodes"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager with sentence-transformers
        
        Args:
            model_name: Name of the sentence-transformers model to use
                       Default: "all-MiniLM-L6-v2" (384 dim, fast, good quality)
                       Alternatives: "all-mpnet-base-v2" (768 dim, higher quality)
        """
        print(f"Loading sentence-transformers model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or text.strip() == "":
            return [0.0] * self.embedding_dim
        
        # Generate embedding using sentence-transformers
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        # Replace empty strings with placeholder
        processed_texts = [t if t and t.strip() else "unknown" for t in texts]
        
        # Batch encoding is more efficient
        embeddings = self.model.encode(processed_texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def delete_existing_embeddings(self):
        """Delete all existing embeddings and vector indexes"""
        print("\n=== Deleting Existing Embeddings ===\n")
        
        with self.driver.session() as session:
            # Drop vector indexes
            print("Dropping vector indexes...")
            indexes = [
                "condition_embedding_index",
                "medication_embedding_index", 
                "procedure_embedding_index",
                "observation_embedding_index",
                "encounter_embedding_index",
                "careplan_embedding_index"
            ]
            
            for index_name in indexes:
                try:
                    session.run(f"DROP INDEX {index_name} IF EXISTS")
                    print(f"  ✓ Dropped {index_name}")
                except Exception as e:
                    print(f"  - {index_name}: {e}")
            
            # Remove embedding properties from nodes
            print("\nRemoving embedding properties from nodes...")
            
            node_types = ["Condition", "Medication", "Procedure", "Observation", "Encounter", "CarePlan"]
            for node_type in node_types:
                try:
                    result = session.run(f"""
                        MATCH (n:{node_type})
                        WHERE n.embedding IS NOT NULL
                        REMOVE n.embedding
                        RETURN count(n) as count
                    """)
                    count = result.single()["count"]
                    print(f"  ✓ Removed embeddings from {count} {node_type} nodes")
                except Exception as e:
                    print(f"  - {node_type}: {e}")
        
        print("\n=== Cleanup Complete ===\n")
    
    def create_vector_indexes(self):
        """Create vector indexes in Neo4j for similarity search"""
        with self.driver.session() as session:
            # Vector index for Conditions
            try:
                session.run("""
                    CREATE VECTOR INDEX condition_embedding_index IF NOT EXISTS
                    FOR (c:Condition)
                    ON c.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dim=self.embedding_dim)
                print("✓ Created vector index for Condition nodes")
            except Exception as e:
                print(f"Condition index: {e}")
            
            # Vector index for Medications
            try:
                session.run("""
                    CREATE VECTOR INDEX medication_embedding_index IF NOT EXISTS
                    FOR (m:Medication)
                    ON m.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dim=self.embedding_dim)
                print("✓ Created vector index for Medication nodes")
            except Exception as e:
                print(f"Medication index: {e}")
            
            # Vector index for Procedures
            try:
                session.run("""
                    CREATE VECTOR INDEX procedure_embedding_index IF NOT EXISTS
                    FOR (p:Procedure)
                    ON p.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dim=self.embedding_dim)
                print("✓ Created vector index for Procedure nodes")
            except Exception as e:
                print(f"Procedure index: {e}")
            
            # Vector index for Observations
            try:
                session.run("""
                    CREATE VECTOR INDEX observation_embedding_index IF NOT EXISTS
                    FOR (o:Observation)
                    ON o.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dim=self.embedding_dim)
                print("✓ Created vector index for Observation nodes")
            except Exception as e:
                print(f"Observation index: {e}")
            
            # Vector index for Encounters
            try:
                session.run("""
                    CREATE VECTOR INDEX encounter_embedding_index IF NOT EXISTS
                    FOR (e:Encounter)
                    ON e.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dim=self.embedding_dim)
                print("✓ Created vector index for Encounter nodes")
            except Exception as e:
                print(f"Encounter index: {e}")
            
            # Vector index for CarePlans
            try:
                session.run("""
                    CREATE VECTOR INDEX careplan_embedding_index IF NOT EXISTS
                    FOR (cp:CarePlan)
                    ON cp.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dim=self.embedding_dim)
                print("✓ Created vector index for CarePlan nodes")
            except Exception as e:
                print(f"CarePlan index: {e}")
    
    def embed_conditions(self, batch_size: int = 100):
        """Add embeddings to all Condition nodes"""
        with self.driver.session() as session:
            # Get all conditions
            result = session.run("""
                MATCH (c:Condition)
                RETURN c.code as code, c.description as description
            """)
            
            conditions = [(r["code"], r["description"]) for r in result]
            print(f"Found {len(conditions)} conditions to embed")
            
            # Process in batches
            for i in range(0, len(conditions), batch_size):
                batch = conditions[i:i+batch_size]
                texts = [desc if desc else code for code, desc in batch]
                embeddings = self.generate_embeddings_batch(texts)
                
                # Update nodes with embeddings
                for (code, _), embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH (c:Condition {code: $code})
                        SET c.embedding = $embedding
                    """, code=code, embedding=embedding)
                
                print(f"  Processed {min(i+batch_size, len(conditions))}/{len(conditions)} conditions")
    
    def embed_medications(self, batch_size: int = 100):
        """Add embeddings to all Medication nodes"""
        with self.driver.session() as session:
            # Get all medications
            result = session.run("""
                MATCH (m:Medication)
                RETURN m.code as code, m.description as description
            """)
            
            medications = [(r["code"], r["description"]) for r in result]
            print(f"Found {len(medications)} medications to embed")
            
            # Process in batches
            for i in range(0, len(medications), batch_size):
                batch = medications[i:i+batch_size]
                texts = [desc if desc else code for code, desc in batch]
                embeddings = self.generate_embeddings_batch(texts)
                
                # Update nodes with embeddings
                for (code, _), embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH (m:Medication {code: $code})
                        SET m.embedding = $embedding
                    """, code=code, embedding=embedding)
                
                print(f"  Processed {min(i+batch_size, len(medications))}/{len(medications)} medications")
    
    def embed_procedures(self, batch_size: int = 100):
        """Add embeddings to all Procedure nodes"""
        with self.driver.session() as session:
            # Get all procedures
            result = session.run("""
                MATCH (p:Procedure)
                RETURN p.code as code, p.description as description
            """)
            
            procedures = [(r["code"], r["description"]) for r in result]
            print(f"Found {len(procedures)} procedures to embed")
            
            # Process in batches
            for i in range(0, len(procedures), batch_size):
                batch = procedures[i:i+batch_size]
                texts = [desc if desc else code for code, desc in batch]
                embeddings = self.generate_embeddings_batch(texts)
                
                # Update nodes with embeddings
                for (code, _), embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH (p:Procedure {code: $code})
                        SET p.embedding = $embedding
                    """, code=code, embedding=embedding)
                
                print(f"  Processed {min(i+batch_size, len(procedures))}/{len(procedures)} procedures")
    
    def embed_observations(self, batch_size: int = 100):
        """Add embeddings to all Observation nodes"""
        with self.driver.session() as session:
            # Get all observations
            result = session.run("""
                MATCH (o:Observation)
                RETURN o.code as code, o.description as description
                LIMIT 1000
            """)
            
            observations = [(r["code"], r["description"]) for r in result]
            print(f"Found {len(observations)} observations to embed (limited to 1000)")
            
            # Process in batches
            for i in range(0, len(observations), batch_size):
                batch = observations[i:i+batch_size]
                texts = [desc if desc else code for code, desc in batch]
                embeddings = self.generate_embeddings_batch(texts)
                
                # Update nodes with embeddings
                for (code, _), embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH (o:Observation {code: $code})
                        SET o.embedding = $embedding
                    """, code=code, embedding=embedding)
                
                print(f"  Processed {min(i+batch_size, len(observations))}/{len(observations)} observations")
    
    def embed_encounters(self, batch_size: int = 100):
        """Add embeddings to all Encounter nodes"""
        with self.driver.session() as session:
            # Get all encounters
            result = session.run("""
                MATCH (e:Encounter)
                RETURN e.id as id, e.encounterClass as encounterClass, e.description as description
            """)
            
            encounters = [(r["id"], r["encounterClass"], r["description"]) for r in result]
            print(f"Found {len(encounters)} encounters to embed")
            
            # Process in batches
            for i in range(0, len(encounters), batch_size):
                batch = encounters[i:i+batch_size]
                # Create text from encounterClass and description
                texts = [
                    f"{enc_class or ''} {desc or ''}" if (enc_class or desc) else f"encounter_{id}"
                    for id, enc_class, desc in batch
                ]
                embeddings = self.generate_embeddings_batch(texts)
                
                # Update nodes with embeddings
                for (id, _, _), embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH (e:Encounter {id: $id})
                        SET e.embedding = $embedding
                    """, id=id, embedding=embedding)
                
                print(f"  Processed {min(i+batch_size, len(encounters))}/{len(encounters)} encounters")
    
    def embed_careplans(self, batch_size: int = 100):
        """Add embeddings to all CarePlan nodes"""
        with self.driver.session() as session:
            # Get all careplans
            result = session.run("""
                MATCH (cp:CarePlan)
                RETURN cp.id as id, cp.code as code, cp.description as description
            """)
            
            careplans = [(r["id"], r["code"], r["description"]) for r in result]
            print(f"Found {len(careplans)} careplans to embed")
            
            # Process in batches
            for i in range(0, len(careplans), batch_size):
                batch = careplans[i:i+batch_size]
                # Use description or code as text
                texts = [desc if desc else (code if code else f"careplan_{id}") for id, code, desc in batch]
                embeddings = self.generate_embeddings_batch(texts)
                
                # Update nodes with embeddings
                for (id, _, _), embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH (cp:CarePlan {id: $id})
                        SET cp.embedding = $embedding
                    """, id=id, embedding=embedding)
                
                print(f"  Processed {min(i+batch_size, len(careplans))}/{len(careplans)} careplans")
    
    def embed_all_nodes(self):
        """Embed all supported node types"""
        print("\n=== Starting Vector Embedding Generation ===\n")
        print("Using sentence-transformers model for embeddings.\n")
        
        print("1. Embedding Conditions...")
        self.embed_conditions()
        
        print("\n2. Embedding Medications...")
        self.embed_medications()
        
        print("\n3. Embedding Procedures...")
        self.embed_procedures()
        
        print("\n4. Embedding Observations...")
        self.embed_observations()
        
        print("\n5. Embedding Encounters...")
        self.embed_encounters()
        
        print("\n6. Embedding CarePlans...")
        self.embed_careplans()
        
        print("\n7. Creating vector indexes...")
        self.create_vector_indexes()
        
        print("\n=== Vector Embedding Generation Complete! ===\n")
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
