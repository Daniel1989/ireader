import { memo, useEffect, useState } from "react";
import { Warning } from "@phosphor-icons/react";
import renderMarkdown from "./markdown";
import { Spin } from 'antd';

const PromptReply = ({
  text,
  pending,
  error,
}: any) => {
  // 会话聊天窗口UI，要包含一个输入框，一个会话历史，有消息时的页面滚动，左边的会话历史

  // TODO 逐字显示依赖response一下子返回，后面优化
  // const [response, setResponse] = useState(text);
  // let interval: NodeJS.Timer;
  // let index = 0;
  // const simulateStream = (text:string) => {
  //   index = 0;
  //   setResponse('');
  //   interval = setInterval(() => {
  //     if (index < text.length) {
  //       setResponse((prev: string) => prev + text[index]);
  //       index++;
  //     } else {
  //       clearInterval(interval);
  //     }
  //   }, 50); // Adjust this speed to make the stream faster/slower
  // };

  // useEffect(() => {
  //   if (text) {
  //     simulateStream(text); // Simulate the stream when the message is updated
  //   }
  //   return () => {
  //     clearInterval(interval);
  //     index = 0;
  //   }
  // }, [text]);


  if (pending) {
    return <span className="pl-2 pr-2 flex-1"><Spin /></span>
  }

  if (error) {
    return <span
      className={`inline-block p-2 rounded-lg bg-red-50 text-red-500 flex-1`}
    >
      <Warning className="h-4 w-4 mb-1 inline-block" /> Could not
      respond to message.
      <span className="text-xs">Reason: {error || "unknown"}</span>
    </span>
  }

  return <span
    className={`reply flex flex-col gap-y-1 mt-2 flex-1`}
    dangerouslySetInnerHTML={{ __html: renderMarkdown(text) }}
  />
};

export default memo(PromptReply);
