"""
Test Neo4j connection and verify graph data
"""
from neo4j import GraphDatabase
import config


def test_connection():
    """Test basic Neo4j connectivity"""
    print(f"Testing connection to {config.NEO4J_URI}...")
    
    try:
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        # Verify connectivity
        driver.verify_connectivity()
        print("✓ Successfully connected to Neo4j!")
        
        # Test query
        with driver.session() as session:
            # Get node counts
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as node_type, count(n) as count
                ORDER BY count DESC
            """)
            
            print("\n📊 Node counts in database:")
            total_nodes = 0
            for record in result:
                node_type = record["node_type"]
                count = record["count"]
                total_nodes += count
                print(f"  - {node_type}: {count:,}")
            
            print(f"\n  Total nodes: {total_nodes:,}")
            
            # Get relationship counts
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            print("\n🔗 Relationship counts:")
            total_rels = 0
            for record in result:
                rel_type = record["rel_type"]
                count = record["count"]
                total_rels += count
                print(f"  - {rel_type}: {count:,}")
            
            print(f"\n  Total relationships: {total_rels:,}")
            
            # Sample query - get a random patient
            result = session.run("""
                MATCH (p:Patient)
                RETURN p.id as patient_id, p.firstName as first_name, 
                       p.lastName as last_name, p.gender as gender
                LIMIT 1
            """)
            
            record = result.single()
            if record:
                print(f"\n👤 Sample patient:")
                print(f"  - ID: {record['patient_id']}")
                print(f"  - Name: {record['first_name']} {record['last_name']}")
                print(f"  - Gender: {record['gender']}")
            
        driver.close()
        print("\n✅ Neo4j connection test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed!")
        print(f"Error: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check if Neo4j is running: http://localhost:7474")
        print(f"  2. Verify credentials in .env file")
        print(f"  3. Ensure database has data loaded")
        return False


if __name__ == "__main__":
    test_connection()
