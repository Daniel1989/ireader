// components/ChatUI.js
import { useEffect, useRef, useState } from 'react';
import ChatContainer from './ChatContainer';
import WebPageList from './WebPageList';
import { HOST } from '../../constnat';

export default function ChatPage() {
  const [col1Width, setCol1Width] = useState(600); // Default width for first column

  // Track which divider is being dragged
  const [isDragging, setIsDragging] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [conversationId, setConversationId] = useState('');

  const onSelected = (ids: string[]) => {
    setSelectedIds(ids);
  }

  // Handle the mouse move event to adjust the column width
  const handleMouseMove = (e: any) => {
    setCol1Width(e.clientX);
  };

  // Handle mouse up to stop dragging
  const handleMouseUp = () => setIsDragging(false);

  // Handle mouse down to start dragging
  const startDragging = () => {
    setIsDragging(true);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, col1Width]);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const cid = urlParams.get('conversationid');

    if (!cid) {
      // Call API to create new conversation
      fetch(`${HOST}/kl/conversation/create`, {
        method: 'POST',
        // Add any required headers and body data
      })
        .then(response => response.json())
        .then(data => {
          // Update URL with new conversationId
          urlParams.set('conversationid', data.conversation_id);
          window.history.replaceState({}, '', `${window.location.pathname}?${urlParams}`);
          setConversationId(data.conversation_id)
        })
        .catch(error => {
          console.error('Error creating conversation:', error);
        });
    } else {
      setConversationId(cid)
    }
  }, []);

  return (
    <div className="flex">
      <div
        style={{ width: col1Width, minWidth: "300px" }}
        className={`overflow-scroll`}
      >
        <WebPageList width={col1Width} onSelected={onSelected} selectedIds={selectedIds}/>
      </div>
      <div
        className="w-1 h-[100vh] cursor-col-resize bg-gray-300"
        onMouseDown={() => startDragging()}
      />
      <div
        className={`${'w-[20px]'
          } h-32 overflow-hidden`}
      >
      </div>

      <div className="flex-grow  h-32 max-w-[120vh]">
        <ChatContainer selectedIds={selectedIds} conversationId={conversationId}/>
      </div>
    </div>
  );
}