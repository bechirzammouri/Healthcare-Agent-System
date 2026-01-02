"""
Quick test of the GraphRAG-enabled agent
"""
from agent.graph import create_agent
from langchain_core.messages import HumanMessage

print("="*70)
print("Testing GraphRAG-enabled Agent")
print("="*70)

agent = create_agent()

# Test queries
queries = [
    "Find conditions similar to chronic kidney disease",
    "What are the top 5 most common conditions?",
]

for query in queries:
    print(f"\n📝 Query: {query}")
    print("-"*70)
    
    try:
        response = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        
        # Print the agent's response
        print(response["messages"][-1].content[:500])
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ GraphRAG Agent Test Complete!")
print("="*70)
