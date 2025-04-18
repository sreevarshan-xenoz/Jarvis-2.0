import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled, { ThemeProvider } from 'styled-components';
import Spline from '@splinetool/react-spline';
import { darkTheme } from './themes/darkTheme';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import DiagnosticPanel from './components/DiagnosticPanel';
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

function App() {
  const [command, setCommand] = useState('');
  const [modelStatus, setModelStatus] = useState({ online: false, status: 'Checking model status...' });
  const [notification, setNotification] = useState(null);
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const backgroundSplineRef = useRef();
  const foregroundSplineRef = useRef();

  useEffect(() => {
    // Check model status on initial load
    checkModelStatus();
    
    // Set up interval to check status periodically
    const statusInterval = setInterval(checkModelStatus, 60000); // Check every minute
    
    return () => clearInterval(statusInterval);
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

  const handleCommandSubmit = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;

    const userCommand = command.trim();
    setCommand('');

    try {
      showNotification('Executing command...');
      
      const result = await aiService.executeCommand(userCommand);
      
      if (result.success) {
        showNotification(result.message || 'Command executed successfully');
      } else {
        showNotification(result.message || 'Command execution failed');
      }
    } catch (error) {
      showNotification(`Error: ${error.message || 'Failed to execute command'}`);
    }
  };

  const showNotification = (message) => {
    setNotification(message);
    // Clear notification after 5 seconds
    setTimeout(() => setNotification(null), 5000);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <AppContainer>
        <NeonGlow />
        <WatermarkCover />
        <WatermarkCover style={{ bottom: '10px', right: '10px' }} />
        <WatermarkCover style={{ bottom: '10px', right: '0' }} />
        <WatermarkCover style={{ bottom: '0', right: '10px' }} />
        
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
        
        <DiagnosticButton
          onClick={() => setShowDiagnostic(true)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <DiagnosticIcon isOnline={modelStatus.online} />
          Run Diagnostic
        </DiagnosticButton>
        
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
            <ChatInterface />
            
            <CommandBar
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <CommandInput 
                placeholder="Enter command..."
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCommandSubmit(e);
                  }
                }}
              />
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
}

export default App;