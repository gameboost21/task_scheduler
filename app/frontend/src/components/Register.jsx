import React, { useState } from 'react'
import { fetchWithAuth } from "../utils/fetchWithAuth"

function Register() {

    const [form, setForm] = useState({ username: '', email: '', password: ''});
    const [message, setMessage] = useState('');

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault()
        try {
            const response = await fetchWithAuth("https://dashboard.tuschkoreit.de/register", {
                method: "POST",
                headers: {
                    "Content-Type" : "application/json"
                },
                body: JSON.stringify(form)
            });
            if (!response.ok) throw new Error("Registration Failed!")
            const data = await response.json()
            setMessage(data.message)
        }catch(err) {
            setMessage("Error: " + err.message)
        }
    }

    return (
        <form onSubmit={handleRegister} className="max-w-sm mx-auto p-6 bg-white rounded shadow space-y-4">
            {message && <p className="text-blue-600">{message}</p>}
            <input type="text" name='username' placeholder='Username' required onChange={handleChange} className="w-full p-2 border rounded"/>
            <input type="email" name='email' placeholder='Email' required onChange={handleChange} className="w-full p-2 border rounded"/>
            <input type="password" name='password' placeholder='Password' required onChange={handleChange} className="w-full p-2 border rounded"/>
            <button type='submit'className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Register</button>
        </form>
    )
}

export default Register