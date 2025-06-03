import React, { useState, useEffect } from 'react'
import TaskForm from "./TaskForm";
import { fetchWithAuth } from '../utils/fetchWithAuth';

function TaskList({ tasks, onDelete }) {

    const handleDelete = async (id) => {
        try {
            const response = await fetchWithAuth(`https://dashboard.tuschkoreit.de/tasks/${id}`, {
                method: "DELETE",
            });
            if (!response.ok) throw new Error("Task could not be deleted");

            // Let the parent re-fetch tasks instead of updating local state
            onDelete();
        } catch (error) {
            console.error("Error deleting task. Error: ", error);
        }
    };

    return (
        <div className="max-w-2xl mx-auto mt-10 space-y-6">
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