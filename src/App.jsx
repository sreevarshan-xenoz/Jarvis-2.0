import React from 'react';
import { motion } from 'framer-motion';
import styled, { ThemeProvider } from 'styled-components';
import Spline from '@splinetool/react-spline';
import { darkTheme } from './themes/darkTheme';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import Footer from './components/Footer';

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

const MainContent = styled(motion.main)`
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  backdrop-filter: blur(5px);
  background: rgba(0, 0, 0, 0.4);
  border-radius: 16px;
  margin: 1rem;
`;

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <AppContainer>
        <SplineContainer>
          <Spline scene="https://prod.spline.design/q2c5wAVesDdTQQ8A/scene.splinecode" />
        </SplineContainer>
        <ContentLayer>
          <Header />
          <MainContent
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ChatInterface />
          </MainContent>
          <Footer />
        </ContentLayer>
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;