import React, { useEffect, useState } from 'react';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import Login from './components/Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Tracks login status
  const [tasks, setTasks] = useState([]);

  // ✅ Fetch tasks using token from localStorage (always read it fresh)
  const fetchTasks = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("No token found in localStorage.");
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
      setIsAuthenticated(true); // ✅ Successful fetch means user is authenticated
    } catch (error) {
      console.error("Error fetching tasks:", error);
      setIsAuthenticated(false); // ❌ Token might be invalid or expired
    }
  };

  // ✅ Automatically try to fetch tasks if we think the user is authenticated
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetchTasks();
    }
  }, []); // run only on initial mount

  // ✅ Called when login succeeds from Login.jsx
  const handleLogin = () => {
    setIsAuthenticated(true); // Trigger re-render to show the authenticated view
  };

  // ✅ Logout: clear token and reset state
  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setTasks([]);
  };

  // ❗ Only show login form if user is not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="p-4 space-y-6">
      <button
        onClick={handleLogout}
        className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
      >
        Logout
      </button>
      <TaskForm onTaskCreated={fetchTasks} />
      <TaskList tasks={tasks} onDelete={fetchTasks} />
    </div>
  );
}

export default App;
