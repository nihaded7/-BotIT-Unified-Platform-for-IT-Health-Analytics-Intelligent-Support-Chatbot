from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.chatboot.retrieval import RetrievalSystem
from backend.chatboot.gpt_client import ask_gpt
from pathlib import Path
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

csv_path = Path(__file__).parent / "Data/processed/IT_Troubleshooting_Dset_ready.csv"
if not csv_path.exists():
    raise FileNotFoundError(f"CSV not found at: {csv_path}")

retrieval_system = RetrievalSystem(csv_path)

app = FastAPI()

# In-memory storage for conversation sessions (in production, use Redis or database)
conversation_sessions: Dict[str, dict] = {}

class Query(BaseModel):
    question: str
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    message: str

@app.get("/")
def root():
    return {"message": "API is running!"}

@app.post("/start-session")
def start_session():
    """Start a new conversation session"""
    session_id = str(uuid.uuid4())
    conversation_sessions[session_id] = {
        "created_at": datetime.now(),
        "problem": None,
        "solution": None,
        "current_step": None,
        "conversation_history": [],
        "last_activity": datetime.now()
    }
    return SessionResponse(session_id=session_id, message="New session started")

@app.post("/chat")
def chat(query: Query):
    # Generate session ID if not provided
    if not query.session_id:
        query.session_id = str(uuid.uuid4())
        conversation_sessions[query.session_id] = {
            "created_at": datetime.now(),
            "problem": None,
            "solution": None,
            "current_step": None,
            "conversation_history": [],
            "last_activity": datetime.now()
        }
    
    session_id = query.session_id
    
    # Get or create session
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "created_at": datetime.now(),
            "problem": None,
            "solution": None,
            "current_step": None,
            "conversation_history": [],
            "last_activity": datetime.now()
        }
    
    session = conversation_sessions[session_id]
    session["last_activity"] = datetime.now()
    
    # Add user question to history
    session["conversation_history"].append({
        "role": "user",
        "content": query.question,
        "timestamp": datetime.now()
    })
    
    # Check if this is a follow-up question about a previous solution
    is_followup = is_followup_question(query.question, session)
    
    if is_followup and session["solution"]:
        # This is a follow-up question, use GPT with full context
        try:
            context = build_conversation_context(session)
            gpt_answer = ask_gpt_with_context(query.question, context)
            
            # Add bot response to history
            session["conversation_history"].append({
                "role": "bot",
                "content": gpt_answer,
                "timestamp": datetime.now(),
                "source": "gpt_context"
            })
            
            return {
                "source": "gpt_context",
                "similarity": None,
                "answer": gpt_answer,
                "session_id": session_id,
                "is_followup": True
            }
        except Exception as e:
            print("GPT context error:", e)
            # Fall back to regular GPT
            pass
    
    # Try retrieval first
    try:
        response, score, matched_issue = retrieval_system.search(query.question, top_k=3, threshold=0.5)
        print(f"[Retrieval] best_match_score={score:.3f} matched_issue={matched_issue}")
    except Exception as e:
        print("Retrieval error:", e)
        response, score, matched_issue = None, 0.0, None

    # Only use database response if it's a high-confidence match AND not a follow-up question
    if response and score >= 0.5 and not is_followup:
        # Update session with new problem and raw KB solution
        session["problem"] = query.question
        session["solution"] = response
        session["current_step"] = 1

        # Ask GPT to polish the KB answer into a conversational, step-by-step response
        try:
            kb_prompt = (
                "You are an IT support assistant.\n"
                "Below is a knowledge-base solution relevant to the user's problem.\n"
                "Rewrite it as a concise, friendly, step-by-step response.\n"
                "- Keep only factual steps from the KB, do not invent.\n"
                "- Clarify where needed.\n"
                "- Prefer bullet points or short numbered steps.\n\n"
                f"User question: {query.question}\n\n"
                f"Knowledge-base solution:\n{response}\n"
            )
            polished_answer = ask_gpt(kb_prompt)
        except Exception as e:
            print("GPT polish error:", e)
            polished_answer = response  # fallback to raw KB text

        final_answer = f"{polished_answer}\n\nSource: Knowledge Base (RAG)"

        # Add bot response to history
        session["conversation_history"].append({
            "role": "bot",
            "content": final_answer,
            "timestamp": datetime.now(),
            "source": "gpt_kb"
        })

        return {
            "source": "gpt_kb",
            "similarity": score,
            "answer": final_answer,
            "session_id": session_id,
            "is_followup": False
        }
    elif response and score >= 0.5 and is_followup:
        # High confidence match but it's a follow-up question - use GPT with context instead
        print(f"Follow-up question matched database with {score} confidence, using GPT with context instead")
        pass

    # GPT fallback
    try:
        # If we have previous context, use it
        if session["problem"] and session["solution"]:
            context = build_conversation_context(session)
            gpt_answer = ask_gpt_with_context(query.question, context)
        else:
            gpt_answer = ask_gpt(query.question)
        
        # Append source footer
        footer = "Source: GPT with context" if (session["problem"] and session["solution"]) else "Source: GPT fallback"
        final_gpt_answer = f"{gpt_answer}\n\n{footer}"

        # Add bot response to history
        session["conversation_history"].append({
            "role": "bot",
            "content": final_gpt_answer,
            "timestamp": datetime.now(),
            "source": "gpt"
        })
        
        return {
            "source": "gpt",
            "similarity": None,
            "answer": final_gpt_answer,
            "session_id": session_id,
            "is_followup": False
        }
    except Exception as e:
        print("GPT error:", e)
        error_msg = "❌ Failed to get an answer. Please try again."
        
        # Add error to history
        session["conversation_history"].append({
            "role": "bot",
            "content": error_msg,
            "timestamp": datetime.now(),
            "source": "error"
        })
        
        return {
            "source": "error",
            "similarity": None,
            "answer": error_msg,
            "session_id": session_id,
            "is_followup": False
        }

