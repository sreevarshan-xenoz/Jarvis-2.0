import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const ModelInfoContainer = styled(motion.div)`
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(30, 30, 50, 0.8);
  border: 1px solid rgba(128, 10, 255, 0.4);
  border-radius: 10px;
  color: white;
  padding: 10px 15px;
  font-size: 12px;
  z-index: 10;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  max-width: 300px;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  background-color: ${({ available }) => 
    available ? 'rgba(46, 204, 113, 0.8)' : 'rgba(231, 76, 60, 0.8)'};
  box-shadow: 0 0 5px ${({ available }) => 
    available ? 'rgba(46, 204, 113, 0.6)' : 'rgba(231, 76, 60, 0.6)'};
`;

const ModelText = styled.div`
  display: flex;
  flex-direction: column;
`;

const ModelSource = styled.span`
  font-weight: bold;
  margin-bottom: 2px;
`;

const ModelMessage = styled.span`
  opacity: 0.8;
`;

const ModelInfo = ({ info }) => {
  if (!info) return null;
  
  const { available, source, message } = info;
  let sourceText = 'Unknown';
  
  switch (source) {
    case 'gradio':
      sourceText = 'Hugging Face Gradio';
      break;
    case 'backend':
      sourceText = 'AURA Backend';
      break;
    case 'error':
      sourceText = 'Error';
      break;
    case 'checking...':
      sourceText = 'Checking...';
      break;
    default:
      sourceText = source || 'Unknown';
  }
  
  return (
    <ModelInfoContainer
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <StatusDot available={available} />
      <ModelText>
        <ModelSource>{sourceText}</ModelSource>
        <ModelMessage>{message}</ModelMessage>
      </ModelText>
    </ModelInfoContainer>
  );
};

export default ModelInfo; 