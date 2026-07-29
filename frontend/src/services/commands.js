const API =
  "http://127.0.0.1:8000";



export async function executeCommand(message) {


  const response =
    await fetch(
      `${API}/commands/`,
      {

        method:"POST",

        headers:{

          "Content-Type":
            "application/json",

        },


        body:JSON.stringify({

          message

        }),

      }
    );



  return await response.json();

}