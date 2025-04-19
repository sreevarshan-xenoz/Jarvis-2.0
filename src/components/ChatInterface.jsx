import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import aiService from '../services/aiService';
import voiceService from '../services/voiceService';
import { FaMicrophone, FaMicrophoneSlash, FaVolumeUp, FaVolumeMute } from 'react-icons/fa';
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
  justify-content: space-between;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(128, 0, 255, 0.4);
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
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

const VoiceModeToggle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.8rem;
  color: ${({ active }) => 
    active ? 'rgba(66, 220, 219, 0.9)' : 'rgba(255, 255, 255, 0.6)'};
`;

const VoiceModeIcon = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${({ active }) => 
    active ? 'rgba(66, 220, 219, 0.2)' : 'rgba(255, 255, 255, 0.1)'};
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid ${({ active }) => 
    active ? 'rgba(66, 220, 219, 0.6)' : 'rgba(255, 255, 255, 0.3)'};
  transition: all 0.3s ease;
  
  &:hover {
    background: ${({ active }) => 
      active ? 'rgba(66, 220, 219, 0.3)' : 'rgba(255, 255, 255, 0.2)'};
  }
`;

// Mock audio URL for testing - you'll replace this with your actual audio service
const DEMO_AUDIO_URL = 'https://actions.google.com/sounds/v1/alarms/beep_short.ogg';

const InputForm = styled.form`
  display: flex;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.5);
  border-top: 1px solid rgba(128, 0, 255, 0.4);
`;

const MessageInput = styled.input`
  flex: 1;
  background: rgba(20, 20, 30, 0.7);
  border: 1px solid rgba(128, 0, 255, 0.3);
  border-radius: 20px;
  color: white;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  
  &:focus {
    outline: none;
    border-color: rgba(66, 220, 219, 0.6);
    box-shadow: 0 0 10px rgba(66, 220, 219, 0.2);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
`;

const SendButton = styled(motion.button)`
  background: linear-gradient(135deg, rgba(66, 220, 219, 0.5), rgba(165, 55, 253, 0.5));
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.5rem;
  cursor: pointer;
  color: white;
  font-size: 1rem;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 10px rgba(66, 220, 219, 0.4);
  }
`;

const VoiceControls = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  margin-bottom: 10px;
`;

const VoiceSettings = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const VoiceSelect = styled.select`
  background: rgba(20, 20, 30, 0.7);
  border: 1px solid rgba(128, 0, 255, 0.3);
  border-radius: 10px;
  color: white;
  padding: 5px;
  font-size: 0.8rem;

  &:focus {
    outline: none;
    border-color: rgba(66, 220, 219, 0.6);
  }
`;

const RangeInput = styled.input`
  width: 100px;
  accent-color: #42dcdb;
