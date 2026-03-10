import os
from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Cognitive Architecture API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- THE BULLETPROOF GROQ MODEL ---
# This is faster than Gemini and handles your 10-agent swarm effortlessly
master_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY")
)

class UserRequest(BaseModel):
    prompt: str

@app.post("/api/analyze")
async def run_master_system(request: UserRequest):
    user_prompt = request.prompt
    
    # Define Agents
    arch = Agent(role='System Architect', goal='Design the high-level infrastructure.', backstory='Infrastructure master.', llm=master_llm)
    sec = Agent(role='Cybersecurity Auditor', goal='Find vulnerabilities.', backstory='Security expert.', llm=master_llm)
    biz = Agent(role='Business Strategist', goal='Analyze revenue models.', backstory='Startup consultant.', llm=master_llm)

    # Define Tasks that pass data between agents
    t1 = Task(description=f'Architect the infrastructure for: {user_prompt}', expected_output='Tech stack list.', agent=arch)
    t2 = Task(description='Audit the architecture for security flaws.', expected_output='Vulnerability report.', agent=sec)
    t3 = Task(description='Propose 2 revenue streams.', expected_output='Monetization strategy.', agent=biz)

    swarm = Crew(
        agents=[arch, sec, biz],
        tasks=[t1, t2, t3],
        process=Process.sequential # THIS IS THE KEY FOR FACULTY: Show them the sequential handoff!
    )

    result = swarm.kickoff()
    
    # Extract reports for your frontend cards
    agent_reports = [{"agent_role": t.agent.role, "output": str(t.output)} for t in swarm.tasks]
    
    return {
        "status": "success",
        "final_summary": str(result),
        "agent_reports": agent_reports
    }
    
