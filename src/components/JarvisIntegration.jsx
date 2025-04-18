import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import aiService from '../services/aiService';

const AuraContainer = styled(motion.div)`
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(30, 30, 50, 0.8);
  border: 1px solid rgba(128, 10, 255, 0.4);
  border-radius: 10px;
  color: white;
  padding: 15px;
  width: 280px;
  z-index: 10;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
`;

const AuraHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(128, 10, 255, 0.3);
  padding-bottom: 10px;
`;

const AuraTitle = styled.h3`
  margin: 0;
  color: ${({ theme }) => theme.primary};
  font-size: 16px;
  display: flex;
  align-items: center;
`;

const AuraIcon = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${({ isActive }) => 
    isActive ? 'rgba(66, 220, 219, 0.8)' : 'rgba(255, 87, 87, 0.8)'};
  margin-right: 8px;
  box-shadow: 0 0 8px ${({ isActive }) => 
    isActive ? 'rgba(66, 220, 219, 0.6)' : 'rgba(255, 87, 87, 0.6)'};
`;

const StatusText = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.text};
  margin-bottom: 10px;
`;

const ActionButton = styled(motion.button)`
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid ${({ active }) => 
    active ? 'rgba(66, 220, 219, 0.6)' : 'rgba(128, 10, 255, 0.4)'};
  color: ${({ active }) => 
    active ? 'rgba(66, 220, 219, 1)' : 'white'};
  border-radius: 5px;
  padding: 8px 12px;
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &:hover:not(:disabled) {
    background: rgba(0, 0, 0, 0.7);
  }
`;

const ToggleSwitch = styled.div`
  display: flex;
  align-items: center;
  margin-top: 10px;
`;

const SwitchLabel = styled.label`
  font-size: 12px;
  margin-left: 8px;
  user-select: none;
`;

const SwitchInput = styled.input`
  height: 0;
  width: 0;
  visibility: hidden;
  position: absolute;
`;

const SwitchSlider = styled.div`
  cursor: pointer;
  width: 36px;
  height: 18px;
  background: ${({ checked }) => 
    checked ? 'rgba(66, 220, 219, 0.5)' : 'rgba(255, 87, 87, 0.5)'};
  display: block;
  border-radius: 18px;
  position: relative;
  
  &:after {
    content: '';
    position: absolute;
    top: 2px;
    left: ${({ checked }) => checked ? '20px' : '2px'};
    width: 14px;
    height: 14px;
    background: ${({ checked }) => 
      checked ? 'rgba(66, 220, 219, 1)' : 'white'};
    border-radius: 14px;
    transition: 0.3s;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  }
`;

const AuraIntegration = ({ onUseAuraChange }) => {
  const [auraAvailable, setAuraAvailable] = useState(false);
  const [auraStatus, setAuraStatus] = useState({
    initialized: false,
    running: false,
    components: {}
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useAura, setUseAura] = useState(false);
  
  // Check for available integrations
  useEffect(() => {
    const checkIntegrations = async () => {
      try {
        const integrations = await aiService.getIntegrations();
        setAuraAvailable(integrations.aura);
        
        if (integrations.aura) {
          // If AURA is available, check its status
          await checkAuraStatus();
        }
      } catch (error) {
        console.error('Error checking integrations:', error);
        setError('Failed to check for AURA integration');
      }
    };
    
    checkIntegrations();
  }, []);
  
  const checkAuraStatus = async () => {
    try {
      const status = await aiService.getAuraStatus();
      setAuraStatus(status);
      setError(null);
    } catch (error) {
      console.error('Error checking AURA status:', error);
      setError('Failed to check AURA status');
    }
  };
  
  const handleAuraAction = async (action) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await aiService.auraAction(action);
      await checkAuraStatus();
    } catch (error) {
      console.error(`Error performing AURA action (${action}):`, error);
      setError(`Failed to ${action} AURA: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleToggleUseAura = () => {
    const newValue = !useAura;
    setUseAura(newValue);
    
    // Notify parent component
    if (onUseAuraChange) {
      onUseAuraChange(newValue);
    }
  };
  
  if (!auraAvailable) {
    return null;
  }
  
  return (
    <AuraContainer
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <AuraHeader>
        <AuraTitle>
          <AuraIcon isActive={auraStatus.running} />
          AURA Core
        </AuraTitle>
      </AuraHeader>
      
      <StatusText>
        Status: {auraStatus.initialized 
          ? (auraStatus.running ? 'Running' : 'Initialized (Not Running)') 
          : 'Not Initialized'}
      </StatusText>
      
      {error && (
        <StatusText style={{ color: 'rgba(255, 87, 87, 1)' }}>
          Error: {error}
        </StatusText>
      )}
      
      <div>
        <ActionButton
          onClick={() => handleAuraAction('initialize')}
          disabled={isLoading || auraStatus.initialized}
          active={auraStatus.initialized}
          whileHover={{ scale: isLoading || auraStatus.initialized ? 1 : 1.05 }}
          whileTap={{ scale: isLoading || auraStatus.initialized ? 1 : 0.95 }}
        >
          Initialize
        </ActionButton>
        
        <ActionButton
          onClick={() => handleAuraAction('start')}
          disabled={isLoading || !auraStatus.initialized || auraStatus.running}
          active={auraStatus.running}
          whileHover={{ scale: isLoading || !auraStatus.initialized || auraStatus.running ? 1 : 1.05 }}
          whileTap={{ scale: isLoading || !auraStatus.initialized || auraStatus.running ? 1 : 0.95 }}
        >
          Start
        </ActionButton>
        
        <ActionButton
          onClick={() => handleAuraAction('stop')}
          disabled={isLoading || !auraStatus.running}
          whileHover={{ scale: isLoading || !auraStatus.running ? 1 : 1.05 }}
          whileTap={{ scale: isLoading || !auraStatus.running ? 1 : 0.95 }}
        >
          Stop
        </ActionButton>
      </div>
      
      <ToggleSwitch>
        <SwitchInput
          type="checkbox"
          id="useAura"
          checked={useAura}
          onChange={handleToggleUseAura}
        />
        <SwitchSlider
          checked={useAura}
          onClick={handleToggleUseAura}
        />
        <SwitchLabel htmlFor="useAura">
          {useAura ? 'Using AURA AI' : 'Using Cloud AI'}
        </SwitchLabel>
      </ToggleSwitch>
    </AuraContainer>
  );
};

export default AuraIntegration; 