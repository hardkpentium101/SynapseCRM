#!/usr/bin/env python3
"""
Test script for HCP Agent
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()


def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")
    from src.agent import (
        get_llm_manager,
        HCPAgent,
        IntentClassifierAgent,
        EntityExtractorAgent,
        get_tool_registry,
        get_memory,
    )

    print("  ✓ All imports successful")


def test_llm_manager():
    """Test LLM manager"""
    print("\nTesting LLM Manager...")
    from src.agent import get_llm_manager

    llm = get_llm_manager()
    print(f"  ✓ Provider: {llm.__class__.__name__}")

    # Test list models
    models = llm.list_models()
    print(f"  ✓ Available models: {len(models)}")
    for m in models[:5]:
        print(f"    - {m.id}")


def test_tool_registry():
    """Test tool registry"""
    print("\nTesting Tool Registry...")
    from src.agent import get_tool_registry

    registry = get_tool_registry()
    tools = registry.get_all_definitions()
    print(f"  ✓ Registered tools: {len(tools)}")
    for tool in tools:
        print(f"    - {tool['function']['name']}")


def test_agent():
    """Test agent functionality (requires GROQ_API_KEY)"""
    print("\nTesting Agent...")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your-groq-api-key":
        print("  ⚠ Skipping agent test (no API key)")
        return

    from src.agent import HCPAgent, get_llm_manager

    llm = get_llm_manager()
    agent = HCPAgent(llm)

    print("  ✓ Agent initialized")

    # Create session
    session = agent.create_session("test_user")
    print(f"  ✓ Session created: {session.session_id}")

    # Test with a simple message
    print("\n  Testing: 'I met with Dr. Sharma today'")
    result = agent.process(
        user_input="I met with Dr. Sharma today", session_id=session.session_id
    )

    print(f"    Intent: {result.intent}")
    print(f"    Response: {result.message[:100]}...")
    print(f"    Success: {result.success}")

    if result.entities:
        print(f"    Entities: {result.entities}")


def test_langgraph():
    """Test LangGraph integration"""
    print("\nTesting LangGraph...")

    try:
        from src.agent.langgraph import build_agent_graph, run_agent

        graph = build_agent_graph()
        print("  ✓ Graph built successfully")

        # Try to compile
        compiled = graph.compile()
        print("  ✓ Graph compiled successfully")

    except ImportError as e:
        print(f"  ⚠ LangGraph not available: {e}")
    except Exception as e:
        print(f"  ⚠ LangGraph error: {e}")


def main():
    print("=" * 50)
    print("HCP Agent Test Suite")
    print("=" * 50)

    test_imports()

    try:
        test_llm_manager()
    except Exception as e:
        print(f"  ✗ LLM Manager error: {e}")

    try:
        test_tool_registry()
    except Exception as e:
        print(f"  ✗ Tool Registry error: {e}")

    try:
        test_agent()
    except Exception as e:
        print(f"  ✗ Agent error: {e}")

    try:
        test_langgraph()
    except Exception as e:
        print(f"  ✗ LangGraph error: {e}")

    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()

    from src.agent.langsmith.tracing import wait_for_all_tracers
    wait_for_all_tracers()
