import React from 'react'
import { Link } from 'react-router-dom'

function Navbar({ isAuthenticated, user, onLogout }) {

    return (
        <nav className="bg-gray-800 text-white px-4 py-2 flex justify-between items-center">
            <div className="space-x-4">
                {isAuthenticated && (
                    <>
                        <Link to="/dashboard" className="hover:underline">Dashboard</Link>
                        <Link to="/register" className="hover:underline">Register</Link>
                        {user?.role === "admin" && (
                            <Link to="/admin" className="hover:underline">Admin Panel</Link>
                        )}
                    </>
                )}
            </div>
            <div>
                {isAuthenticated ? (
                    <button onClick={onLogout} className="bg-red-500 px-3 py-1 rounded hover:bg-red-600">
                        Logout
                    </button>
                ) : (
                    <Link to="/login" className="hover:underline">Login</Link>
                )}
            </div>
        </nav>
    )

}
export default Navbar