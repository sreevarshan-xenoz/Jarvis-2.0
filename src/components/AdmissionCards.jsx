import React from 'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const categories = [
  {
    title: 'Regular Admission',
    description: 'Submit by January 15th. Required documents include application form, mark sheets, and certificates.',
    color: '#00ff9d'
  },
  {
    title: 'Management Quota',
    description: '35% seats allocated. Requires minimum 75% academic merit and personal interview.',
    color: '#ff00ff'
  },
  {
    title: 'Sports Quota',
    description: '5% seats reserved for athletes with state/national level certificates.',
    color: '#00ffff'
  },
  {
    title: 'International Students',
    description: 'Additional requirements include passport copy and valid student visa documents.',
    color: '#ffff00'
  }
];

const AdmissionCard = ({ title, description, color, index }) => (
  <motion.div
    initial={{ opacity: 0, y: 50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: index * 0.1 }}
    whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
  >
    <Card
      sx={{
        height: '100%',
        background: 'rgba(26, 26, 26, 0.8)',
        backdropFilter: 'blur(10px)',
        border: `1px solid ${color}`,
        borderRadius: '10px',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: `0 0 20px ${color}40`,
        }
      }}
    >
      <CardContent>
        <Typography
          variant="h5"
          gutterBottom
          sx={{
            color,
            fontFamily: 'Orbitron',
            fontWeight: 600,
            textShadow: `0 0 10px ${color}40`
          }}
        >
          {title}
        </Typography>
        <Typography variant="body1" sx={{ color: '#fff' }}>
          {description}
        </Typography>
      </CardContent>
    </Card>
  </motion.div>
);

const AdmissionCards = () => (
  <Grid container spacing={3} sx={{ mb: 6 }}>
    {categories.map((category, index) => (
      <Grid item xs={12} sm={6} md={3} key={category.title}>
        <AdmissionCard {...category} index={index} />
      </Grid>
    ))}
  </Grid>
);

export default AdmissionCards;