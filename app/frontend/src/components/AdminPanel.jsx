import React, { useState, useEffect } from 'react'
import { fetchWithAuth } from '../utils/fetchWithAuth';

function AdminPanel() {
    const [users, setUsers] = useState([]);
    const [error, setError] = useState("")
    const [expandedUserId, setExpandedUserId] = useState(null)
    const [roles] = useState(["admin", "moderator", "power_user", "viewer"])
    const [approvingId, setApprovingId] = useState(null)

    const fetchUsers = async () => {
        try {
            const response = await fetchWithAuth("https://dashboard.tuschkoreit.de/admin/users")
            if (!response.ok) throw new Error("Error fetching users")
            const data = await response.json();
            setUsers(data)
        } catch (err) {
            setError(err.message);
        }
    }


    const updateUserRole = async (id, newRole) => {
        try {
            const response = await fetchWithAuth(`https://dashboard.tuschkoreit.de/admin/users/${id}/role`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role: newRole })
            });
            if (!response.ok) throw new Error("Failed to update user role");
            await fetchUsers();
        } catch (err) {
            setError(err.message)
        }
    }

    const deleteUser = async (id) => {
        try {
            const response = await fetchWithAuth(`https://dashboard.tuschkoreit.de/admin/users/${id}`, {
                method: "DELETE"
            });
            if (!response.ok) throw new Error("Failed to delete Users");
            fetchUsers()
        } catch (err) {
            setError(err.message)
        }
    }

    const approveUser = async (id) => {
        setApprovingId(id)
        try {
            const response = await fetchWithAuth(`https://dashboard.tuschkoreit.de/admin/approve/${id}`, {
                method: "POST"
            });
            if (!response.ok) throw new Error("Failed to Approve User or User doesn`t exist");
            await fetchUsers()
        } catch (err) {
            setError(err.message);
        } finally {
            setApprovingId(null)
        }
    };


    useEffect(() => {
        fetchUsers();
    }, []);

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Admin Panel</h2>
            {error && <div className="text-red-500">{error}</div>}
            <ul className="space-y-2">
                {users.map((user) => (
                    <li key={user.id} className="flex justify-between items-center border-b pb-2">
                        <div className="flex justify-between items-center">
                            <span className='font-medium'>{user.username}</span>
                            <div className="flex space-x-2">
                                <select
                                    value={user.role}
                                    onChange={(e) => updateUserRole(user.id, e.target.value)}
                                    className="border rounded px-2 py-1"
                                >
                                    {roles.map(r => <option key={r} value={r}>{r}</option>)}
                                </select>
                                <button
                                    onClick={() => setExpandedUserId(expandedUserId === user.id ? null : user.id)}
                                    className="text-blue-500 underline"
                                >
                                    {expandedUserId === user.id ? 'Hide' : 'Details'}
                                </button>
                                
                                {!user.is_active && (
                                    <button
                                        onClick={() => approveUser(user.id)}
                                        disabled= {approvingId === user.id}
                                        className="bg-green-500 text-white px-2 py-1 rounded hover:bg-green-600"
                                    >
                                        {approvingId === user.id ? "Approving..." : "Approved"}
                                    </button>
                                )}
                                
                                <button
                                    onClick={() => deleteUser(user.id)}
                                    className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>

                        {expandedUserId === user.id && (
                            <div className="mt-2 text-sm text-gray-700">
                                <p><strong>ID:</strong> {user.id}</p>
                                <p><strong>Email:</strong> {user.email}</p>
                                <p><strong>Active:</strong> {String(user.is_active)}</p>
                                <p><strong>Role:</strong> {user.role}</p>
                            </div>
                        )}

                    </li>
                ))}
            </ul>
        </div>
    )
}
export default AdminPanel