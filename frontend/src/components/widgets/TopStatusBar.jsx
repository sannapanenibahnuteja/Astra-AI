import { useEffect, useState } from "react";
import "./TopStatusBar.css";

const API = "http://127.0.0.1:8000";

export default function TopStatusBar() {

    const [system,setSystem]=useState({

        cpu:0,
        memory:0,
        disk:0,
        battery:{percent:0}

    });

    const [time,setTime]=useState("");

    useEffect(()=>{

        async function fetchSystem(){

            try{

                const response=
                    await fetch(`${API}/monitor/`);

                const data=
                    await response.json();

                setSystem(data);

            }

            catch(e){

                console.error(e);

            }

        }

        fetchSystem();

        const interval=
            setInterval(fetchSystem,3000);

        return()=>clearInterval(interval);

    },[]);



    useEffect(()=>{

        function updateClock(){

            const now=new Date();

            setTime(

                now.toLocaleTimeString([],{

                    hour:"2-digit",

                    minute:"2-digit"

                })

            );

        }

        updateClock();

        const timer=
            setInterval(updateClock,1000);

        return()=>clearInterval(timer);

    },[]);



    return(

        <header className="topbar">

            <div className="logo">

                ⚡ ASTRA

            </div>

            <div className="status">

                <div className="chip">

                    CPU {system.cpu.toFixed(0)}%

                </div>

                <div className="chip">

                    RAM {system.memory.toFixed(0)}%

                </div>

                <div className="chip">

                    DISK {system.disk.toFixed(0)}%

                </div>

                <div className="chip">

                    BAT {system.battery?.percent ?? 0}%

                </div>

                <div className="chip online">

                    ● ONLINE

                </div>

                <div className="chip">

                    {time}

                </div>

            </div>

        </header>

    );

}