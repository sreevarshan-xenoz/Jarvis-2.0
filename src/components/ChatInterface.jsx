import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

const ChatContainer = styled(motion.div)`
  width: 100%;
  max-width: 800px;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-radius: ${({ theme }) => theme.borderRadius.large};
  box-shadow: ${({ theme }) => theme.shadows.large};
  overflow: hidden;
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
`;

const InputContainer = styled.div`
  padding: 1.5rem;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-top: 1px solid ${({ theme }) => theme.border};
  display: flex;
  gap: 1rem;
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
`;

const VoiceIndicator = styled(motion.div)`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${({ isActive, theme }) =>
    isActive ? theme.success : theme.textSecondary};
`;

const ChatInterface = ({ mode }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const chatBodyRef = useRef(null);

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessage = {
      id: Date.now(),
      text: input,
      isUser: true,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now(),
        text: 'This is a simulated AI response. Integration with the actual backend will be implemented soon.',
        isUser: false,
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  const handleVoiceToggle = () => {
    setIsListening(!isListening);
    // Voice recognition logic will be implemented here
  };

  return (
    <ChatContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ChatHeader>
        <VoiceIndicator
          isActive={isListening}
          animate={{ scale: isListening ? [1, 1.2, 1] : 1 }}
          transition={{ repeat: isListening ? Infinity : 0, duration: 1 }}
        />
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
              >
                {message.text}
              </Message>
            ))}
          </AnimatePresence>
        </MessageList>
      </ChatBody>

      <InputContainer>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          disabled={mode === 'voice'}
        />
        {mode !== 'text' && (
          <Button
            onClick={handleVoiceToggle}
            whileTap={{ scale: 0.95 }}
          >
            {isListening ? 'Stop' : 'Start'} Voice
          </Button>
        )}
        {mode !== 'voice' && (
          <Button
            onClick={handleSend}
            whileTap={{ scale: 0.95 }}
            disabled={!input.trim()}
          >
            Send
          </Button>
        )}
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface;