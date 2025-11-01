import React from 'react'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Sales Analytics Chat Assistant</h1>
        <p>Ask questions about your sales data in natural language</p>
      </header>
      <main>
        <ChatInterface />
      </main>
    </div>
  )
}

export default App
