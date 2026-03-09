import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [expandedAgent, setExpandedAgent] = useState(null);

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const runAnalysis = async () => {
    if (!prompt) return;
    setLoading(true);
    setData(null);
    setExpandedAgent(null);

    try {
      const response = await axios.post(`${apiUrl}/api/analyze`, {
        prompt: prompt
      });
      setData(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("System Error: Connection to neural backend failed.");
    } finally {
      setLoading(false);
    }
  };

  const getAgentIcon = (role) => {
    if (role.includes("Architect")) return "🏗️";
    if (role.includes("Frontend")) return "🎨";
    if (role.includes("Backend")) return "⚙️";
    if (role.includes("Cybersecurity") || role.includes("SecOps")) return "🛡️";
    if (role.includes("DevOps") || role.includes("Lead")) return "👑";
    if (role.includes("Market")) return "📊";
    if (role.includes("Growth")) return "🚀";
    if (role.includes("Financial")) return "💰";
    return "🤖";
  };

  return (
    <div className="app-wrapper">
      <div className="glow-orb orb-1"></div>
      <div className="glow-orb orb-2"></div>

      <div className="glass-container">
        
        {/* --- NEW INSTITUTIONAL BANNER --- */}
        <div className="institutional-banner">
          <img src="reva-logo.png" alt="University Logo" className="uni-logo" />
          <div className="academic-details">
            <h2 className="uni-name">REVA UNIVERSITY</h2>
            <p className="dept-name">B.Tech in Artificial Intelligence & Data Science • 6th Semester</p>
            <div className="credits-bar">
              <span className="credit-divider">•</span>
              <span className="credit-item"><strong>Guide:</strong> Dr. Sunil Manoli </span>
              <span className="credit-divider">•</span>
              <span className="credit-divider">•</span>
              <span className="credit-item"><strong>Student-1 :</strong> Meghana U </span>
              <span className="credit-divider">•</span>
              <span className="credit-item"><strong>Student-2 :</strong> Rajkumar Math </span>
            </div>
          </div>
        </div>

        <header className="header">
          <div className="badge-wrapper">
            <span className="version-badge">Mini Project </span>
          </div>
          <h1 className="neon-text">Multi Agents AI System</h1>
          <p className="subtitle">Autonomous Interactive Dashboard</p>
        </header>

        <main className="main-content">
          <div className="input-card">
            <textarea 
              className="glass-input"
              placeholder="Initialize task... (e.g., 'Design the architecture for an AI crypto wallet')"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <button className="neon-btn" onClick={runAnalysis} disabled={loading}>
              {loading ? (
                <span className="btn-content">
                  <span className="btn-spinner"></span> Simulating Intelligence...
                </span>
              ) : '🚀 Deploy Agent Swarm'}
            </button>
          </div>

          {loading && (
            <div className="glass-loading">
              <div className="pulse-ring"></div>
              <h3>Analyzing User's Intent</h3>
              <p>Gemini 2.5 Flash is orchestrating the agent collaboration...</p>
            </div>
          )}

          {data && (
            <div className="dashboard-layout">
              <div className="routing-status">
                <span className="status-dot"></span>
                Router Deployed: <strong className="glow-text">{data.routed_team} Team</strong>
              </div>

              <div className="agent-grid">
                {data.agent_reports.map((agent, index) => (
                  <div 
                    key={index} 
                    className={`agent-card ${expandedAgent === index ? 'active' : ''}`}
                    onClick={() => setExpandedAgent(expandedAgent === index ? null : index)}
                  >
                    <div className="agent-card-header">
                      <div className="agent-identity">
                        <span className="agent-icon">{getAgentIcon(agent.agent_role)}</span>
                        <h3 className="agent-name">{agent.agent_role}</h3>
                      </div>
                      <span className="toggle-icon">{expandedAgent === index ? '−' : '+'}</span>
                    </div>
                    
                    {expandedAgent === index && (
                      <div className="agent-card-body">
                        <div className="markdown-content custom-scroll">
                          <ReactMarkdown>{agent.output}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="master-summary">
                <h3 className="summary-title">🏆 Final Master Blueprint -Summary </h3>
                <div className="markdown-content">
                  <ReactMarkdown>{data.final_summary}</ReactMarkdown>
                </div>
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
