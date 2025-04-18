import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled, { ThemeProvider } from 'styled-components';
import Spline from '@splinetool/react-spline';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import DiagnosticPanel from './components/DiagnosticPanel';
import JarvisIntegration from './components/JarvisIntegration';
import aiService from './services/aiService';

const AppContainer = styled.div`
  min-height: 100vh;
  background: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.text};
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
`;

// First scene - now the waves scene as background (previously overlay)
const SplineBackgroundContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: auto;
`;

// Second scene - now the qX39 scene as overlay with opacity (previously background)
const SplineForegroundContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: auto;
  opacity: 0.5;
`;

const ContentLayer = styled.div`
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  pointer-events: none;
`;

const HeaderContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 4;
  pointer-events: auto;
`;

const BottomContainer = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 2rem;
  z-index: 4;
  pointer-events: none;
  
  & > * {
    pointer-events: auto;
  }
`;

const CommandBar = styled(motion.div)`
  width: 90%;
  max-width: 600px;
  height: 60px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1.5rem;
  box-shadow: 0 0 15px rgba(66, 220, 219, 0.5), 0 0 30px rgba(120, 0, 255, 0.3);
  border: 1px solid rgba(128, 0, 255, 0.4);
  margin-top: 1rem;
`;

const CommandInput = styled.input`
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  color: white;
  padding: 0 1rem;
  font-size: 1rem;
  
  &:focus {
    outline: none;
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const NeonGlow = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: 
    radial-gradient(circle at 20% 30%, rgba(66, 220, 219, 0.1) 0%, transparent 30%),
    radial-gradient(circle at 80% 70%, rgba(165, 55, 253, 0.1) 0%, transparent 30%);
  z-index: 0;
`;

const StatusIndicator = styled.div`
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: ${({ isOnline }) => 
    isOnline ? 'rgba(66, 220, 219, 1)' : 'rgba(255, 87, 87, 1)'};
  box-shadow: 0 0 10px ${({ isOnline }) => 
    isOnline ? 'rgba(66, 220, 219, 0.7)' : 'rgba(255, 87, 87, 0.7)'};
  z-index: 5;
`;

const StatusTooltip = styled.div`
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  padding: 0.5rem 0.75rem;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
  font-size: 0.8rem;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 5;

  ${StatusIndicator}:hover + & {
    opacity: 1;
    transform: translateY(0);
  }
`;

const NotificationContainer = styled(motion.div)`
  position: absolute;
  bottom: 7rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.9rem;
  max-width: 80%;
  text-align: center;
  border: 1px solid rgba(128, 0, 255, 0.4);
  box-shadow: 0 0 15px rgba(66, 220, 219, 0.3);
  z-index: 5;
`;

const DiagnosticButton = styled(motion.button)`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: linear-gradient(135deg, rgba(66, 220, 219, 0.2), rgba(165, 55, 253, 0.2));
  border: 1px solid rgba(66, 220, 219, 0.3);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 5px;
  font-size: 0.8rem;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: linear-gradient(135deg, rgba(66, 220, 219, 0.3), rgba(165, 55, 253, 0.3));
  }
`;

const DiagnosticIcon = styled.span`
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: ${({ isOnline }) => 
    isOnline ? 'rgba(66, 220, 219, 0.8)' : 'rgba(255, 87, 87, 0.8)'};
  box-shadow: 0 0 5px ${({ isOnline }) => 
    isOnline ? 'rgba(66, 220, 219, 0.6)' : 'rgba(255, 87, 87, 0.6)'};
`;

const WatermarkCover = styled.div`
  position: fixed;
  bottom: 0;
  right: 0;
  width: 200px;
  height: 60px;
  background: #000;
  z-index: 9999;
  pointer-events: none;
`;

// Keep the dark theme for consistency
const darkTheme = {
  background: '#121212',
  text: '#e0e0e0',
  primary: '#42dcdb',
  secondary: '#a18fff',
  accent: '#ff8a80',
  panel: 'rgba(30, 30, 40, 0.7)',
  card: 'rgba(25, 25, 35, 0.8)',
  shadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
  success: '#66BB6A',
  error: '#EF5350',
  warning: '#FFA726',
  info: '#42A5F5'
};

