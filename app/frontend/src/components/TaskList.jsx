import React, { useState, useEffect } from 'react'
import TaskForm from "./TaskForm";

function TaskList() {
    const [tasks, setTasks] = useState([]);

    const fetchTasks = async () => {
        const response = await fetch("https://dashboard.tuschkoreit.de/tasks")
        const data = await response.json();
        setTasks(data)
    };

    useEffect(() => {
        fetchTasks();
    }, []);

    const handleTaskCreated = (newTask) => {
        setTasks((p) => [...p, newTask]);
    };

    const handleDelete = async (id) => {
        try {
            const response = await fetch(`https://dashboard.tuschkoreit.de/tasks/${id}`, {
                method: "DELETE",
            });
            if (!response.ok) throw new Error("Task could not be deleted")

            setTasks((prevTasks) => prevTasks.filter((task) => task.id !== id));
        } catch (error) {
            console.error("Error deleting task. Error: ", error)
        }

    }

    return (
        <div className="max-w-2xl mx-auto mt-10 space-y-6">
            <TaskForm onTaskCreated={handleTaskCreated} />
            <ul className="space-y-2">
                {tasks.map((task) => (
                    <li
                        key={task.id}
                        className="flex justify-between items-center p-4 bg-gray-100 rounded shadow"
                    >
                        <div>
                            <p className="font-semibold">{task.taskname}</p>
                            <p className="text-sm text-gray-600">
                                Scheduled: {task.sheduled ? "Yes" : "No"}, Runs: {task.runcount}
                            </p>
                        </div>
                        <button
                            onClick={() => handleDelete(task.id)}
                            className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                        >
                            Delete
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    )

}

export default TaskList