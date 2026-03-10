import os
from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# NEW: Import the model provider directly to avoid 'crewai' path issues
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

app = FastAPI(title="Cognitive Architecture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THE BULLETPROOF INTEGRATION ---
# This bypasses the 'crewai' internal LLM routing and uses the stable LangChain provider
master_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

# ... (Keep your existing agents and tasks exactly as they are) ...
# When you define your Agents, you don't even need to change anything else!
# Just pass 'master_llm' into the llm= parameter of your agents.



class UserRequest(BaseModel):
    prompt: str

@app.post("/api/analyze")
async def run_master_system(request: UserRequest):
    user_prompt = request.prompt
    
    # ==========================================
    # THE MASTER ROUTER
    # ==========================================
    router_agent = Agent(role='Master Router', goal='Classify user inputs accurately into domain categories.', backstory='You are a hyper-logical classification AI. You only output exactly one word: BUSINESS or TECHNICAL.', verbose=False, llm=master_llm)
    routing_task = Task(description=f'Analyze this prompt: "{user_prompt}". If it asks about software, architecture, code, databases, or cybersecurity, output the word TECHNICAL. If it asks about startups, markets, growth, or revenue, output the word BUSINESS. Output NOTHING ELSE.', expected_output='Exactly one word: BUSINESS or TECHNICAL.', agent=router_agent)
    
    router_crew = Crew(agents=[router_agent], tasks=[routing_task])
    route_result = router_crew.kickoff()
    decision = route_result.raw.strip().upper()

    # ==========================================
    # STACK 1: THE BUSINESS CREW
    # ==========================================
    market_analyst = Agent(role='Market Analyst', goal='Analyze the competitive landscape and target audience.', backstory='Expert in market trends and identifying competitors.', verbose=True, llm=master_llm)
    growth_marketer = Agent(role='Growth Marketer', goal='Design a zero-budget user acquisition strategy.', backstory='Growth hacker who specializes in viral marketing and initial user adoption.', verbose=True, llm=master_llm)
    financial_agent = Agent(role='Financial Strategist', goal='Evaluate revenue models and profitability.', backstory='Startup CFO focusing on sustainable monetization.', verbose=True, llm=master_llm)
    biz_lead = Agent(role='Lead Business Consultant', goal='Synthesize all business research into a final executive summary.', backstory='Elite consultant who writes crisp, actionable boardroom reports.', verbose=True, llm=master_llm)

    task_biz_1 = Task(description=f'Analyze market demand and competitors for: "{user_prompt}".', expected_output='Market analysis summary with 2 competitors.', agent=market_analyst)
    task_biz_2 = Task(description=f'Based on the market analysis for "{user_prompt}", suggest a 3-step go-to-market strategy.', expected_output='A 3-step growth hacking plan.', agent=growth_marketer)
    task_biz_3 = Task(description=f'Suggest two realistic revenue models for: "{user_prompt}".', expected_output='Financial strategy and pricing tiers.', agent=financial_agent)
    task_biz_4 = Task(description='Combine the market analysis, growth strategy, and financial models into a highly structured 3-section executive report.', expected_output='Final structured business report.', agent=biz_lead)

    business_crew = Crew(agents=[market_analyst, growth_marketer, financial_agent, biz_lead], tasks=[task_biz_1, task_biz_2, task_biz_3, task_biz_4], process=Process.sequential)

    # ==========================================
    # STACK 2: THE TECH & CYBERSECURITY CREW
    # ==========================================
    system_architect = Agent(role='System Architect', goal='Design the high-level cloud and system architecture.', backstory='Elite architect who maps out scalable infrastructure.', verbose=True, llm=master_llm)
    frontend_dev = Agent(role='Frontend Specialist', goal='Design the UI/UX component structure.', backstory='Expert in modern component-driven user interfaces.', verbose=True, llm=master_llm)
    backend_dev = Agent(role='Backend & API Engineer', goal='Design the database schema and API endpoints.', backstory='Data engineer specializing in high-performance RESTful APIs.', verbose=True, llm=master_llm)
    secops_agent = Agent(role='Cybersecurity Auditor', goal='Identify vulnerabilities and ensure data protection.', backstory='Hardened threat hunter who finds flaws in network protocols.', verbose=True, llm=master_llm)
    tech_lead = Agent(role='Lead DevOps Engineer', goal='Synthesize the tech designs into a unified technical blueprint.', backstory='Senior engineering manager who writes clear technical documentation.', verbose=True, llm=master_llm)

    task_tech_1 = Task(description=f'Design the high-level architecture components for: "{user_prompt}".', expected_output='List of required infrastructure components.', agent=system_architect)
    task_tech_2 = Task(description=f'Outline the core UI screens and frontend component structure needed for: "{user_prompt}".', expected_output='Frontend UI/UX breakdown.', agent=frontend_dev)
    task_tech_3 = Task(description=f'Define the 3 primary API endpoints and core database tables needed for: "{user_prompt}".', expected_output='Backend API and database schema overview.', agent=backend_dev)
    task_tech_4 = Task(description=f'Review the proposed architecture for "{user_prompt}" and list 2 critical security vulnerabilities that must be mitigated.', expected_output='Security audit and mitigation report.', agent=secops_agent)
    task_tech_5 = Task(description='Combine the system architecture, frontend layout, backend APIs, and security audit into a highly structured 4-section Technical Blueprint.', expected_output='Final structured technical architecture document.', agent=tech_lead)

    tech_crew = Crew(agents=[system_architect, frontend_dev, backend_dev, secops_agent, tech_lead], tasks=[task_tech_1, task_tech_2, task_tech_3, task_tech_4, task_tech_5], process=Process.sequential)
    # ==========================================
    # EXECUTION
    # ==========================================
    
    # 1. Handle the Router Result (Type-safe)
    if hasattr(route_result, 'raw'):
        decision = route_result.raw.strip().upper()
    else:
        decision = str(route_result).strip().upper()

    agent_reports = []
    
    # 2. Run the chosen crew
    if "TECHNICAL" in decision:
        final_result = tech_crew.kickoff()
        team_used = "Technical"
        target_crew = tech_crew
    else:
        final_result = business_crew.kickoff()
        team_used = "Business"
        target_crew = business_crew

    # 3. Handle the Final Result (Type-safe)
    if hasattr(final_result, 'raw'):
        final_summary = final_result.raw
    else:
        final_summary = str(final_result)

    # 4. Extract individual agent outputs
    for task in target_crew.tasks:
        output_text = task.output.raw if hasattr(task.output, 'raw') else str(task.output)
        agent_reports.append({
            "agent_role": task.agent.role,
            "output": output_text
        })

    return {
        "status": "success",
        "routed_team": team_used,
        "final_summary": final_summary,
        "agent_reports": agent_reports
    }
    
