#!/usr/bin/env python3
"""
Quick test of AI functionality without GUI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.warp_terminal_gui import WarpTerminalWindow

# Create a minimal test
class AITester:
    def __init__(self):
        self.warp = WarpTerminalWindow.__new__(WarpTerminalWindow)
        # Initialize just the AI parts
        self.warp.OLLAMA_AVAILABLE = True
        self.warp.OLLAMA_CLIENT = None
    
    def test_ai(self, query):
        try:
            response = self.warp.get_ai_response(query)
            print(f"Query: {query}")
            print(f"Response: {response}")
            print("-" * 50)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None

if __name__ == "__main__":
    tester = AITester()
    
    print("🤖 Testing AI functionality...")
    print("=" * 50)
    
    # Test queries
    queries = [
        "What is Docker?",
        "How do I list files in Linux?",
        "Explain git commands"
    ]
    
    for query in queries:
        tester.test_ai(query)
    
    print("✅ AI test complete!")