import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { GlobeIcon } from 'lucide-react';
import MovieCard from './cards/MovieCard';
import NewsCard from './cards/NewsCard';
import MusicCard from './cards/MusicCard';
import FoodCard from './cards/FoodCard';
import AttractionCard from './cards/AttractionCard';
import TriviaPanel from './TriviaPanel';
import VoiceBox from './VoiceBoxPlaceholder';

const Container = styled(motion.div)`
  display: flex;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #0a3d62 0%, #1e3c72 25%, #2a5298 50%, #0a3d62 100%);
`;

const Panel = styled.div`
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  
  &:last-child {
    border-right: none;
  }
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
  }
`;

const LeftPanel = styled(Panel)`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const MiddlePanel = styled(Panel)`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const RightPanel = styled(Panel)`
  display: flex;
  justify-content: center;
  align-items: center;
`;

const CardContainer = styled(motion.div)`
  margin-bottom: 1.5rem;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  padding: 2rem;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 1rem;
  margin: 2rem;
  text-align: center;
`;

const ProgressText = styled.div`
  color: white;
  text-align: center;
  margin-top: 1rem;
  font-size: 1rem;
  opacity: 0.8;
`;

function CulturalSnapshotComplete({ query, userId, onVoiceInput }) {
  const [feed, setFeed] = useState([]);
  const [triviaQuestions, setTriviaQuestions] = useState([]);
  const [country, setCountry] = useState('');
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (query) {
      loadCulturalSnapshot();
    }
  }, [query]);

  const loadCulturalSnapshot = async () => {
    try {
      setLoading(true);
      setError(null);

      // Call orchestrate endpoint
      const response = await axios.post('http://localhost:5001/api/orchestrate', {
        query,
        userId: userId || 'anonymous'
      });

      const data = response.data;
      
      setCountry(data.country);
      setInterests(data.interests);
      setFeed(data.feed || []);
      setTriviaQuestions(data.triviaQuestions || []);
      
      setLoading(false);
      
      // Trigger slide-down animation
      setTimeout(() => setShowContent(true), 100);
      
    } catch (err) {
      console.error('Error loading cultural snapshot:', err);
      setError(err.response?.data?.error || err.message);
      setLoading(false);
    }
  };

  const renderCard = (card, index) => {
    switch (card.type) {
      case 'movie':
        return (
          <CardContainer
            key={`movie-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <MovieCard data={card} />
          </CardContainer>
        );
      case 'news':
        return (
          <CardContainer
            key={`news-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <NewsCard data={card} />
          </CardContainer>
        );
      case 'music':
        return (
          <CardContainer
            key="music"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <MusicCard data={card} />
          </CardContainer>
        );
      case 'food':
        return (
          <CardContainer
            key={`food-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <FoodCard data={card} />
          </CardContainer>
        );
      case 'attraction':
        return (
          <CardContainer
            key={`attraction-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <AttractionCard data={card} />
          </CardContainer>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Container
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <LoadingContainer>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <GlobeIcon size={64} color="white" />
          </motion.div>
          <ProgressText>Creating cultural snapshot...</ProgressText>
          <ProgressText style={{ fontSize: '0.85rem', opacity: 0.6 }}>
            Analyzing your query and gathering cultural content
          </ProgressText>
        </LoadingContainer>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage>
          <h3>Error Loading Cultural Snapshot</h3>
          <p>{error}</p>
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container
      initial={{ y: '-100%' }}
      animate={showContent ? { y: 0 } : { y: '-100%' }}
      transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
    >
      <LeftPanel>
        {feed.map((card, index) => renderCard(card, index))}
      </LeftPanel>
      
      <MiddlePanel>
        <TriviaPanel questions={triviaQuestions} country={country} />
      </MiddlePanel>
      
      <RightPanel>
        <VoiceBox country={country} onVoiceInput={(transcript) => {
          // This will start a Vapi conversation instead
          console.log('Voice conversation about', country);
        }} />
      </RightPanel>
    </Container>
  );
}

export default CulturalSnapshotComplete;

