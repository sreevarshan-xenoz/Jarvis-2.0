import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const HeaderContainer = styled.header`
  padding: 1.5rem 2rem;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-bottom: 1px solid ${({ theme }) => theme.border};
  display: flex;
  justify-content: center;
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

const Header = () => {
  return (
    <HeaderContainer>
      <Logo
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <LogoText>AURA (Augmented User Response Assistant)</LogoText>
      </Logo>
    </HeaderContainer>
  );
};

export default Header;