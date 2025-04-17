import React, { useState } from 'react';
import { motion } from 'framer-motion';
import styled, { ThemeProvider } from 'styled-components';
import Spline from '@splinetool/react-spline';
import { darkTheme } from './themes/darkTheme';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';

const AppContainer = styled.div`
  min-height: 100vh;
  background: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.text};
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
`;

const SplineContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
`;

const ContentLayer = styled.div`
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const HeaderContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 2;
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
  z-index: 2;
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

function App() {
  const [command, setCommand] = useState('');

  return (
    <ThemeProvider theme={darkTheme}>
      <AppContainer>
        <NeonGlow />
        <SplineContainer>
          <Spline scene="https://prod.spline.design/q2c5wAVesDdTQQ8A/scene.splinecode" />
        </SplineContainer>
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
                    // Handle command here
                    setCommand('');
                  }
                }}
              />
            </CommandBar>
          </BottomContainer>
        </ContentLayer>
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;