const App = () => {
  const [messages, setMessages] = useState(() => {
    // Load messages from localStorage if available
    const savedMessages = localStorage.getItem('aura_messages');
    return savedMessages ? JSON.parse(savedMessages) : [{
      id: 1,
      role: 'assistant',
      content: "Hello! I'm AURA, your Augmented User Response Assistant. How can I assist you today?"
    }];
  });
  const [command, setCommand] = useState('');
  const [modelStatus, setModelStatus] = useState({ online: false, status: 'Checking status...' });
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const [notification, setNotification] = useState(null);
  const [useJarvis, setUseJarvis] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const backgroundSplineRef = useRef();
  const foregroundSplineRef = useRef();
  const audioRef = useRef(new Audio());
  const [playingAudioId, setPlayingAudioId] = useState(null);

  useEffect(() => {
    // Check model status on initial load
    checkModelStatus();
    
    // Set up interval to check status periodically
    const statusInterval = setInterval(checkModelStatus, 60000); // Check every minute
    
    return () => clearInterval(statusInterval);
  }, []);

  useEffect(() => {
    // Save messages to localStorage whenever they change
    localStorage.setItem('aura_messages', JSON.stringify(messages));
  }, [messages]);

  // Handle audio playback cleanup
  useEffect(() => {
    const audio = audioRef.current;
    
    // Set up audio events
    const handleEnded = () => setPlayingAudioId(null);
    const handleError = (e) => {
      console.error('Audio playback error:', e);
      setPlayingAudioId(null);
    };
    
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    
    return () => {
      audio.pause();
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, []);

  const checkModelStatus = async () => {
    try {
      const status = await aiService.getModelStatus();
      setModelStatus({
        online: status.online,
        status: status.online ? 'Gemma 2B model is online' : 'Gemma 2B model is offline'
      });
    } catch (error) {
      setModelStatus({
        online: false,
        status: 'Unable to connect to AI service'
      });
    }
  };

  const onLoadBackground = (splineApp) => {
    backgroundSplineRef.current = splineApp;
    console.log('Background Spline scene loaded');
  };

  const onLoadForeground = (splineApp) => {
    foregroundSplineRef.current = splineApp;
    console.log('Foreground Spline scene loaded');
  };

  const handleUnifiedInput = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;

    const userInput = command.trim();
    setCommand('');
    setIsLoading(true);

    // Add user message to chat history
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: userInput
    };
    setMessages(prevMessages => [...prevMessages, userMessage]);

    try {
      // Check if input starts with a command prefix like "/"
      if (userInput.startsWith('/')) {
        // Handle as command
        const cmdText = userInput.substring(1); // Remove the slash
        showNotification('Executing command...');
        
        const result = await aiService.executeCommand(cmdText, useJarvis);
        
        // Add command result to chat
        const responseMessage = {
          id: Date.now(),
          role: 'assistant',
          content: result.message || 'Command executed'
        };
        setMessages(prevMessages => [...prevMessages, responseMessage]);
        
        if (result.success) {
          showNotification(result.message || 'Command executed successfully');
        } else {
          showNotification(result.message || 'Command execution failed');
        }

        // Auto-play response if voice mode is on
        if (voiceMode) {
          playMessageAudio(responseMessage);
        }
      } else {
        // Handle as conversation
        const response = await aiService.sendMessage(userInput);
        
        // Add AI response to chat
        const responseMessage = {
          id: Date.now(),
          role: 'assistant',
          content: response.response || "I couldn't generate a response at this time."
        };
        setMessages(prevMessages => [...prevMessages, responseMessage]);
        
        // Auto-play response if voice mode is on
        if (voiceMode) {
          playMessageAudio(responseMessage);
        }
      }
    } catch (error) {
      console.error('Error processing input:', error);
      showNotification(`Error: ${error.message || 'Failed to process input'}`);
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `Error: ${error.message || 'Something went wrong'}`
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

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
        const result = await aiService.textToSpeech(message.content);
        
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
            showNotification('Browser blocked audio playback. Please interact with the page first.');
            setPlayingAudioId(null);
          });
      }
    } catch (error) {
      console.error('Error playing audio:', error);
      showNotification('Failed to play audio: ' + error.message);
      setPlayingAudioId(null);
    }
  };

  const showNotification = (message) => {
    setNotification(message);
    // Clear notification after 5 seconds
    setTimeout(() => setNotification(null), 5000);
  };

  // Keep clearChatHistory function
  const clearChatHistory = () => {
    const initialMessage = {
      id: Date.now(),
      role: 'assistant',
      content: "Chat history cleared. How can I assist you today?"
    };
    setMessages([initialMessage]);
    showNotification("Chat history cleared");
  };

  // Handle Jarvis toggle
  const handleUseJarvisChange = (value) => {
    setUseJarvis(value);
    showNotification(value ? 'Switched to Jarvis' : 'Switched to AURA AI');
  };

  // Toggle voice mode
  const toggleVoiceMode = () => {
    const newMode = !voiceMode;
    setVoiceMode(newMode);
    
    // Stop any playing audio when turning off voice mode
    if (!newMode && playingAudioId) {
      audioRef.current.pause();
      setPlayingAudioId(null);
    }
    
    showNotification(newMode ? 'Voice mode enabled' : 'Voice mode disabled');
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <AppContainer>
        <NeonGlow />
        <WatermarkCover />
        <WatermarkCover style={{ bottom: '10px', right: '10px' }} />
        <WatermarkCover style={{ bottom: '10px', right: '0' }} />
        <WatermarkCover style={{ bottom: '0', right: '10px' }} />
        
        <JarvisIntegration onUseJarvisChange={handleUseJarvisChange} />
        
        <motion.button
          style={{
            position: 'absolute',
            top: '20px',
            right: '200px',
            background: 'rgba(30, 30, 50, 0.7)',
            border: '1px solid rgba(255, 87, 87, 0.4)',
            borderRadius: '20px',
            color: 'rgba(255, 87, 87, 0.8)',
            fontSize: '12px',
            padding: '6px 12px',
            cursor: 'pointer',
            zIndex: 10,
            backdropFilter: 'blur(4px)'
          }}
          onClick={clearChatHistory}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Clear History
        </motion.button>
        
        <motion.button
          style={{
            position: 'absolute',
            top: '20px',
            right: '120px',
            background: 'rgba(30, 30, 50, 0.7)',
            border: `1px solid ${voiceMode ? 'rgba(66, 220, 219, 0.6)' : 'rgba(255, 255, 255, 0.4)'}`,
            borderRadius: '20px',
            color: voiceMode ? 'rgba(66, 220, 219, 0.9)' : 'rgba(255, 255, 255, 0.8)',
            fontSize: '12px',
            padding: '6px 12px',
            cursor: 'pointer',
            zIndex: 10,
            backdropFilter: 'blur(4px)'
          }}
          onClick={toggleVoiceMode}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Voice {voiceMode ? 'On' : 'Off'}
        </motion.button>
        
        <DiagnosticButton
          onClick={() => setShowDiagnostic(true)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <DiagnosticIcon isOnline={modelStatus.online} />
          Run Diagnostic
        </DiagnosticButton>
        
        {/* The newer 3D scene forms the solid background */}
        <SplineBackgroundContainer>
          <Spline 
            scene="https://prod.spline.design/qX39OiHwKkpiLOPh/scene.splinecode" 
            onLoad={onLoadBackground}
            style={{ width: '100%', height: '100%' }}
            hideAttribution={true}
          />
        </SplineBackgroundContainer>
        
        {/* The wave design overlays with partial transparency */}
        <SplineForegroundContainer>
          <Spline 
            scene="https://prod.spline.design/q2c5wAVesDdTQQ8A/scene.splinecode" 
            onLoad={onLoadForeground}
            style={{ width: '100%', height: '100%' }}
            hideAttribution={true}
          />
        </SplineForegroundContainer>
        
        <AnimatePresence>
          {showDiagnostic && (
            <DiagnosticPanel onClose={() => setShowDiagnostic(false)} />
          )}
        </AnimatePresence>
        
        <ContentLayer>
          <HeaderContainer>
            <Header />
          </HeaderContainer>
          
          <BottomContainer>
            {/* Chat Display Section */}
            <ChatDisplayContainer>
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
                <div>
                  {playingAudioId && playingAudioId !== 'loading' && (
                    <span style={{ fontSize: '0.8rem', color: 'rgba(66, 220, 219, 0.9)' }}>
                      Playing audio...
                    </span>
                  )}
                </div>
              </ChatHeader>
              
              <ChatBody>
                <AnimatePresence>
                  {messages.map((message) => (
                    <ChatMessage 
                      key={message.id}
                      isUser={message.role === 'user'}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      {message.content}
                      {message.role === 'assistant' && (
                        <AudioButton 
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => playMessageAudio(message)}
                        >
                          {playingAudioId === message.id ? '⏸' : '🔊'}
                        </AudioButton>
                      )}
                    </ChatMessage>
                  ))}
                </AnimatePresence>
                
                {isLoading && (
                  <LoadingContainer>
                    <LoadingDots>
                      <motion.span animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }} />
                      <motion.span animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} />
                      <motion.span animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} />
                    </LoadingDots>
                  </LoadingContainer>
                )}
              </ChatBody>
            </ChatDisplayContainer>
            
            <CommandBar
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              as="form"
              onSubmit={handleUnifiedInput}
            >
              <CommandInput 
                placeholder="Enter message or /command..."
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                disabled={isLoading}
              />
              <SendButton 
                type="submit"
                disabled={isLoading || !command.trim()}
                whileHover={{ scale: isLoading ? 1 : 1.05 }}
                whileTap={{ scale: isLoading ? 1 : 0.95 }}
              >
                {isLoading ? (
                  <LoadingIcon />
                ) : (
                  <SendIcon />
                )}
              </SendButton>
            </CommandBar>

            {notification && (
              <NotificationContainer
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {notification}
              </NotificationContainer>
            )}
          </BottomContainer>

          <StatusIndicator isOnline={modelStatus.online} />
          <StatusTooltip>{modelStatus.status}</StatusTooltip>
        </ContentLayer>
      </AppContainer>
    </ThemeProvider>
  );
};

