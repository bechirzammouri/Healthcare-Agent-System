"""
Test the healthcare agent with various queries to demonstrate tool usage
"""
from agent import run_agent
import time


def test_query(query: str, description: str):
    """Run a test query and display results"""
    print("\n" + "="*70)
    print(f"Test: {description}")
    print(f"Query: {query}")
    print("-"*70)
    
    try:
        start_time = time.time()
        answer = run_agent(query)
        elapsed = time.time() - start_time
        
        print(f"Answer:\n{answer}")
        print(f"\n⏱️  Time: {elapsed:.2f}s")
        print("✅ Success")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run test suite"""
    print("="*70)
    print("HEALTHCARE AGENT TEST SUITE")
    print("="*70)
    
    tests = [
        # Analytics Tool Tests
        {
            "query": "How many nodes are in the database?",
            "description": "Node counts (Analytics Tool)"
        },
        {
            "query": "What are the top 5 most common conditions?",
            "description": "Top conditions ranking (Analytics Tool)"
        },
        {
            "query": "What are the most prescribed medications?",
            "description": "Top medications (Analytics Tool)"
        },
        {
            "query": "What is the patient demographic breakdown?",
            "description": "Demographics analysis (Analytics Tool)"
        },
        
        # Neo4j Query Tool Tests
        {
            "query": "Show me the medical history for patient abf03ea9-2d1b-414e-8b07-5087c44bac8a",
            "description": "Patient history with ID (Neo4j Tool)"
        },
        {
            "query": "Show me the medical history for a random patient",
            "description": "Patient history random (Neo4j Tool)"
        },
        {
            "query": "Find patients with diabetes",
            "description": "Condition lookup (Neo4j Tool)"
        },
        {
            "query": "What medications are used to treat hypertension?",
            "description": "Medication info (Neo4j Tool)"
        },
        
        # Complex queries requiring multiple tools or reasoning
        {
            "query": "How many patients have encounters in the database?",
            "description": "Multi-step reasoning"
        }
    ]

    test_custom_queries = [
        {
            "query": "How many encounters does each patient have? Show top 5 patients.",
            "description": "Custom Cypher generation (Neo4j Tool)"
        }
        ]
    
    passed = 0
    failed = 0
    
    for test in tests[1:2]:
        if test_query(test["query"], test["description"]):
            passed += 1
        else:
            failed += 1
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print("="*70)


if __name__ == "__main__":
    main()
