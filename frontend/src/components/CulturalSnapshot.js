import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import axios from 'axios';
import { MessageSquare, AlertCircle } from 'lucide-react';
import MovieCard from './cards/MovieCard';
import NewsCard from './cards/NewsCard';
import MusicCard from './cards/MusicCard';
import FoodCard from './cards/FoodCard';
import AttractionCard from './cards/AttractionCard';
import TriviaPanel from './TriviaPanel';
import VoiceBox from './VoiceBoxPlaceholder';

const Container = styled.div`
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
  padding: 1rem;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 8px;
  margin: 1rem;
`;

const ProgressText = styled.div`
  color: white;
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  opacity: 0.8;
`;

function CulturalSnapshot({ country, interests = [], onVoiceInput }) {
  const [cards, setCards] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [voiceStatus, setVoiceStatus] = useState('Click to speak');

  useEffect(() => {
    if (country) {
      loadContent();
    }
  }, [country, interests]);

  const loadContent = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load content feed
      const contentResponse = await axios.post('http://localhost:5001/api/content-feed', {
        country,
        interests
      });

      const contentCards = contentResponse.data.cards;
      setCards(contentCards);

      // Load trivia questions based on content
      const triviaResponse = await axios.post('http://localhost:5001/api/trivia', {
        country,
        content_cards: contentCards
      });

      const triviaQuestions = triviaResponse.data.questions;
      setQuestions(triviaQuestions);

      setLoading(false);
    } catch (err) {
      console.error('Error loading content:', err);
      setError(err.message);
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
      <Container>
        <LoadingContainer>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <MessageSquare size={48} />
          </motion.div>
          <ProgressText>Loading cultural snapshot for {country}...</ProgressText>
        </LoadingContainer>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage>
          <AlertCircle size={24} style={{ display: 'inline-block', marginRight: '0.5rem' }} />
          Error loading content: {error}
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <LeftPanel>
        {cards.map((card, index) => renderCard(card, index))}
      </LeftPanel>
      
      <MiddlePanel>
        <TriviaPanel questions={questions} country={country} />
      </MiddlePanel>
      
      <RightPanel>
        <VoiceBox onVoiceInput={onVoiceInput} />
      </RightPanel>
    </Container>
  );
}

export default CulturalSnapshot;

