import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const HeaderContainer = styled.header`
  padding: 1.5rem 2rem;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-bottom: 1px solid ${({ theme }) => theme.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const LogoText = styled.h1`
  font-size: 1.5rem;
  background: ${({ theme }) => theme.gradients.primary};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Controls = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const ModeToggle = styled.div`
  display: flex;
  background: ${({ theme }) => theme.background};
  border-radius: ${({ theme }) => theme.borderRadius.large};
  padding: 0.5rem;
  gap: 0.5rem;
`;

const ModeButton = styled(motion.button)`
  padding: 0.5rem 1rem;
  border-radius: ${({ theme }) => theme.borderRadius.medium};
  border: none;
  background: ${({ active, theme }) =>
    active ? theme.primary : 'transparent'};
  color: ${({ active, theme }) =>
    active ? theme.text : theme.textSecondary};
  cursor: pointer;
  font-weight: 500;
  transition: all ${({ theme }) => theme.animations.fast};

  &:hover {
    background: ${({ active, theme }) =>
      active ? theme.primary : theme.border};
  }
`;

const Header = ({ mode, onModeChange }) => {
  return (
    <HeaderContainer>
      <Logo
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <LogoText>SRM College AI Assistant</LogoText>
      </Logo>

      <Controls>
        <ModeToggle>
          <ModeButton
            active={mode === 'text'}
            onClick={() => onModeChange('text')}
            whileTap={{ scale: 0.95 }}
          >
            Text
          </ModeButton>
          <ModeButton
            active={mode === 'voice'}
            onClick={() => onModeChange('voice')}
            whileTap={{ scale: 0.95 }}
          >
            Voice
          </ModeButton>
          <ModeButton
            active={mode === 'hybrid'}
            onClick={() => onModeChange('hybrid')}
            whileTap={{ scale: 0.95 }}
          >
            Hybrid
          </ModeButton>
        </ModeToggle>
      </Controls>
    </HeaderContainer>
  );
};

export default Header;