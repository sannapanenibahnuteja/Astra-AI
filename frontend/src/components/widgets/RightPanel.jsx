import { useEffect, useState } from "react";

import "./RightPanel.css";
import GlassPanel from "../ui/GlassPanel";

const API = "http://127.0.0.1:8000";

export default function RightPanel() {

    const [memory, setMemory] = useState({

        count: 0,

        recent: []

    });

    useEffect(() => {

        async function loadMemory() {

            try {

                const response =
                    await fetch(
                        `${API}/memory/recent`
                    );

                const data =
                    await response.json();

                setMemory(data);

            }

            catch (error) {

                console.error(error);

            }

        }

        loadMemory();

        const interval =
            setInterval(
                loadMemory,
                3000
            );

        return () =>
            clearInterval(interval);

    }, []);

    return (

        <aside className="right-panel">

            <GlassPanel className="panel-card">

                <h3>Memory</h3>

                <h2>{memory.count} Memories</h2>

                {

                    memory.recent.length === 0

                        ?

                        <p>No memories yet</p>

                        :

                        <ul className="memory-list">

                            {

                                memory.recent.map(item => (

                                    <li key={item.id}>

                                        {item.value}

                                    </li>

                                ))

                            }

                        </ul>

                }

            </GlassPanel>

        </aside>

    );

}