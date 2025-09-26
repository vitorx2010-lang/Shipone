import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import Shipments from './components/Shipments'
import Tracking from './components/Tracking'
import './App.css'

function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [token, setToken] = useState(null)
  const [currentPage, setCurrentPage] = useState('dashboard')

  useEffect(() => {
    // Verificar se há token salvo no localStorage
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      setToken(savedToken)
      setCurrentUser(JSON.parse(savedUser))
    }
  }, [])

  const handleLogin = (user, userToken) => {
    setCurrentUser(user)
    setToken(userToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setCurrentUser(null)
    setToken(null)
    setCurrentPage('dashboard')
  }

  // Simular navegação baseada em hash
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1) || 'dashboard'
      setCurrentPage(hash)
    }

    window.addEventListener('hashchange', handleHashChange)
    handleHashChange() // Executar na inicialização

    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const renderPage = () => {
    switch (currentPage) {
      case 'shipments':
        return <Shipments token={token} />
      case 'tracking':
        return <Tracking />
      case 'dashboard':
      default:
        return <Dashboard token={token} />
    }
  }

  if (!currentUser) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <Layout currentUser={currentUser} onLogout={handleLogout}>
      {renderPage()}
    </Layout>
  )
}

export default App
