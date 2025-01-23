// components/ChatUI.js
import { useEffect, useRef, useState } from 'react';
import { ABORT_STREAM_EVENT, streamChat } from './streamChat';
import Message from './message';
import { PauseOutlined, SendOutlined } from '@ant-design/icons';
import { Empty, Input } from 'antd';
import { useSearchParams } from 'react-router-dom';
import { HOST } from '../../../constnat';

export default function ChatContainer(props: any) {
  const { selectedIds, conversationId } = props;
  const [messages, setMessages] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [input, setInput] = useState('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  let generatorTimeout: NodeJS.Timer;

  const stopGeneration = (e: any) => {
    e.stopPropagation();
    setGenerating(false);
    window.dispatchEvent(new CustomEvent(ABORT_STREAM_EVENT));
    generatorTimeout && clearTimeout(generatorTimeout);
    const lastMessage = messages[messages.length - 1];
    if (lastMessage.pending) {
      setMessages((msgs) => [...msgs.slice(0, -1)]);
    }
  }

  const sendMessage = () => {
    if (generating) {
      return;
    } else if (input.trim()) {
      setGenerating(true);
      setMessages([...messages, { text: input, user: 'You' }, { text: '', pending: true, user: 'AI' }]);
      setInput('');
      // Simulate a response from the bot or other user
      // 优化聊天时滚动
      // 优化聊天时再次发送
      // 优化停止生成
      generatorTimeout = setTimeout(() => {
        streamChat(input, (values: any) => {
          if (values.type === "stopGeneration") {
            setGenerating(false);
          } else {
            chatContainerRef.current?.scrollTo({ top: chatContainerRef.current?.scrollHeight, behavior: 'smooth' });
            setMessages((msgs) => [...msgs.slice(0, -1),
            {
              ...values,
              ...msgs[msgs.length - 1],
              pending: false,
              text: msgs[msgs.length - 1].text + values.textResponse
            }]);
            if (values.close) {
              setGenerating(false);
            }
          }

        }, [], selectedIds, conversationId);
      }, 300);
    }
  };

  useEffect(() => {
    const fetchConversationHistory = async () => {
      try {
        const response = await fetch(`${HOST}/kl/conversation/${conversationId}/history`);
        const data = await response.json();
        setMessages(data.conversation.messages.map((msg: any) => {
          if (msg.role === 'assistant') {
            return {
              "sources": msg.references,
              "type": "textResponseChunk",
              "close": false,
              "error": false,
              "text": msg.content,
              "pending": false,
              "user": "AI"
            }
          } else {
            return {
              "text": msg.content,
              "user": "You"
            }
          }

        }));
      } catch (error) {
        console.error('Error fetching conversation history:', error);
      }
    };

    fetchConversationHistory();
  }, [conversationId]);

  useEffect(() => {
    return () => {
      generatorTimeout && clearTimeout(generatorTimeout);
    }
  }, [])

  useEffect(() => {
    if(messages.length){
      chatContainerRef.current?.scrollTo({ top: chatContainerRef.current?.scrollHeight, behavior: 'smooth' });
    }
  }, [messages.length])


  return (
    <>
      <div ref={chatContainerRef} className='h-full min-h-[85vh]' style={{ paddingRight: '14px', overflowY: 'scroll' }} >
        {messages.length ? messages.map((msg, index) => {
          return (
            <Message message={msg} key={index} isLast={index === messages.length - 1} />
          )
        }) : <div className='width-full h-full flex items-center justify-center'><Empty description="No messages yet" /></div>
        }
      </div>
      <div style={{ display: 'flex', marginTop: '20px' }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
          style={{ padding: '10px' }}
        />
        <button onClick={sendMessage} style={{ padding: '10px 20px' }} >
          {
            generating ? <PauseOutlined className='text-3xl' onClick={stopGeneration} /> : <SendOutlined className={input.trim() === '' ? 'text-3xl opacity-50 cursor-not-allowed' : 'text-3xl'} />
          }

        </button>
      </div>
    </>
  );
}