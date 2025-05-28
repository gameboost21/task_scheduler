import React, { useDebugValue, useEffect, useState } from 'react'

const URL = "https://dashboard.tuschkoreit.de/tasks"

function GetData() {

    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchTasks = async () => {
        try {
            const reponse = await fetch(URL);

            const data = await reponse.json();
            console.log("Fetched tasks: ", data);
            setTasks(data);

        } catch (err) {
            console.error("Fetch Error: ", err)
            setError(err.message)
        } finally {
            setLoading(false)
        }

    }
    useEffect(() => {
        fetchTasks();
    }, []);

    if (loading) return <p>Loading tasks...</p>;
    if (error) return <p>Error: {error}</p>;


    return (
        <div>
            <ul className="space-y-4">
                {tasks.map((task) => (
                    <li 
                    key={task.id} 
                    className="bg-white shadow-md rounded-xl p-4 border border-gray-200"
                    >
                        <h2 className="text-xl font-semibold text-blue-700 mb-2">{task.taskname}</h2>
                        <p className="text-sm text-gray-700">ID: {task.id}</p>
                        <p className="text-sm text-gray-700">Run Count: {task.runcount}</p>
                        <p className="text-sm text-gray-700">
                         Scheduled:{" "}
                        <span className={task.sheduled ? "text-green-600" : "text-red-600"}>
                        {task.sheduled ? "Yes" : "No"}
                        </span>
                        </p>
                        <p className="text-sm text-gray-700">
                        Successful:{" "}
                        <span className={task.successful ? "text-green-600" : "text-red-600"}>
                        {task.successful ? "Yes" : "No"}
                         </span>
                        </p>
                    </li>))}
            </ul>
        </div>
    )

}
export default GetData