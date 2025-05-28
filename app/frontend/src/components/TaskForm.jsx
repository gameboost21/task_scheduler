import { useState } from "react"

const URL = "https://dashboard.tuschkoreit.de/tasks"

function TaskForm({ onTaskCreated }) {
    const [taskname, setTaskname] = useState("")
    const [scheduled, setScheduled] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault();

        const newTask = {
            taskname,
            sheduled: scheduled,
            runcount: 0,
            successful: false
        };

        try {
            const response = await fetch("https://dashboard.tuschkoreit.de/tasks", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(newTask)
            });
            if (!response.ok) {
                throw new Error("Failed to create Task")
            }

            const createdTask = await response.json();
            onTaskCreated(createdTask);
            setTaskname("");
            setScheduled(false);
        } catch (error) {
            console.error("Error creating Task. Error: ", error)
        }
    }

    return (
        <>
            <form onSubmit={handleSubmit} className="space-y-4 bg-white p-4 shadow rounded max-w-md mx-auto">
                <h2 className="text-xl font-bold">Create a new Task</h2>
                <div>
                    <label className="block font-medium">Task Name:</label>
                    <input
                        type="text"
                        value={taskname}
                        onChange={(e) => setTaskname(e.target.value)}
                        className="w-full border p-2 rounded"
                        required
                    />
                </div>

                <div>
                    <input
                        type="checkbox"
                        checked={scheduled}
                        onChange={(e) => setScheduled(e.target.checked)}
                        className="mr-2"
                    />
                    <label>Scheduled?</label>
                </div>

                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Create Task
                </button>
            </form>
        </>
    );
}

export default TaskForm