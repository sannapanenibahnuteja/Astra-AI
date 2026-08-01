import { useState } from "react";
import "./CommandInput.css";

import { streamMessage } from "../../services/chat";
import { speak } from "../../services/voice";
import { executeCommand } from "../../services/commands";
import { detectWakeWord } from "../../services/wakeWord";

import useChatStore from "../../store/chatStore";
import useAIStateStore from "../../store/aiStateStore";

import MicrophoneButton from "./MicrophoneButton";

export default function CommandInput() {

  const [text, setText] = useState("");
  const [, setVoiceText] = useState("");

  const addMessage =
    useChatStore(state => state.addMessage);

  const updateMessage =
    useChatStore(state => state.updateMessage);

  const setTyping =
    useChatStore(state => state.setTyping);

  const setAIState =
    useAIStateStore(state => state.setState);

  // --------------------------------------------------
  // TEXT CHAT
  // --------------------------------------------------

  async function handleSend(message = text) {

    if (!message.trim())
      return;

    addMessage({
      id: Date.now(),
      role: "user",
      content: message
    });

    setText("");

    setTyping(true);
    setAIState("thinking");

    const id = Date.now() + 1;

    addMessage({
      id,
      role: "assistant",
      content: ""
    });

    let response = "";

    try {

      await streamMessage(

        message,

        partial => {

          response = partial;

          updateMessage(id, partial);

        }

      );

      setTyping(false);
      setAIState("idle");

      if (response.trim()) {
        speak(response);
      }

    }

    catch (error) {

      console.error(error);

      setTyping(false);
      setAIState("error");

    }

  }

  // --------------------------------------------------
  // VOICE
  // --------------------------------------------------

  async function processVoice(text) {

    console.log("VOICE:", text);

    const wake = detectWakeWord(text);

    console.log("WAKE:", wake);

    if (!wake.detected)
      return;

    const command = wake.command?.trim();

    if (!command) {

      speak("Yes?");

      return;

    }

    addMessage({
      id: Date.now(),
      role: "user",
      content: command,
    });

    setAIState("thinking");

    try {

      const result = await executeCommand(command);

      addMessage({
        id: Date.now() + 1,
        role: "assistant",
        content: result.message,
      });

      if (result.message)
        speak(result.message);

    }

    catch (err) {

      console.error(err);

      speak("Sorry, something went wrong.");

    }

    setAIState("idle");

  }

  return (

    <div className="command-input">

      <input

        value={text}

        onChange={(e) => {

          setText(e.target.value);

        }}

        placeholder="Ask Astra anything..."

        onKeyDown={(e) => {

          if (e.key === "Enter")
            handleSend();

        }}

      />

      <MicrophoneButton

        onTranscript={(value) => {

          console.log("LIVE:", value);

          setVoiceText(value);

          setAIState("listening");

        }}

        onComplete={(value) => {

          console.log("FINAL:", value);

          processVoice(value);

        }}

      />

      <button onClick={() => handleSend()}>

        Send

      </button>

    </div>

  );

}