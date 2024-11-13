// components/ChatUI.js
import { useEffect, useRef, useState } from 'react';
import ChatContainer from './ChatContainer';
import WebPageList from './WebPageList';

export default function ChatPage() {
  const [col1Width, setCol1Width] = useState(600); // Default width for first column

  // Track which divider is being dragged
  const [isDragging, setIsDragging] = useState(false);

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

  return (
    <div className="flex">
      <div
        style={{ width: col1Width, minWidth: "300px" }}
        className={`overflow-scroll`}
      >
        <WebPageList width={col1Width}/>
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
        <ChatContainer />
      </div>
    </div>
  );
}