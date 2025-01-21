import { v4 } from "uuid";
import { fetchEventSource } from "@microsoft/fetch-event-source";

export const ABORT_STREAM_EVENT = "abort-chat-stream";

const stopListenerList: (() => void)[] = [];


export const streamChat = async function (message: string, handleChat: any, attachments = []) {
    const ctrl = new AbortController();
    const token  = window.localStorage.getItem("anythingllm_authToken");
    const stopListener = () => {
      ctrl.abort();
      handleChat({ id: v4(), type: "stopGeneration" });
    }
    stopListenerList.forEach(listener => window.removeEventListener(ABORT_STREAM_EVENT, listener));
    stopListenerList.length = 0;
    stopListenerList.push(stopListener);
    window.addEventListener(ABORT_STREAM_EVENT, stopListener);

    // 与服务端的交互
    await fetchEventSource(`${window.location.origin}/kl/chat`, {
      method: "POST",
      body: JSON.stringify({ message, attachments }),
      headers: {
        "Authorization": `Bearer ${token}` 
      },
      signal: ctrl.signal,
      openWhenHidden: true,
      async onopen(response:any) {
        if (response.ok) {
          return; // everything's good
        } else if (
          response.status >= 400 &&
          response.status < 500 &&
          response.status !== 429
        ) {
          handleChat({
            id: v4(),
            type: "abort",
            textResponse: null,
            sources: [],
            close: true,
            error: `An error occurred while streaming response. Code ${response.status}`,
          });
          ctrl.abort();
          throw new Error("Invalid Status code response.");
        } else {
          handleChat({
            id: v4(),
            type: "abort",
            textResponse: null,
            sources: [],
            close: true,
            error: `An error occurred while streaming response. Unknown Error.`,
          });
          ctrl.abort();
          throw new Error("Unknown error");
        }
      },
      async onmessage(msg:any) {
        try {
          const chatResult = JSON.parse(msg.data);
          handleChat(chatResult);
        } catch {}
      },
      onerror(err:any) {
        handleChat({
          id: v4(),
          type: "abort",
          textResponse: null,
          sources: [],
          close: true,
          error: `An error occurred while streaming response. ${err.message}`,
        });
        ctrl.abort();
        throw new Error();
      },
    });
  }