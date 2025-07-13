import React, { useState } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard')

  return (
    <div className="app">
      <header className="app-header">
        <h1>Amauta Wearable AI Node</h1>
        <p>Complete 13-Class Node System</p>
      </header>
      
      <nav className="app-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'nodes' ? 'active' : ''}
          onClick={() => setActiveTab('nodes')}
        >
          Nodes
        </button>
        <button 
          className={activeTab === 'health' ? 'active' : ''}
          onClick={() => setActiveTab('health')}
        >
          Health
        </button>
      </nav>
      
      <main className="app-main">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <h2>System Dashboard</h2>
            <div className="node-summary">
              <h3>13-Class Node System</h3>
              <div className="node-tiers">
                <div className="tier">
                  <h4>Foundation Tier (4 nodes)</h4>
                  <p>Musa, Hakim, Skald, Oracle</p>
                </div>
                <div className="tier">
                  <h4>Governance Tier (3 nodes)</h4>
                  <p>Junzi, Yachay, Sachem</p>
                </div>
                <div className="tier">
                  <h4>Elder Tier (3 nodes)</h4>
                  <p>Archon, Amauta, Mzee</p>
                </div>
                <div className="tier">
                  <h4>Core Nodes (3 nodes)</h4>
                  <p>Griot, Ronin, Tohunga</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'nodes' && (
          <div className="nodes">
            <h2>Node Management</h2>
            <p>Node management interface will be implemented here.</p>
          </div>
        )}
        
        {activeTab === 'health' && (
          <div className="health">
            <h2>System Health</h2>
            <p>Health monitoring interface will be implemented here.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App 