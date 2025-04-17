import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import aiService from '../services/aiService';

const PanelContainer = styled(motion.div)`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 600px;
  background: rgba(0, 0, 0, 0.85);
  border-radius: 10px;
  padding: 1.5rem;
  z-index: 100;
  box-shadow: 0 0 30px rgba(66, 220, 219, 0.5), 0 0 60px rgba(120, 0, 255, 0.3);
  border: 1px solid rgba(128, 0, 255, 0.6);
  color: white;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 80vh;
  overflow-y: auto;
  
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

const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(128, 0, 255, 0.4);
  padding-bottom: 0.75rem;
`;

const Title = styled.h2`
  font-size: 1.25rem;
  background: linear-gradient(90deg, #42dcdb, #a537fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  
  &:hover {
    color: white;
  }
`;

const RunButton = styled(motion.button)`
  background: linear-gradient(90deg, #42dcdb, #a537fd);
  border: none;
  border-radius: 5px;
  padding: 0.5rem 1rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ResultSection = styled.div`
  margin-top: 1rem;
`;

const TestResult = styled.div`
  margin-bottom: 0.75rem;
  padding: 0.75rem;
  border-radius: 5px;
  background: rgba(0, 0, 0, 0.3);
  border-left: 3px solid ${({ success }) => 
    success ? 'rgba(66, 220, 219, 0.8)' : 'rgba(255, 87, 87, 0.8)'};
`;

const TestTitle = styled.div`
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  margin-bottom: 0.5rem;
`;

const StatusBadge = styled.span`
  background: ${({ success }) => 
    success ? 'rgba(66, 220, 219, 0.2)' : 'rgba(255, 87, 87, 0.2)'};
  color: ${({ success }) => 
    success ? 'rgba(66, 220, 219, 1)' : 'rgba(255, 87, 87, 1)'};
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
`;

const TestMessage = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
`;

const DetailToggle = styled.button`
  background: transparent;
  border: none;
  color: rgba(128, 0, 255, 0.8);
  cursor: pointer;
  padding: 0;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  text-decoration: underline;
  
  &:hover {
    color: rgba(165, 55, 253, 1);
  }
`;

const DetailBox = styled(motion.pre)`
  background: rgba(0, 0, 0, 0.4);
  border-radius: 4px;
  padding: 0.5rem;
  font-size: 0.8rem;
  overflow-x: auto;
  margin-top: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  max-height: 200px;
  white-space: pre-wrap;
`;

const LoadingSpinner = styled(motion.div)`
  width: 20px;
  height: 20px;
  border: 2px solid rgba(66, 220, 219, 0.3);
  border-top: 2px solid rgba(66, 220, 219, 1);
  border-radius: 50%;
`;

const SummarySection = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: ${({ success }) => 
    success 
      ? 'linear-gradient(90deg, rgba(66, 220, 219, 0.1), rgba(66, 220, 219, 0.05))' 
      : 'linear-gradient(90deg, rgba(255, 87, 87, 0.1), rgba(255, 87, 87, 0.05))'};
  border-radius: 5px;
  align-items: center;
  margin-bottom: 1rem;
`;

const SummaryText = styled.div`
  font-weight: 600;
  color: ${({ success }) => 
    success ? 'rgba(66, 220, 219, 1)' : 'rgba(255, 87, 87, 1)'};
`;

const Timestamp = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
`;

const DiagnosticPanel = ({ onClose }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [expandedDetails, setExpandedDetails] = useState({});
  
  const runDiagnostic = async () => {
    setIsRunning(true);
    try {
      const diagnosticResults = await aiService.runDiagnostic();
      setResults(diagnosticResults);
    } catch (error) {
      console.error('Error running diagnostic:', error);
      setResults({
        success: false,
        message: `Diagnostic failed with error: ${error.message}`,
        timestamp: new Date().toISOString(),
        tests: {}
      });
    } finally {
      setIsRunning(false);
    }
  };
  
  const toggleDetails = (testName) => {
    setExpandedDetails(prev => ({
      ...prev,
      [testName]: !prev[testName]
    }));
  };
  
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  return (
    <PanelContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <PanelHeader>
        <Title>AI Model Diagnostic</Title>
        <CloseButton onClick={onClose}>×</CloseButton>
      </PanelHeader>
      
      <div>
        <RunButton 
          onClick={runDiagnostic} 
          disabled={isRunning}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isRunning ? (
            <LoadingSpinner 
              animate={{ rotate: 360 }} 
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
          ) : 'Run Diagnostic Test'}
        </RunButton>
      </div>
      
      {results && (
        <ResultSection>
          <SummarySection success={results.success}>
            <SummaryText success={results.success}>
              {results.message}
              <Timestamp>{formatTimestamp(results.timestamp)}</Timestamp>
            </SummaryText>
            <StatusBadge success={results.success}>
              {results.success ? 'PASSED' : 'FAILED'}
            </StatusBadge>
          </SummarySection>
          
          {results.tests && Object.entries(results.tests).map(([testName, testResult]) => (
            <TestResult key={testName} success={testResult.success}>
              <TestTitle>
                {testName.charAt(0).toUpperCase() + testName.slice(1).replace(/([A-Z])/g, ' $1')}
                <StatusBadge success={testResult.success}>
                  {testResult.success ? 'PASSED' : 'FAILED'}
                </StatusBadge>
              </TestTitle>
              <TestMessage>{testResult.message}</TestMessage>
              {testResult.details && (
                <>
                  <DetailToggle onClick={() => toggleDetails(testName)}>
                    {expandedDetails[testName] ? 'Hide Details' : 'Show Details'}
                  </DetailToggle>
                  {expandedDetails[testName] && (
                    <DetailBox
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      {JSON.stringify(testResult.details, null, 2)}
                    </DetailBox>
                  )}
                </>
              )}
            </TestResult>
          ))}
        </ResultSection>
      )}
    </PanelContainer>
  );
};

export default DiagnosticPanel; 