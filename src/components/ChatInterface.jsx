import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaPaperPlane } from 'react-icons/fa';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid rgba(128, 0, 255, 0.4);
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(128, 0, 255, 0.4);
    border-radius: 3px;
  }
`;

const Message = styled(motion.div)`
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 70%;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.4;
  
  ${({ isUser }) => isUser ? `
    align-self: flex-end;
    background: linear-gradient(135deg, rgba(66, 220, 219, 0.3), rgba(165, 55, 253, 0.3));
    color: white;
    border: 1px solid rgba(128, 0, 255, 0.4);
  ` : `
    align-self: flex-start;
    background: rgba(20, 20, 30, 0.7);
    color: white;
    border: 1px solid rgba(66, 220, 219, 0.4);
  `}
`;

const InputForm = styled.form`
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.5);
  border-top: 1px solid rgba(128, 0, 255, 0.4);
`;

const Input = styled.input`
  flex: 1;
  padding: 12px;
  border: 1px solid rgba(128, 0, 255, 0.3);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: rgba(20, 20, 30, 0.7);
  color: white;
  transition: all 0.2s;
  
  &:focus {
    border-color: rgba(66, 220, 219, 0.6);
    box-shadow: 0 0 10px rgba(66, 220, 219, 0.2);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
  
  &:disabled {
    background: rgba(20, 20, 30, 0.5);
    cursor: not-allowed;
  }
`;

const SendButton = styled(motion.button)`
  padding: 12px;
  width: 44px;
  background: linear-gradient(135deg, rgba(66, 220, 219, 0.3), rgba(165, 55, 253, 0.3));
  color: white;
  border: 1px solid rgba(128, 0, 255, 0.4);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(66, 220, 219, 0.5), rgba(165, 55, 253, 0.5));
    box-shadow: 0 0 10px rgba(66, 220, 219, 0.2);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const ChatInterface = ({ onSendMessage, messages = [], isProcessing }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isProcessing) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.map((message, index) => (
          <Message
            key={message.id || index}
            isUser={message.role === 'user'}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {message.content}
          </Message>
        ))}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <InputForm onSubmit={handleSubmit}>
        <Input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isProcessing}
        />
        <SendButton 
          type="submit" 
          disabled={!input.trim() || isProcessing}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FaPaperPlane />
        </SendButton>
      </InputForm>
    </ChatContainer>
  );
};

export default ChatInterface;
