import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import Particles from 'react-particles';
import { loadFull } from 'tsparticles';
import AdmissionCards from './components/AdmissionCards';
import FeeCalculator from './components/FeeCalculator';
import NavigationMenu from './components/NavigationMenu';

const App = () => {
  const particlesInit = async (engine) => {
    await loadFull(engine);
  };

  const particlesConfig = {
    particles: {
      number: { value: 80, density: { enable: true, value_area: 800 } },
      color: { value: '#00ff9d' },
      shape: { type: 'circle' },
      opacity: { value: 0.5, random: true },
      size: { value: 3, random: true },
      line_linked: {
        enable: true,
        distance: 150,
        color: '#00ff9d',
        opacity: 0.4,
        width: 1
      },
      move: {
        enable: true,
        speed: 2,
        direction: 'none',
        random: true,
        straight: false,
        out_mode: 'out',
        bounce: false,
      }
    },
    interactivity: {
      detect_on: 'canvas',
      events: {
        onhover: { enable: true, mode: 'repulse' },
        onclick: { enable: true, mode: 'push' },
        resize: true
      }
    },
    retina_detect: true
  };

  return (
    <Box sx={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
      <Particles id="tsparticles" init={particlesInit} options={particlesConfig} />
      <NavigationMenu />
      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Typography
            variant="h1"
            component="h1"
            sx={{
              textAlign: 'center',
              my: 4,
              fontSize: { xs: '2rem', md: '3.5rem' },
              background: 'linear-gradient(45deg, #00ff9d 30%, #ff00ff 90%)',
              backgroundClip: 'text',
              textFillColor: 'transparent',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            College Admissions Portal
          </Typography>
        </motion.div>
        <AdmissionCards />
        <FeeCalculator />
      </Container>
    </Box>
  );
};

export default App;