@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Get conversation session details"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return conversation_sessions[session_id]

@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Delete a conversation session"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": "Session deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

# Clean up old sessions (older than 24 hours)
@app.on_event("startup")
def cleanup_old_sessions():
    """Clean up old sessions on startup"""
    current_time = datetime.now()
    expired_sessions = [
        sid for sid, session in conversation_sessions.items()
        if current_time - session["last_activity"] > timedelta(hours=24)
    ]
    for sid in expired_sessions:
        del conversation_sessions[sid]

def is_followup_question(question: str, session: dict) -> bool:
    """Determine if this is a follow-up question about a previous solution"""
    if not session["solution"]:
        return False
    
    # Keywords that indicate follow-up questions
    followup_keywords = [
        "don't understand", "don't get", "confused", "unclear",
        "step", "how to", "what does", "explain", "clarify",
        "not working", "doesn't work", "still have", "still experiencing",
        "help", "assist", "guide", "walk me through",
        "this didn't work", "this solution didn't work", "it's not working",
        "tried this", "already tried", "still not working", "doesn't help",
        "not helping", "still have the problem", "problem persists"
    ]
    
    question_lower = question.lower()
    
    # Check for follow-up keywords
    has_followup_keywords = any(keyword in question_lower for keyword in followup_keywords)
    
    # Additional check: if the question is very short and contains negative words, it's likely a follow-up
    is_short_negative = (
        len(question.split()) <= 5 and 
        any(word in question_lower for word in ["not", "didn't", "doesn't", "still", "this", "that"])
    )
    
    return has_followup_keywords or is_short_negative

def build_conversation_context(session: dict) -> str:
    """Build context string for GPT based on conversation history"""
    context = f"""You are an IT support specialist helping with a technical issue.

Previous Problem: {session['problem']}

Previous Solution Provided: {session['solution']}

Current Conversation History:
"""
    
    # Add last few exchanges for context
    recent_history = session["conversation_history"][-4:]  # Last 4 exchanges
    for exchange in recent_history:
        role = "User" if exchange["role"] == "user" else "Support"
        context += f"{role}: {exchange['content']}\n"
    
    context += f"""

IMPORTANT CONTEXT: The user is currently experiencing issues with: {session['problem']}
You provided this solution: {session['solution']}

The user is now saying the solution didn't work or they need clarification. 

Please provide a helpful, contextual response that:
1. Acknowledges their current problem
2. Offers alternative solutions or troubleshooting steps
3. Asks clarifying questions if needed
4. Is supportive and understanding

Be conversational and supportive. If they're saying something isn't working, help troubleshoot further with specific steps."""
    
    return context

def ask_gpt_with_context(question: str, context: str) -> str:
    """Ask GPT with conversation context"""
    from backend.chatboot.gpt_client import ask_gpt
    
    # Combine context and question
    full_prompt = f"{context}\n\nUser's current question: {question}"
    
    try:
        return ask_gpt(full_prompt)
    except Exception as e:
        print(f"Error asking GPT with context: {e}")
        # Fall back to regular GPT
        return ask_gpt(question)
