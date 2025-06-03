import React, { useState } from 'react'


function Login({ onLogin }) {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState(null)

    const handleLogin = async (e) => {
        e.preventDefault()


        const formData = new URLSearchParams();
        formData.append("username", username)
        formData.append("password", password)

        try {
            const response = await fetch("https://dashboard.tuschkoreit.de/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error("Login Failed")
            }

            const data = await response.json();
            // console.log("Login response data: ", data)
            const token = data.access_token;
            // console.log("Token: ", token)

            if(!token) {
                throw new Error("No token in response")
            }

            localStorage.setItem("token", token)
            onLogin()
        } catch (err) {
            setError("Invalid username or password")
        }
    }

    return (
        <form onSubmit={handleLogin} className="space-y-4 max-w-sm mx-auto bg-white p-6 rounded shadow">
            <h2 className="text-xl font-bold text-center">Login</h2>
            {error && <p className="text-red-500">{error}</p>}
            <div>
                <label className="block mb-1 font-medium">Username:</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    className="w-full border p-2 rounded"
                />
            </div>
            <div>
                <label className="block mb-1 font-medium">Password:</label>
                <input type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full border p-2 rounded"
                />
            </div>
            <button
                type='submit'
                className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
            >
                Login
            </button>
        </form>
    );
}

export default Login