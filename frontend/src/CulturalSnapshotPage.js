import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import CulturalSnapshotComplete from './components/CulturalSnapshotComplete';
import { GlobeIcon } from 'lucide-react';

const Container = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #0a3d62 0%, #1e3c72 25%, #2a5298 50%, #0a3d62 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
`;

const TitleContainer = styled(motion.div)`
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled.h1`
  font-size: 3.5rem;
  font-weight: 900;
  color: white;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  background: linear-gradient(45deg, #ffffff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 1rem;
`;

const CountryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 900px;
  width: 100%;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
`;

const CountryCard = styled(motion.button)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 1.5rem;
  padding: 3rem 2rem;
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  
  &:hover {
    transform: translateY(-8px);
    border-color: #64b5f6;
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
  }
  
  &:active {
    transform: translateY(-4px);
  }
`;

const Flag = styled.div`
  font-size: 4rem;
  margin-bottom: 0.5rem;
`;

function CulturalSnapshotPage() {
  const [showSnapshot, setShowSnapshot] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  const countries = [
    { name: 'Japan', flag: '🇯🇵', emoji: '🍣' },
    { name: 'France', flag: '🇫🇷', emoji: '🥖' },
    { name: 'Spain', flag: '🇪🇸', emoji: '🏛️' }
  ];

  const handleCountrySelect = (countryName) => {
    setSelectedCountry(countryName);
    setShowSnapshot(true);
    setReloadKey(prev => prev + 1);
  };

  if (showSnapshot && selectedCountry) {
    return (
      <AnimatePresence mode="wait">
        <CulturalSnapshotComplete 
          key={reloadKey}
          query={selectedCountry} 
          userId="current_user"
          onVoiceInput={(newCountry) => {
            setSelectedCountry(newCountry);
          }}
        />
      </AnimatePresence>
    );
  }

  return (
    <Container>
      <TitleContainer
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Title>
          <GlobeIcon size={64} />
          Cultural Snapshot
        </Title>
        <Subtitle>Choose a country to explore its culture</Subtitle>
      </TitleContainer>

      <CountryGrid>
        {countries.map((country, index) => (
          <CountryCard
            key={country.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            onClick={() => handleCountrySelect(country.name)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Flag>{country.flag}</Flag>
            <div style={{ fontSize: '2.5rem' }}>{country.emoji}</div>
            {country.name}
          </CountryCard>
        ))}
      </CountryGrid>
    </Container>
  );
}

export default CulturalSnapshotPage;
