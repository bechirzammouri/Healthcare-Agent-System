"""
Test LLM API connection and function calling
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import config


def test_basic_chat():
    """Test basic LLM chat"""
    print(f"Testing {config.LLM_PROVIDER} API with model {config.LLM_MODEL}...")
    
    try:
        # Initialize LLM
        llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.LLM_MODEL,
            temperature=config.TEMPERATURE
        )
        
        # Simple test message
        messages = [HumanMessage(content="Say 'Hello, I am working!' in one sentence.")]
        
        print("\n🤖 Sending test message...")
        response = llm.invoke(messages)
        
        print(f"✓ Response received: {response.content}")
        print(f"\n✅ Basic chat test passed!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM test failed!")
        print(f"Error: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check GROQ_API_KEY in .env file")
        print(f"  2. Verify API key is valid: https://console.groq.com/keys")
        print(f"  3. Check internet connection")
        return False


def test_function_calling():
    """Test LLM function calling capability"""
    print("\n" + "="*60)
    print("Testing function calling capability...")
    
    try:
        from langchain_core.tools import tool
        
        # Define a simple test tool
        @tool
        def get_weather(city: str) -> str:
            """Get weather for a city"""
            return f"The weather in {city} is sunny, 25°C"
        
        # Initialize LLM with tool
        llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.LLM_MODEL,
            temperature=0
        )
        
        llm_with_tools = llm.bind_tools([get_weather])
        
        # Test message that should trigger tool call
        messages = [HumanMessage(content="What's the weather in Paris?")]
        
        print("🤖 Sending message that requires tool use...")
        response = llm_with_tools.invoke(messages)
        
        if response.tool_calls:
            print(f"✓ Tool called: {response.tool_calls[0]['name']}")
            print(f"✓ Arguments: {response.tool_calls[0]['args']}")
            print(f"\n✅ Function calling test passed!")
        else:
            print(f"⚠ No tool calls detected (response: {response.content})")
            print(f"This might still work but tool calling may be inconsistent")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Function calling test failed!")
        print(f"Error: {str(e)}")
        return False


def test_model_info():
    """Display model information"""
    print("\n" + "="*60)
    print("Configuration:")
    print(f"  Provider: {config.LLM_PROVIDER}")
    print(f"  Model: {config.LLM_MODEL}")
    print(f"  Temperature: {config.TEMPERATURE}")
    print(f"  Max Iterations: {config.MAX_ITERATIONS}")


if __name__ == "__main__":
    print("="*60)
    print("LLM API Test Suite")
    print("="*60)
    
    test_model_info()
    
    # Run tests
    print("\n")
    basic_ok = test_basic_chat()
    
    if basic_ok:
        test_function_calling()
    
    print("\n" + "="*60)
    print("Test suite completed!")
    print("="*60)
