import React, { useState } from 'react';
import { Box, Card, FormControl, InputLabel, MenuItem, Select, Typography, Slider } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

const programs = {
  'Undergraduate': { range: [150000, 250000], base: 150000 },
  'Engineering': { range: [220000, 220000], base: 220000 },
  'Medical': { range: [350000, 350000], base: 350000 },
  'MBA': { range: [280000, 280000], base: 280000 }
};

const FeeCalculator = () => {
  const [program, setProgram] = useState('');
  const [additionalServices, setAdditionalServices] = useState(0);

  const handleProgramChange = (event) => {
    setProgram(event.target.value);
  };

  const calculateTotalFees = () => {
    if (!program) return 0;
    return programs[program].base + additionalServices + 25000 + 15000; // Adding admission and development fees
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Card
        sx={{
          p: 4,
          mb: 6,
          background: 'rgba(26, 26, 26, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid #00ff9d',
          borderRadius: '10px'
        }}
      >
        <Typography
          variant="h4"
          gutterBottom
          sx={{
            color: '#00ff9d',
            fontFamily: 'Orbitron',
            textAlign: 'center',
            textShadow: '0 0 10px #00ff9d40'
          }}
        >
          Fee Calculator
        </Typography>

        <Box sx={{ mt: 4 }}>
          <FormControl fullWidth sx={{ mb: 4 }}>
            <InputLabel>Select Program</InputLabel>
            <Select
              value={program}
              onChange={handleProgramChange}
              label="Select Program"
              sx={{
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#00ff9d'
                }
              }}
            >
              {Object.keys(programs).map((prog) => (
                <MenuItem key={prog} value={prog}>{prog}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ mb: 4 }}>
            <Typography gutterBottom>Additional Services</Typography>
            <Slider
              value={additionalServices}
              onChange={(e, newValue) => setAdditionalServices(newValue)}
              min={0}
              max={50000}
              step={5000}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `₹${value.toLocaleString()}`}
              sx={{
                color: '#00ff9d',
                '& .MuiSlider-thumb': {
                  '&:hover, &.Mui-focusVisible': {
                    boxShadow: '0 0 0 8px rgba(0, 255, 157, 0.16)'
                  }
                }
              }}
            />
          </Box>

          <AnimatePresence>
            {program && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    textAlign: 'center',
                    color: '#fff',
                    fontFamily: 'Orbitron'
                  }}
                >
                  Total Fees: ₹{calculateTotalFees().toLocaleString()}
                </Typography>
              </motion.div>
            )}
          </AnimatePresence>
        </Box>
      </Card>
    </motion.div>
  );
};

export default FeeCalculator;