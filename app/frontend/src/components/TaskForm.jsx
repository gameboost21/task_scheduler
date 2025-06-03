import { useState } from "react"
import { fetchWithAuth } from "../utils/fetchWithAuth"

const URL = "https://dashboard.tuschkoreit.de/tasks"

function TaskForm({ onTaskCreated }) {
    const [taskname, setTaskname] = useState("")
    const [scheduled, setScheduled] = useState(false)
    const [script_path, setPath] = useState("")
    const [schedule_cron, setCron] = useState("")
    const [script_type, setScript] = useState("")

    const handleSubmit = async (e) => {
        e.preventDefault();

        const newTask = {
            taskname,
            sheduled: scheduled,
            runcount: 0,
            successful: false,
            schedule_cron,
            script_path,
            script_type,

        };

        try {
            const response = await fetchWithAuth("https://dashboard.tuschkoreit.de/tasks", {
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
                    <select
                        value={script_type}
                        onChange={(e) => setScript(e.target.value)}
                    >
                        <option value="python">Python</option>
                        <option value="bash">Bash</option>
                    </select>
                </div>



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
                <div>
                    <input
                        type="text"
                        placeholder="Script path (e.g., scripts/mytask.py)"
                        value={script_path}
                        onChange={(e) => setPath(e.target.value)}
                    />
                </div>
                <div><input
                    type="text"
                    placeholder="Cron expression (e.g., */5 * * * *)"
                    value={schedule_cron}
                    onChange={(e) => setCron(e.target.value)}
                />
                </div>
                <div>
                    <textarea placeholder="Iput Parms"></textarea>
                </div>

                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Create Task
                </button>
            </form>
        </>
    );
}

export default TaskForm