`;

const VoiceButton = styled.button`
  background: ${props => props.active ? '#4CAF50' : '#2196F3'};
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    opacity: 0.8;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [playingAudioId, setPlayingAudioId] = useState(null);
  const [voiceMode, setVoiceMode] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const chatBodyRef = useRef(null);
  const audioRef = useRef(new Audio());
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef(null);
  const [voiceSettings, setVoiceSettings] = useState({
    voice: '',
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0
  });
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isRealTimeVoice, setIsRealTimeVoice] = useState(false);

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

    // Auto-play the latest assistant message if voice mode is enabled
    if (voiceMode && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (!lastMessage.isUser && lastMessage.id !== playingAudioId) {
        playMessageAudio(lastMessage);
      }
    }
  }, [messages, voiceMode]);

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

  // Add cleanup on unmount
  useEffect(() => {
    return () => {
      voiceService.cleanup();
    };
  }, []);

  // Handle voice initialization errors
  const initializeVoice = async () => {
    try {
      const hasPermission = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (hasPermission) {
        return true;
      }
    } catch (error) {
      console.error('Microphone permission error:', error);
      setError('Please grant microphone permission to use voice features');
      return false;
    }
  };

  const toggleRealTimeVoice = async () => {
    if (isRealTimeVoice) {
      voiceService.stopRealtimeRecognition();
      setIsRealTimeVoice(false);
    } else {
      const initialized = await initializeVoice();
      if (!initialized) return;

      try {
        setIsRealTimeVoice(true);
        await voiceService.startRealtimeRecognition(
          // Transcript callback
          (text) => {
            if (text.trim()) {
              setInputMessage(text);
              handleSendMessage({ preventDefault: () => {} });
            }
          },
          // Error callback
          (error) => {
            console.error('Voice recognition error:', error);
            setIsRealTimeVoice(false);
            setError(typeof error === 'string' ? error : 'Voice recognition failed');
          }
        );
      } catch (error) {
        console.error('Failed to start real-time voice:', error);
        setIsRealTimeVoice(false);
        setError('Failed to start voice recognition. Please try again.');
      }
    }
  };

  const playMessageAudio = async (message) => {
    try {
      if (playingAudioId === message.id) {
        voiceService.stopSpeaking();
        setPlayingAudioId(null);
        return;
      }

      setPlayingAudioId(message.id);
      await voiceService.speak(message.text, voiceSettings);
      setPlayingAudioId(null);
    } catch (error) {
      console.error('Error playing audio:', error);
      setError(error.message || 'Failed to play audio');
      setPlayingAudioId(null);
    }
  };

  // Enhanced voice settings handling
  const handleVoiceSettingChange = (setting, value) => {
    try {
      // Validate value ranges
      switch (setting) {
        case 'rate':
        case 'pitch':
          value = Math.max(0.1, Math.min(value, 2.0));
          break;
        case 'volume':
          value = Math.max(0, Math.min(value, 1.0));
          break;
      }

      setVoiceSettings(prev => ({
        ...prev,
        [setting]: value
      }));
    } catch (error) {
      console.error('Error updating voice settings:', error);
      setError('Failed to update voice settings');
    }
  };

  // Load voices with retry
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 3;

    const loadVoices = () => {
      try {
        const voices = voiceService.getVoices();
        if (voices.length > 0) {
          setAvailableVoices(voices);
          setVoiceSettings(prev => ({
            ...prev,
            voice: voices[0].name
          }));
          return true;
        }
        return false;
      } catch (error) {
        console.error('Error loading voices:', error);
        return false;
      }
    };

    const tryLoadVoices = () => {
      if (!loadVoices() && retryCount < maxRetries) {
        retryCount++;
        setTimeout(tryLoadVoices, 1000);
      }
    };

    if (typeof speechSynthesis !== 'undefined') {
      speechSynthesis.onvoiceschanged = tryLoadVoices;
      tryLoadVoices();
    }
  }, []);

  const toggleVoiceMode = () => {
    const newMode = !voiceMode;
    setVoiceMode(newMode);
    
    // Stop any playing audio when turning off voice mode
    if (!newMode && playingAudioId) {
      audioRef.current.pause();
      setPlayingAudioId(null);
    }
    
    // Start playing latest assistant message when turning on voice mode
    if (newMode && messages.length > 0) {
      const lastAssistantMessage = [...messages].reverse().find(msg => !msg.isUser);
      if (lastAssistantMessage) {
        playMessageAudio(lastAssistantMessage);
      }
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      text: inputMessage.trim(),
      isUser: true
    };
    
    // Clear input field
    setInputMessage('');
    
    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    
    // Show loading state
    setIsLoading(true);
    setError(null);
    
    try {
      // Send message to AI service
      const response = await aiService.sendMessage(userMessage.text);
      
      // Add AI response to chat
      const aiMessage = {
        id: Date.now(),
        text: response.response || "I couldn't generate a response at this time.",
        isUser: false
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setError(`Failed to get response: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const message = inputMessage.trim();
    setInputMessage('');
    await handleSendMessage(e);
  };

  return (
    <ChatContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ChatHeader>
        <HeaderLeft>
          <VoiceIndicator 
            animate={{ 
              boxShadow: ['0 0 10px rgba(66, 220, 219, 0.5)', '0 0 20px rgba(165, 55, 253, 0.5)', '0 0 10px rgba(66, 220, 219, 0.5)']
            }}
            transition={{ repeat: Infinity, duration: 2 }}
          />
          <HeaderTitle>AURA</HeaderTitle>
        </HeaderLeft>

        <VoiceModeToggle
          active={voiceMode}
          onClick={toggleVoiceMode}
          role="button"
          aria-pressed={voiceMode}
          aria-label="Toggle voice mode"
        >
          <VoiceModeIcon active={voiceMode}>
            {voiceMode ? '🔊' : '🔇'}
          </VoiceModeIcon>
          <span>Voice {voiceMode ? 'On' : 'Off'}</span>
        </VoiceModeToggle>
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

      <VoiceControls>
        <VoiceButton
          onClick={toggleRealTimeVoice}
          active={isRealTimeVoice}
          title={isRealTimeVoice ? 'Stop real-time voice' : 'Start real-time voice'}
          disabled={!!error && error.includes('microphone permission')}
        >
          {isRealTimeVoice ? <FaMicrophoneSlash /> : <FaMicrophone />}
        </VoiceButton>
        
        <VoiceButton
          onClick={() => setIsSpeaking(!isSpeaking)}
          active={isSpeaking}
          title={isSpeaking ? 'Disable speech' : 'Enable speech'}
          disabled={availableVoices.length === 0}
        >
          {isSpeaking ? <FaVolumeMute /> : <FaVolumeUp />}
        </VoiceButton>

        <VoiceSettings>
          <VoiceSelect
            value={voiceSettings.voice}
            onChange={(e) => handleVoiceSettingChange('voice', e.target.value)}
            disabled={availableVoices.length === 0}
          >
            {availableVoices.map(voice => (
              <option key={voice.name} value={voice.name}>
                {voice.name} ({voice.lang})
              </option>
            ))}
          </VoiceSelect>

          <label>
            Rate:
            <RangeInput
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={voiceSettings.rate}
              onChange={(e) => handleVoiceSettingChange('rate', parseFloat(e.target.value))}
              disabled={!isSpeaking}
            />
          </label>

          <label>
            Pitch:
            <RangeInput
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={voiceSettings.pitch}
              onChange={(e) => handleVoiceSettingChange('pitch', parseFloat(e.target.value))}
              disabled={!isSpeaking}
            />
          </label>
        </VoiceSettings>
      </VoiceControls>

      <InputForm onSubmit={handleSubmit}>
        <MessageInput
          type="text"
          value={inputMessage}
          onChange={handleInputChange}
          placeholder="Type a message..."
          disabled={isLoading || isRealTimeVoice}
        />
        <SendButton
          type="submit"
          disabled={isLoading || !inputMessage.trim() || isRealTimeVoice}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label="Send message"
        >
          →
        </SendButton>
      </InputForm>
    </ChatContainer>
  );
};

export default ChatInterface;
