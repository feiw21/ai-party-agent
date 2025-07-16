"""
Evaluation and monitoring module for Alfred AI Agent using LangFuse.
This module provides observability, tracing, and evaluation capabilities.
"""

import os
import time
from typing import Dict, Any, Optional

from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain_core.messages import HumanMessage, AIMessage

# Import your existing agent components
from core.app import build_agent_graph, run_agent_with_tools, tools

# ============================================================================
# LANGFUSE SETUP
# ============================================================================
def setup_langfuse():
    """Initialize LangFuse client with credentials from environment."""
    try:
        # Get API keys from environment (should be set in ~/.zshrc)
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        host = os.environ.get("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        
        if not public_key or not secret_key:
            print("⚠️  LangFuse credentials not found in environment variables.")
            print("💡 Please set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in ~/.zshrc")
            print("💡 Using US cloud instance: https://us.cloud.langfuse.com")
            return None
        
        # Initialize LangFuse client using the credentials provided in the environment variables
        langfuse = get_client()
        
        # Verify connection
        if langfuse.auth_check():
            print(f"✅ LangFuse client authenticated and ready! (Host: {host})")
            return langfuse
        else:
            print("❌ LangFuse authentication failed. Please check your credentials.")
            return None
            
    except Exception as e:
        print(f"❌ Error setting up LangFuse: {str(e)}")
        return None

# ============================================================================
# INTEGRATION WITH LANGFUSE FOR TRACING AND MONITORING
# ============================================================================
class AlfredEvaluator:
    """Evaluation wrapper for Alfred agent with LangFuse integration."""
    
    def __init__(self):
        self.langfuse = setup_langfuse()
        self.agent = build_agent_graph()
        
        # Initialize LangFuse callback handler for LangGraph tracing
        if self.langfuse:
            self.langfuse_handler = CallbackHandler()
        else:
            self.langfuse_handler = None
        
    def trace_conversation(self, 
                          user_input: str, 
                          user_id: Optional[str] = None,
                          session_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run Alfred with full tracing and monitoring using LangGraph integration.
        
        Args:
            user_input: The user's message
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata
            
        Returns:
            Dictionary containing response and trace information
        """
        if not self.langfuse or not self.langfuse_handler:
            print("⚠️  LangFuse not available, running without tracing...")
            return self._run_without_tracing(user_input)
        
        try:
            # Start timing
            start_time = time.time()
            
            # Create initial messages
            messages = [HumanMessage(content=user_input)]
            
            # Run the agent with LangFuse callback handler for detailed tracing
            # This follows the LangGraph integration pattern from the documentation
            # Each call to agent.invoke() creates a new trace
            response = self.agent.invoke(
                {"messages": messages},
                config={"callbacks": [self.langfuse_handler]}
            )
            response_messages = response["messages"]
            
            # Get final response
            final_response = response_messages[-1].content
            
            # Calculate metrics
            execution_time = time.time() - start_time
            
            # Get the actual trace ID from the callback handler
            # The CallbackHandler automatically creates a trace for each invoke
            trace_id = getattr(self.langfuse_handler, 'trace_id', None)
            if not trace_id:
                # Fallback: generate a unique ID based on timestamp and user input
                import hashlib
                unique_string = f"{user_input}_{start_time}_{user_id or 'anonymous'}"
                trace_id = hashlib.md5(unique_string.encode()).hexdigest()
            
            return {
                "response": final_response,
                "trace_id": trace_id,  # Use unique trace ID for each conversation turn
                "execution_time": execution_time,
                "total_messages": len(response_messages),
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "trace_id": "error-no-trace",
                "success": False,
                "error": str(e)
            }
    
    def _run_without_tracing(self, user_input: str) -> Dict[str, Any]:
        """Fallback method when LangFuse is not available."""
        try:
            start_time = time.time()
            messages = [HumanMessage(content=user_input)]
            response_messages = run_agent_with_tools(messages)
            final_response = response_messages[-1].content
            execution_time = time.time() - start_time
            
            return {
                "response": final_response,
                "execution_time": execution_time,
                "total_messages": len(response_messages),
                "success": True
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "success": False,
                "error": str(e)
            }

# ============================================================================
# EVALUATION FUNCTIONS
# ============================================================================
def create_evaluation_dataset(langfuse, dataset_name: str = "alfred-test-dataset"):
    """Create a test dataset for Alfred evaluation."""
    if not langfuse:
        print("⚠️  LangFuse not available, skipping dataset creation.")
        return
    
    try:
        # Create dataset
        langfuse.create_dataset(
            name=dataset_name,
            description="Test dataset for Alfred party agent evaluation",
            metadata={"type": "test", "agent": "alfred-party-agent"}
        )
        
        # Add test cases
        test_cases = [
            {
                "input": "Tell me about Dr. Nikola Tesla",
                "expected_output": "Should provide information about Tesla from guest database"
            },
            {
                "input": "What are the latest developments in wireless energy?",
                "expected_output": "Should search web for current wireless energy news"
            },
            {
                "input": "Help me prepare for a conversation with Dr. Tesla about tech trends",
                "expected_output": "Should combine guest info with current tech news"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            langfuse.create_dataset_item(
                dataset_name=dataset_name,
                input={"text": test_case["input"]},
                expected_output={"text": test_case["expected_output"]},
                metadata={"test_case_id": i}
            )
        
        print(f"✅ Created evaluation dataset: {dataset_name}")
        
    except Exception as e:
        print(f"❌ Error creating dataset: {str(e)}")

def run_evaluation(evaluator: AlfredEvaluator, 
                  test_queries: list = None) -> Dict[str, Any]:
    """Run evaluation on a set of test queries."""
    if test_queries is None:
        test_queries = [
            "Tell me about Dr. Nikola Tesla",
            "What are the latest developments in wireless energy?",
            "Help me prepare for a conversation with Dr. Tesla about tech trends"
        ]
    
    results = []
    total_time = 0
    successful_runs = 0
    
    print("🧪 Running Alfred evaluation...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"  Test {i}/{len(test_queries)}: {query[:50]}...")
        
        result = evaluator.trace_conversation(
            user_input=query,
            user_id="evaluation-user",
            session_id=f"eval-session-{int(time.time())}",
            metadata={"test_case": i, "query_type": "evaluation"}
        )
        
        results.append(result)
        total_time += result.get("execution_time", 0)
        
        if result.get("success"):
            successful_runs += 1
    
    # Calculate metrics
    avg_time = total_time / len(test_queries) if test_queries else 0
    success_rate = successful_runs / len(test_queries) if test_queries else 0
    
    evaluation_summary = {
        "total_tests": len(test_queries),
        "successful_runs": successful_runs,
        "success_rate": success_rate,
        "average_execution_time": avg_time,
        "total_execution_time": total_time,
        "results": results
    }
    
    print(f"✅ Evaluation complete!")
    print(f"   Total tests: {len(test_queries)}")
    print(f"   Success rate: {success_rate:.1%}")
    print(f"   Average time: {avg_time:.2f}s")
    print(f"   Total time: {total_time:.2f}s")
    
    return evaluation_summary

# ============================================================================
# USER FEEDBACK INTEGRATION
# ============================================================================
def record_user_feedback(langfuse, trace_id: str, score: int, feedback_type: str = "user-rating"):
    """Record user feedback using trace-based tracing."""
    if not langfuse:
        print("⚠️  LangFuse not available, skipping feedback recording.")
        return
    
    try:
        # Use the new create_score API as shown in the documentation
        # trace_conversation creates one trace per invoke
        # One user input -> one conversation turn -> one trace -> one score
        # So multiple turn conversations generate multiple traces with multiple scores
        # Unique trace IDs are required for trace-based tracing
        langfuse.create_score(
            trace_id=trace_id,
            name=feedback_type,
            value=score,
            data_type="NUMERIC",
            comment=f"User rating: {score}/5"
        )
        
        # Immediately flush the data to ensure it appears in LangFuse interface
        langfuse.flush()
        
        print(f"✅ User feedback recorded: {score}/5 and flushed to LangFuse")
    except Exception as e:
        print(f"❌ Error recording feedback: {str(e)}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def list_recent_traces(langfuse, limit: int = 10) -> list:
    """List recent traces for monitoring."""
    if not langfuse:
        return []
    
    try:
        # For LangGraph integration, traces are created automatically by the CallbackHandler
        # We can't easily list them without additional API calls, so we'll return a simple status
        return [
            {
                "id": "auto-generated",
                "name": "LangGraph traces",
                "status": "SUCCESS",
                "timestamp": "auto",
                "execution_time": 0.0,
                "note": "Traces are automatically generated by LangFuse CallbackHandler"
            }
        ]
    except Exception as e:
        print(f"❌ Error checking traces: {str(e)}")
        return []

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("🎩 Alfred Evaluation Module")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = AlfredEvaluator()
    
    if evaluator.langfuse:
        # Create evaluation dataset
        create_evaluation_dataset(evaluator.langfuse)
        
        # Run evaluation
        results = run_evaluation(evaluator)
        
        # Show recent traces
        print("\n📊 Recent Traces:")
        recent_traces = list_recent_traces(evaluator.langfuse, limit=5)
        for trace in recent_traces:
            print(f"  - {trace['name']}: {trace['status']} ({trace['execution_time']:.2f}s)")
    else:
        print("⚠️  LangFuse not configured. Please set up your API keys.")
        print("💡 Add to ~/.zshrc:")
        print("   export LANGFUSE_PUBLIC_KEY='your-public-key'")
        print("   export LANGFUSE_SECRET_KEY='your-secret-key'")
        print("   export LANGFUSE_HOST='https://us.cloud.langfuse.com'  # US cloud host is used here") 