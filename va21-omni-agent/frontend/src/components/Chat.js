import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import '../App.css'; // We can reuse the main App.css for now

const socket = io();

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    socket.on('response', (data) => {
      setMessages((prevMessages) => {
        const lastMessage = prevMessages[prevMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'agent') {
          const updatedMessages = [...prevMessages];
          updatedMessages[prevMessages.length - 1] = {
            ...lastMessage,
            text: lastMessage.text + data.data,
          };
          return updatedMessages;
        } else {
          return [...prevMessages, { text: data.data, sender: 'agent' }];
        }
      });
    });

    return () => {
      socket.off('response');
    };
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setMessages([...messages, { text: inputValue, sender: 'user' }]);
      socket.emit('message', inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="chat-window">
        <div className="message-list">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender}`}>
              {message.text}
            </div>
          ))}
        </div>
        <form className="message-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message here..."
          />
          <button type="submit">Send</button>
        </form>
      </div>
  );
}

export default Chat;
