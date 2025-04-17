import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
// Import FixedSizeList only if you need virtualization
// import { FixedSizeList as List } from 'react-window';

const ChatContainer = styled(motion.div)`
  width: 100%;
  max-width: 800px;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-radius: ${({ theme }) => theme.borderRadius.large};
  box-shadow: ${({ theme }) => theme.shadows.large};
  overflow: hidden;
  margin: 1rem;
  
  @media (max-width: 768px) {
    margin: 0.5rem;
    border-radius: ${({ theme }) => theme.borderRadius.medium};
  }
`;

const ChatHeader = styled.div`
  padding: 1.5rem;
  background: ${({ theme }) => theme.gradients.primary};
  color: ${({ theme }) => theme.text};
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const ChatBody = styled.div`
  height: 500px;
  overflow-y: auto;
  padding: 1.5rem;
  
  @media (max-width: 768px) {
    height: calc(100vh - 200px);
    padding: 1rem;
  }
`;

const MessageList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Message = styled(motion.div)`
  padding: 1rem;
  border-radius: ${({ theme }) => theme.borderRadius.medium};
  background: ${({ isUser, theme }) =>
    isUser ? theme.primary : theme.backgroundSecondary};
  color: ${({ theme }) => theme.text};
  max-width: 80%;
  align-self: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
  box-shadow: ${({ theme }) => theme.shadows.small};
  position: relative;
  word-break: break-word;
  
  @media (max-width: 768px) {
    max-width: 90%;
    padding: 0.75rem;
    font-size: 0.95rem;
  }
  
  &:focus {
    outline: 2px solid ${({ theme }) => theme.primary};
    outline-offset: 2px;
  }
  
  &:hover {
    transform: translateY(-1px);
    transition: transform 0.2s ease;
  }
`;

const Button = styled(motion.button)`
  padding: 1rem 2rem;
  border-radius: ${({ theme }) => theme.borderRadius.medium};
  border: none;
  background: ${({ theme }) => theme.gradients.primary};
  color: ${({ theme }) => theme.text};
  font-weight: 600;
  cursor: pointer;
  transition: all ${({ theme }) => theme.animations.fast};

  &:hover {
    opacity: 0.9;
  }

  &:active {
    transform: scale(0.98);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Input = styled.input`
  flex: 1;
  padding: 1rem;
  border-radius: ${({ theme }) => theme.borderRadius.medium};
  border: 1px solid ${({ theme }) => theme.border};
  background: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.text};
  font-size: 1rem;
  transition: all ${({ theme }) => theme.animations.fast};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.primary};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.primary}33;
  }
`;

const InputContainer = styled.div`
  padding: 1.5rem;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-top: 1px solid ${({ theme }) => theme.border};
  display: flex;
  gap: 1rem;
  
  @media (max-width: 768px) {
    padding: 1rem;
    flex-wrap: wrap;
    
    ${Input} {
      flex: 1 1 100%;
    }
    
    button {
      flex: 1;
    }
  }
`;

const LoadingDots = styled(motion.div)`
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 8px;

  span {
    width: 8px;
    height: 8px;
    background: ${({ theme }) => theme.text};
    border-radius: 50%;
  }
`;

const ErrorMessage = styled.div`
  color: ${({ theme }) => theme.error};
  padding: 0.5rem;
  text-align: center;
  font-size: 0.9rem;
`;

const VoiceIndicator = styled(motion.div)`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${({ theme }) => theme.success};
`;

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatBodyRef = useRef(null);

  // Add welcome message on initial load
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: Date.now(),
          text: "Hello! I'm the SRM College AI Assistant. How can I help you today?",
          isUser: false,
        }
      ]);
    }
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <ChatContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ChatHeader>
        <VoiceIndicator />
        <h2>SRM College AI Assistant</h2>
      </ChatHeader>

      <ChatBody ref={chatBodyRef}>
        <MessageList>
          <AnimatePresence>
            {messages.map((message) => (
              <Message
                key={message.id}
                isUser={message.isUser}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                tabIndex={0}
                role="article"
                aria-label={`${message.isUser ? 'Your message' : 'Assistant\'s response'}: ${message.text}`}
              >
                {message.text}
              </Message>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <LoadingDots
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              role="status"
              aria-label="Loading response"
            >
              <motion.span
                animate={{ y: [0, -8, 0] }}
                transition={{ repeat: Infinity, duration: 0.8, delay: 0 }}
              />
              <motion.span
                animate={{ y: [0, -8, 0] }}
                transition={{ repeat: Infinity, duration: 0.8, delay: 0.2 }}
              />
              <motion.span
                animate={{ y: [0, -8, 0] }}
                transition={{ repeat: Infinity, duration: 0.8, delay: 0.4 }}
              />
            </LoadingDots>
          )}
          
          {error && <ErrorMessage role="alert">{error}</ErrorMessage>}
        </MessageList>
      </ChatBody>
    </ChatContainer>
  );
};

export default ChatInterface;
