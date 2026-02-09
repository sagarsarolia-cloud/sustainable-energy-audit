import { useState } from 'react'
import Upload from './components/Upload'
import AuditDashboard from './components/AuditDashboard'
import './App.css'

function App() {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAuditComplete = (data) => {
    setAuditData(data);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <header className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800">
        <h1 className="text-xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
          Sustainable Energy Auditor
        </h1>
        <div className="text-sm text-gray-400">Powered by Gemini 3 Pro</div>
      </header>

      <main className="container mx-auto p-4 py-8">
        {!auditData ? (
          <Upload
            onAuditComplete={handleAuditComplete}
            loading={loading}
            setLoading={setLoading}
          />
        ) : (
          <AuditDashboard
            data={auditData}
            onReset={() => setAuditData(null)}
          />
        )}
      </main>
    </div>
  )
}

export default App
