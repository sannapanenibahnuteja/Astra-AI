import { useEffect, useState } from "react";

import "./SystemHUD.css";


const API =
  "http://127.0.0.1:8000";



function Bar({ value }) {

  return (

    <div className="bar">

      <div

        className="bar-fill"

        style={{
          width: `${value}%`
        }}

      />

    </div>

  );

}



export default function SystemHUD() {


  const [system, setSystem] =
    useState(null);



  useEffect(() => {


    async function fetchSystem(){


      try {


        const response =
          await fetch(
            `${API}/monitor/`
          );


        const data =
          await response.json();


        setSystem(data);


      }

      catch(error){

        console.error(
          error
        );

      }

    }



    fetchSystem();



    const interval =
      setInterval(
        fetchSystem,
        3000
      );



    return () =>
      clearInterval(interval);



  },[]);




  if(!system)
    return null;



  const battery =
    system.battery
      ?
      system.battery.percent
      :
      0;



  return (

    <div className="system-hud">


      <h3>
        ASTRA SYSTEM
      </h3>



      <div className="metric">

        <span>
          CPU
        </span>

        <strong>
          {system.cpu}%
        </strong>

      </div>


      <Bar
        value={system.cpu}
      />



      <div className="metric">

        <span>
          MEMORY
        </span>

        <strong>
          {system.memory}%
        </strong>

      </div>


      <Bar
        value={system.memory}
      />



      <div className="metric">

        <span>
          DISK
        </span>

        <strong>
          {system.disk}%
        </strong>

      </div>


      <Bar
        value={system.disk}
      />



      <div className="metric">

        <span>
          BATTERY
        </span>

        <strong>
          {battery}%
        </strong>

      </div>


      <Bar
        value={battery}
      />



      <p>
        ● SYSTEM ONLINE
      </p>


    </div>

  );

}