import React, { useEffect, useState, useSyncExternalStore } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import Login from './components/Login';
import Register from './components/Register';
import AdminPanel from './components/AdminPanel';
import Navbar from './components/Navbar';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Tracks login status
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true)

  const parseJwt = (token) => {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
      return null;
    }
  }

  // ✅ Fetch tasks using token from localStorage (always read it fresh)
  const fetchTasks = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("No token found in localStorage.");
      setLoading(false)
      return;
    }

    try {
      const response = await fetch("https://dashboard.tuschkoreit.de/tasks", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Unauthorized");
      }

      const data = await response.json();
      setTasks(data);
      const decoded = parseJwt(token)
      setUser(decoded)
      setIsAuthenticated(true); // ✅ Successful fetch means user is authenticated
    } catch (error) {
      console.error("Error fetching tasks:", error);
      setIsAuthenticated(false); // ❌ Token might be invalid or expired
      setUser(null)
    } finally {
      setLoading(false)
    }
  };

  // ✅ Automatically try to fetch tasks if we think the user is authenticated
  useEffect(() => {
    fetchTasks();
  }, []); // run only on initial mount

  // ✅ Called when login succeeds from Login.jsx
  const handleLogin = () => {
    setIsAuthenticated(true); // Trigger re-render to show the authenticated view
    fetchTasks();
  };

  // ✅ Logout: clear token and reset state
  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setUser(null)
    setTasks([]);
  };

  // ❗ Only show login form if user is not authenticated
  // if (!isAuthenticated) {
  //  return <Login onLogin={handleLogin} />;
  // }

  return (
    <Router>
      <Navbar isAuthenticated={isAuthenticated} user={user} onLogout={handleLogout} />
      <Routes>
        {/* Public Routes */}
        <Route path='/login' element={<Login onLogin={handleLogin} />} />
        <Route path='/register' element={<Register />} />
        {/* Protected Route */}

        <Route
          path='/dashboard'
          element={
            isAuthenticated ? (
              <div className="p-4 space-y-6">
                {user?.role !== 'viewer' && (
                  <TaskForm onTaskCreated={fetchTasks} />
                )}
                <TaskList tasks={tasks} onDelete={fetchTasks} />
              </div>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path='/admin'
          element={
            isAuthenticated && user?.role === 'admin' ? (
              <AdminPanel />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Default Route */}
        <Route path='*' element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </Router>
  );
}

export default App;
