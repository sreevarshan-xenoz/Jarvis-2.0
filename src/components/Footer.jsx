import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const FooterContainer = styled.footer`
  padding: 2rem;
  background: ${({ theme }) => theme.backgroundSecondary};
  border-top: 1px solid ${({ theme }) => theme.border};
`;

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
`;

const FooterSection = styled(motion.div)`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const FooterTitle = styled.h3`
  color: ${({ theme }) => theme.text};
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`;

const FooterLink = styled(motion.a)`
  color: ${({ theme }) => theme.textSecondary};
  text-decoration: none;
  transition: color ${({ theme }) => theme.animations.fast};
  
  &:hover {
    color: ${({ theme }) => theme.primary};
  }
`;

const Copyright = styled.div`
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid ${({ theme }) => theme.border};
  text-align: center;
  color: ${({ theme }) => theme.textSecondary};
`;

const Footer = () => {
  const sections = [
    {
      title: 'Quick Links',
      links: [
        { text: 'Home', url: 'https://srmrmp.edu.in/' },
        { text: 'About', url: 'https://srmrmp.edu.in/about-us/' },
        { text: 'Academics', url: 'https://srmrmp.edu.in/academics/' },
        { text: 'Admissions', url: 'https://srmrmp.edu.in/admissions/' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { text: 'Student Portal', url: '#' },
        { text: 'Library', url: '#' },
        { text: 'Research', url: '#' },
        { text: 'Campus Life', url: '#' },
      ],
    },
    {
      title: 'Connect',
      links: [
        { text: 'Contact Us', url: 'https://srmrmp.edu.in/contact-us/' },
        { text: 'Facebook', url: '#' },
        { text: 'Twitter', url: '#' },
        { text: 'LinkedIn', url: '#' },
      ],
    },
  ];

  return (
    <FooterContainer>
      <FooterContent>
        {sections.map((section, index) => (
          <FooterSection
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <FooterTitle>{section.title}</FooterTitle>
            {section.links.map((link, linkIndex) => (
              <FooterLink
                key={link.text}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                whileHover={{ x: 5 }}
                transition={{ duration: 0.2 }}
              >
                {link.text}
              </FooterLink>
            ))}
          </FooterSection>
        ))}
      </FooterContent>
      <Copyright>
        © {new Date().getFullYear()} SRM College AI Assistant. All rights reserved.
      </Copyright>
    </FooterContainer>
  );
};

export default Footer;