// Add these styled components
const ChatDisplayContainer = styled.div`
  width: 90%;
  max-width: 600px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 15px;
  box-shadow: 0 0 15px rgba(66, 220, 219, 0.5), 0 0 30px rgba(120, 0, 255, 0.3);
  overflow: hidden;
  border: 1px solid rgba(128, 0, 255, 0.4);
  margin-bottom: 20px;
`;

const ChatHeader = styled.div`
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(30, 0, 60, 0.9) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
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

const VoiceIndicator = styled(motion.div)`
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(90deg, #42dcdb, #a537fd);
  box-shadow: 0 0 10px rgba(66, 220, 219, 0.5);
`;

const ChatBody = styled.div`
  height: 250px;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  
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

const ChatMessage = styled(motion.div)`
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: ${({ isUser }) => 
    isUser 
      ? 'linear-gradient(135deg, rgba(66, 220, 219, 0.2) 0%, rgba(66, 220, 219, 0.1) 100%)' 
      : 'linear-gradient(135deg, rgba(165, 55, 253, 0.2) 0%, rgba(165, 55, 253, 0.1) 100%)'};
  color: white;
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
  
  &:hover {
    transform: translateY(-1px);
    transition: transform 0.2s ease;
  }
`;

const AudioButton = styled(motion.button)`
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(66, 220, 219, 0.3), rgba(165, 55, 253, 0.3));
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.7rem;
  padding: 0;
  
  &:hover {
    background: linear-gradient(135deg, rgba(66, 220, 219, 0.5), rgba(165, 55, 253, 0.5));
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  padding: 0.5rem;
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  
  span {
    width: 8px;
    height: 8px;
    background: linear-gradient(90deg, #42dcdb, #a537fd);
    border-radius: 50%;
  }
`;

const SendButton = styled(motion.button)`
  background: linear-gradient(135deg, rgba(66, 220, 219, 0.7), rgba(165, 55, 253, 0.7));
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 10px;
  color: white;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingIcon = () => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
    style={{ width: '16px', height: '16px', borderRadius: '50%', 
            border: '2px solid rgba(255,255,255,0.2)', 
            borderTopColor: 'white' }}
  />
);

const SendIcon = () => <span>➤</span>;

export default App;