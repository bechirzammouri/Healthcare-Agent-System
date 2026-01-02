"""
Test suite for GraphRAG pipeline
Tests vector search, graph traversal, and hybrid retrieval
"""
import sys
from agent.tools.vector_search_tool import VectorSearchTool
from agent.tools.graph_traversal_tool import GraphTraversalTool
from agent.tools.graphrag_tool import GraphRAGTool


def print_test_header(test_name, description):
    """Print formatted test header"""
    print("\n" + "="*70)
    print(f"Test: {test_name}")
    print(f"Description: {description}")
    print("-"*70)


def print_result(result, success=True):
    """Print test result"""
    if success:
        print("✅ Result:")
        print(result[:500] + "..." if len(result) > 500 else result)
    else:
        print(f"❌ Error: {result}")


def run_tests():
    """Run all GraphRAG tests"""
    
    print("="*70)
    print("GRAPHRAG PIPELINE TEST SUITE")
    print("="*70)
    
    passed = 0
    failed = 0
    total = 0
    
    # Initialize tools
    vector_tool = VectorSearchTool()
    traversal_tool = GraphTraversalTool()
    graphrag_tool = GraphRAGTool()
    
    # Test 1: Vector similarity search for conditions
    total += 1
    print_test_header(
        "Vector Similarity Search - Conditions",
        "Find conditions similar to 'diabetes'"
    )
    try:
        result = vector_tool._run(
            query_text="diabetes chronic metabolic disease",
            node_type="condition",
            limit=5,
            similarity_threshold=0.5
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Test 2: Vector similarity search for medications
    total += 1
    print_test_header(
        "Vector Similarity Search - Medications",
        "Find medications similar to 'pain medication'"
    )
    try:
        result = vector_tool._run(
            query_text="pain medication analgesic",
            node_type="medication",
            limit=5,
            similarity_threshold=0.5
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Test 3: Graph traversal - condition treatment path
    total += 1
    print_test_header(
        "Graph Traversal - Condition Treatment Path",
        "Find treatment patterns for diabetes"
    )
    try:
        result = traversal_tool._run(
            traversal_type="condition_treatment_path",
            condition_code="diabetes",
            limit=10
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Test 4: Graph traversal - medication interactions
    total += 1
    print_test_header(
        "Graph Traversal - Medication Interactions",
        "Find medications commonly prescribed with insulin"
    )
    try:
        result = traversal_tool._run(
            traversal_type="medication_interactions",
            medication_code="insulin",
            limit=5
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Test 5: Graph traversal - temporal patterns
    total += 1
    print_test_header(
        "Graph Traversal - Temporal Patterns",
        "Find common disease progression sequences"
    )
    try:
        result = traversal_tool._run(
            traversal_type="temporal_patterns",
            limit=10
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Test 6: GraphRAG - semantic then traverse
    total += 1
    print_test_header(
        "GraphRAG - Semantic Then Traverse",
        "Find treatments for cardiovascular conditions using hybrid approach"
    )
    try:
        result = graphrag_tool._run(
            query_text="cardiovascular heart disease treatment",
            retrieval_mode="semantic_then_traverse",
            focus_entity="condition",
            traversal_depth=2,
            top_k=3,
            similarity_threshold=0.5
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Test 7: GraphRAG - hybrid combined
    total += 1
    print_test_header(
        "GraphRAG - Hybrid Combined",
        "Find comprehensive information about respiratory medications"
    )
    try:
        result = graphrag_tool._run(
            query_text="respiratory breathing asthma medication",
            retrieval_mode="hybrid_combined",
            focus_entity="medication",
            traversal_depth=2,
            top_k=3,
            similarity_threshold=0.5
        )
        if "error" in result.lower():
            print_result(result, success=False)
            failed += 1
        else:
            print_result(result)
            passed += 1
    except Exception as e:
        print_result(str(e), success=False)
        failed += 1
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {total}")
    print("="*70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
