// components/ChatUI.js
import { useEffect, useRef, useState } from 'react';
import { ABORT_STREAM_EVENT, streamChat } from './streamChat';
import Message from './message';
import { PauseOutlined, SendOutlined } from '@ant-design/icons';
import { Empty, Input } from 'antd';
import { useSearchParams } from 'react-router-dom';
import { HOST } from '../../../constnat';
import { useTranslation } from 'react-i18next';

type TranslationKeys = 
    | 'chat.error.load'
    | 'chat.noMessages'
    | 'chat.placeholder'
    | 'chat.stop'
    | 'chat.send';

export default function ChatContainer(props: any) {
  const { t } = useTranslation();
  const { selectedIds, conversationId } = props;
  const [messages, setMessages] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [input, setInput] = useState('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Translation wrapper function with ts-ignore for type safety bypass
  const translate = (key: TranslationKeys, params?: Record<string, any>) => {
    // @ts-ignore: Suppress type checking for translation function
    return t(key, params);
  };

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
        if (data.success) {
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
        }
      } catch (error) {
        console.error(translate('chat.error.load'), error);
      }
    };

    if (conversationId) {
      fetchConversationHistory();
    }
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
        }) : <div className='width-full h-full flex items-center justify-center'>
          <Empty description={translate('chat.noMessages')} />
        </div>
        }
      </div>
      <div style={{ display: 'flex', marginTop: '20px' }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={translate('chat.placeholder')}
          style={{ padding: '10px' }}
        />
        <button 
          onClick={generating ? stopGeneration : sendMessage} 
          style={{ padding: '10px 20px' }}
          title={generating ? translate('chat.stop') : translate('chat.send')}
        >
          {
            generating ? 
              <PauseOutlined className='text-3xl' /> : 
              <SendOutlined className={input.trim() === '' ? 'text-3xl opacity-50 cursor-not-allowed' : 'text-3xl'} />
          }
        </button>
      </div>
    </>
  );
}