import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import aiService from '../services/aiService';
// Import FixedSizeList only if you need virtualization
// import { FixedSizeList as List } from 'react-window';

const ChatContainer = styled(motion.div)`
  width: 90%;
  max-width: 600px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 15px;
  box-shadow: 0 0 15px rgba(66, 220, 219, 0.5), 0 0 30px rgba(120, 0, 255, 0.3);
  overflow: hidden;
  border: 1px solid rgba(128, 0, 255, 0.4);
  
  @media (max-width: 768px) {
    width: 95%;
    border-radius: 12px;
  }
`;

const ChatHeader = styled.div`
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(30, 0, 60, 0.9) 100%);
  color: ${({ theme }) => theme.text};
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(128, 0, 255, 0.4);
`;

const HeaderTitle = styled.h2`
  font-size: 1.2rem;
  background: linear-gradient(90deg, #42dcdb, #a537fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 10px rgba(66, 220, 219, 0.5);
  font-weight: 700;
  margin: 0;
`;

const ChatBody = styled.div`
  height: 150px;
  overflow-y: auto;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.5);
  
  @media (max-width: 768px) {
    height: 120px;
    padding: 0.5rem;
  }
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #42dcdb, #a537fd);
    border-radius: 10px;
  }
`;

const MessageList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Message = styled(motion.div)`
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  background: ${({ isUser }) => 
    isUser 
      ? 'linear-gradient(135deg, rgba(66, 220, 219, 0.2) 0%, rgba(66, 220, 219, 0.1) 100%)' 
      : 'linear-gradient(135deg, rgba(165, 55, 253, 0.2) 0%, rgba(165, 55, 253, 0.1) 100%)'};
  color: ${({ theme }) => theme.text};
  max-width: 85%;
  align-self: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
  box-shadow: ${({ isUser }) => 
    isUser 
      ? '0 0 10px rgba(66, 220, 219, 0.2)' 
      : '0 0 10px rgba(165, 55, 253, 0.2)'};
  position: relative;
  word-break: break-word;
  border: 1px solid ${({ isUser }) => 
    isUser 
      ? 'rgba(66, 220, 219, 0.3)' 
      : 'rgba(165, 55, 253, 0.3)'};
  font-size: 0.9rem;
  
  @media (max-width: 768px) {
    max-width: 90%;
    padding: 0.5rem;
    font-size: 0.85rem;
  }
  
  &:focus {
    outline: 2px solid ${({ isUser }) => 
      isUser ? 'rgba(66, 220, 219, 0.5)' : 'rgba(165, 55, 253, 0.5)'};
    outline-offset: 2px;
  }
  
  &:hover {
    transform: translateY(-1px);
    transition: transform 0.2s ease;
    box-shadow: ${({ isUser }) => 
      isUser 
        ? '0 0 15px rgba(66, 220, 219, 0.3)' 
        : '0 0 15px rgba(165, 55, 253, 0.3)'};
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
  padding: 4px;

  span {
    width: 6px;
    height: 6px;
    background: linear-gradient(90deg, #42dcdb, #a537fd);
    border-radius: 50%;
  }
`;

const ErrorMessage = styled.div`
  color: #ff5c5c;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.8rem;
  text-shadow: 0 0 5px rgba(255, 92, 92, 0.5);
`;

const VoiceIndicator = styled(motion.div)`
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(90deg, #42dcdb, #a537fd);
  box-shadow: 0 0 10px rgba(66, 220, 219, 0.5);
`;

const AudioButton = styled(motion.button)`
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(66, 220, 219, 0.3), rgba(165, 55, 253, 0.3));
  border: 1px solid rgba(128, 0, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.8rem;
  padding: 0;
  
  &:hover {
    background: linear-gradient(135deg, rgba(66, 220, 219, 0.5), rgba(165, 55, 253, 0.5));
  }
  
  &:focus {
    outline: none;
  }
`;

const AudioStatusIndicator = styled(motion.span)`
  position: absolute;
  bottom: 0.5rem;
  right: 2.5rem;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.7);
`;

// Mock audio URL for testing - you'll replace this with your actual audio service
const DEMO_AUDIO_URL = 'https://actions.google.com/sounds/v1/alarms/beep_short.ogg';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [playingAudioId, setPlayingAudioId] = useState(null);
  const chatBodyRef = useRef(null);
  const audioRef = useRef(new Audio());

  // Add welcome message on initial load
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: Date.now(),
          text: "Hello! I'm AURA, your Augmented User Response Assistant. How can I assist you today?",
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

  // Handle audio playback cleanup
  useEffect(() => {
    const audio = audioRef.current;
    
    // Set up audio events
    const handleEnded = () => setPlayingAudioId(null);
    const handleError = (e) => {
      console.error('Audio playback error:', e);
      setPlayingAudioId(null);
      setError('Failed to play audio');
    };
    
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    
    return () => {
      audio.pause();
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, []);

  const playMessageAudio = async (message) => {
    try {
      // If already playing this message's audio, stop it
      if (playingAudioId === message.id) {
        audioRef.current.pause();
        setPlayingAudioId(null);
        return;
      }
      
      // Stop any currently playing audio
      audioRef.current.pause();
      
      let audioUrl;
      
      // If no audio URL exists for this message yet, generate one
      if (!message.audioUrl) {
        setPlayingAudioId('loading');
        
        // Convert text to audio through AI service
        const result = await aiService.textToSpeech(message.text);
        
        // Update the message with the audio URL
        audioUrl = result.audioUrl;
        setMessages(prevMessages => 
          prevMessages.map(msg => 
            msg.id === message.id ? { ...msg, audioUrl: audioUrl } : msg
          )
        );
      } else {
        audioUrl = message.audioUrl;
      }
      
      // Play the audio
      audioRef.current.src = audioUrl;
      
      const playPromise = audioRef.current.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            setPlayingAudioId(message.id);
          })
          .catch(error => {
            console.error('Audio play error:', error);
            setError('Browser blocked audio playback. Please interact with the page first.');
            setPlayingAudioId(null);
          });
      }
    } catch (error) {
      console.error('Error playing audio:', error);
      setError('Failed to play audio: ' + error.message);
      setPlayingAudioId(null);
    }
  };

  return (
    <ChatContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ChatHeader>
        <VoiceIndicator 
          animate={{ 
            boxShadow: ['0 0 10px rgba(66, 220, 219, 0.5)', '0 0 20px rgba(165, 55, 253, 0.5)', '0 0 10px rgba(66, 220, 219, 0.5)']
          }}
          transition={{ repeat: Infinity, duration: 2 }}
        />
        <HeaderTitle>AURA</HeaderTitle>
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
                aria-label={`${message.isUser ? 'Your message' : 'AURA\'s response'}: ${message.text}`}
              >
                {message.text}
                {!message.isUser && (
                  <>
                    <AudioButton 
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => playMessageAudio(message)}
                      aria-label={playingAudioId === message.id ? "Pause audio" : "Play message audio"}
                    >
                      {playingAudioId === message.id ? '⏸' : '🔊'}
                    </AudioButton>
                    
                    {playingAudioId === message.id && (
                      <AudioStatusIndicator 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        Playing...
                      </AudioStatusIndicator>
                    )}
                    
                    {playingAudioId === 'loading' && message.id === messages[messages.length - 1].id && (
                      <AudioStatusIndicator 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        Loading audio...
                      </AudioStatusIndicator>
                    )}
                  </>
                )}
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
