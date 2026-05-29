import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<div>GasMap - Coming Soon</div>} />
        </Routes>
      </div>
    </Router>
  )
}

export default App