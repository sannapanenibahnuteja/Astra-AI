import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function TaskCard() {

    const [tasks, setTasks] = useState([]);

    async function loadTasks() {

        try {

            const response = await fetch(`${API}/tasks/`);

            const data = await response.json();

            setTasks(data);

        }

        catch (err) {

            console.error(err);

        }

    }

    useEffect(() => {

        loadTasks();

        const interval = setInterval(loadTasks, 3000);

        return () => clearInterval(interval);

    }, []);

    return (

        <>

            <h3>Today's Tasks</h3>

            {

                tasks.length === 0 ?

                (

                    <p>No tasks</p>

                )

                :

                (

                    tasks.map(task => (

                        <div
                            key={task.id}
                            style={{
                                marginBottom:12,
                                display:"flex",
                                alignItems:"center",
                                gap:"10px"
                            }}
                        >

                            <input
                                type="checkbox"
                                checked={task.completed === 1}
                                readOnly
                            />

                            <span>

                                {task.title}

                            </span>

                        </div>

                    ))

                )

            }

        </>

    );

}