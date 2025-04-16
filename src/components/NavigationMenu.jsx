import React from 'react';
import { Box, Button } from '@mui/material';
import { motion } from 'framer-motion';

const menuItems = [
  { label: 'Home', color: '#00ff9d' },
  { label: 'Admissions', color: '#ff00ff' },
  { label: 'Programs', color: '#00ffff' },
  { label: 'Contact', color: '#ffff00' }
];

const NavigationMenu = () => {
  return (
    <Box
      component={motion.div}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 100 }}
      sx={{
        position: 'sticky',
        top: 0,
        zIndex: 10,
        display: 'flex',
        justifyContent: 'center',
        gap: 2,
        py: 2,
        background: 'rgba(10, 10, 10, 0.8)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}
    >
      {menuItems.map((item, index) => (
        <motion.div
          key={item.label}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <Button
            variant="outlined"
            sx={{
              color: item.color,
              borderColor: item.color,
              '&:hover': {
                borderColor: item.color,
                boxShadow: `0 0 20px ${item.color}40`,
                background: `${item.color}10`
              }
            }}
          >
            {item.label}
          </Button>
        </motion.div>
      ))}
    </Box>
  );
};

export default NavigationMenu;