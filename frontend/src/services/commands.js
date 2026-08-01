const API = "http://127.0.0.1:8000";

/**
 * Sends every command/chat message to Astra's backend.
 * The backend decides whether it is:
 *   - a command
 *   - an AI conversation
 *   - or an AI fallback.
 */
export async function executeCommand(message) {

    console.log("====================================");
    console.log("ASTRA COMMAND");
    console.log("Message:", message);

    try {

        const response = await fetch(`${API}/commands/`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                message,
            }),

        });

        console.log("HTTP Status:", response.status);

        if (!response.ok) {

            throw new Error(
                `Backend returned ${response.status}`
            );

        }

        const result = await response.json();

        console.log("Backend Response:", result);
        console.log("====================================");

        return result;

    } catch (error) {

        console.error("COMMAND ERROR:", error);

        return {

            success: false,

            message:
                "Unable to connect to Astra backend.",

            data: null,

        };

    }

}