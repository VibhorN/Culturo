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

// Country-specific color schemes based on flag colors
const countryColors = {
  'Japan': {
    primary: '#DC143C', // Red
    secondary: '#FFFFFF', // White
    accent: '#FFD700', // Gold
    gradient: 'linear-gradient(135deg, #8B0000 0%, #DC143C 25%, rgba(255, 255, 255, 0.5) 40%, rgba(255, 255, 255, 0.4) 50%, rgba(255, 255, 255, 0.3) 60%, #DC143C 75%, #8B0000 100%)',
    earthTone: true,
  },
  'France': {
    primary: '#002654', // Blue
    secondary: '#FFFFFF', // White
    accent: '#ED2939', // Red
    gradient: 'linear-gradient(135deg, #002654 0%, #0055A4 30%, rgba(255, 255, 255, 0.15) 50%, #0055A4 70%, #ED2939 100%)',
    earthTone: true,
  },
  'Spain': {
    primary: '#AA151B', // Red
    secondary: '#F1BF00', // Yellow
    accent: '#FFFFFF', // White
    gradient: 'linear-gradient(135deg, #AA151B 0%, #CC1818 25%, #F1BF00 50%, #FFE400 75%, #AA151B 100%)',
    earthTone: true,
  }
};

const Container = styled(motion.div)`
  display: flex;
  width: 100%;
  height: 100vh;
  background: ${props => countryColors[props.$country]?.gradient || 'linear-gradient(135deg, #2d5016 0%, #3e6b1e 25%, #4a7c29 50%, #2d5016 100%)'};
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
  width: 100%;
  position: relative;
  gap: 2rem;
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
  font-size: 1rem;
  opacity: 0.8;
`;

const FunFactContainer = styled(motion.div)`
  max-width: 700px;
  width: 90%;
  padding: 1.5rem 2rem;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
`;

const FunFactText = styled(motion.p)`
  color: white;
  font-size: 1.2rem;
  text-align: center;
  margin: 0;
  font-weight: 500;
  line-height: 1.6;
`;

const SpinnerWrapper = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
`;

// Fun facts for different countries
const countryFacts = {
  'Japan': [
    "Japan is made up of over 6,800 islands.",
    "The oldest company in the world, Kongō Gumi, was founded in Japan in 578 AD.",
    "Sushi began as a way to preserve fish in fermented rice.",
    "Tokyo was once called Edo.",
    "There are more vending machines in Japan than people in some small towns.",
    "Cherry blossoms symbolize renewal and the fleeting nature of life.",
    "Sumo wrestling has been Japan’s national sport for over 1,500 years.",
    "Mount Fuji is actually three volcanoes stacked on top of each other.",
    "Japan has the world’s highest life expectancy.",
    "Capsule hotels were invented in Japan.",
    "In Japan, slurping noodles loudly is a sign of appreciation.",
    "The Shinkansen bullet train can reach speeds over 300 km/h.",
    "There are cat, owl, and even hedgehog cafés in Japan.",
    "Japan has more than 200 flavors of Kit Kat, including green tea and wasabi.",
    "The Japanese language has no plural form for nouns.",
    "Karaoke was invented in Japan in the 1970s.",
    "There’s a festival where people throw beans to chase away evil spirits.",
    "Samurai once made up Japan’s warrior class for over 600 years.",
    "Many Japanese people celebrate Christmas with KFC.",
    "Napping at work (inemuri) is often seen as a sign of dedication."
  ]
  ,
  'France': [
    "France is the most visited country in the world.",
    "The Eiffel Tower was meant to be a temporary structure for the 1889 World's Fair.",
    "France has 12 time zones, more than any other country.",
    "The Louvre is the largest art museum on Earth.",
    "The French army was the first to use camouflage in World War I.",
    "Baguettes were officially given length and weight standards by law.",
    "France banned supermarkets from throwing away unsold food.",
    "Louis XIX was king of France for only 20 minutes.",
    "There are more than 400 kinds of cheese made in France.",
    "The guillotine was used in France until 1977.",
    "The Tour de France began in 1903.",
    "French was the official language of England for about 300 years.",
    "‘Salut!’ can mean both ‘hi’ and ‘bye.’",
    "Mont Blanc is the highest mountain in Western Europe.",
    "France was the first country to ban supermarkets from wasting food.",
    "The French drink around 10 billion glasses of wine per year.",
    "The Louvre pyramid has exactly 673 glass panes.",
    "The metric system was invented in France.",
    "There’s a small Statue of Liberty on the Seine River in Paris.",
    "France has produced more Nobel Prize winners in Literature than any other country."
  ]
  ,
  'Spain': [
    "Spain has the second-highest number of UNESCO World Heritage Sites after Italy.",
    "Spanish is the world’s second most spoken native language.",
    "Madrid is located at the very center of Spain.",
    "Spain was once the most powerful empire in the world during the 16th century.",
    "The famous ‘running of the bulls’ happens every July in Pamplona.",
    "Spain produces over half of the world’s olive oil.",
    "Flamenco is a mix of music, dance, and emotion originating from Andalusia.",
    "The world’s oldest restaurant, Sobrino de Botín, is in Madrid (opened in 1725).",
    "Spain didn’t officially participate in either World War I or II.",
    "La Tomatina is a festival where thousands of people throw tomatoes.",
    "The Sagrada Família in Barcelona has been under construction since 1882.",
    "Tapas were originally invented to cover drinks and keep flies out.",
    "Siestas are traditional afternoon naps to escape the midday heat.",
    "Spain was the first country to bring chocolate to Europe.",
    "Spanish people celebrate New Year’s Eve by eating 12 grapes at midnight.",
    "Spain’s national anthem has no official lyrics.",
    "Bullfighting dates back over 2,000 years in Spanish culture.",
    "The Pyrenees form a natural border between Spain and France.",
    "Spain is home to Europe’s only desert, the Tabernas Desert.",
    "The official name of Spain is the ‘Kingdom of Spain.’"
  ]
};

function CulturalSnapshotComplete({ query, userId, onVoiceInput }) {
  const [feed, setFeed] = useState([]);
  const [triviaQuestions, setTriviaQuestions] = useState([]);
  const [country, setCountry] = useState('');
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showContent, setShowContent] = useState(false);
  const [currentFactIndex, setCurrentFactIndex] = useState(0);

  useEffect(() => {
    if (query) {
      loadCulturalSnapshot();
    }
  }, [query]);

  // Cycle through fun facts every 3 seconds
  useEffect(() => {
    if (!loading) return;
    
    const facts = countryFacts[query] || countryFacts['Japan'];
    const interval = setInterval(() => {
      setCurrentFactIndex((prev) => (prev + 1) % facts.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [loading, query]);

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
    const facts = countryFacts[query] || countryFacts['Japan'];
    const currentFact = facts[currentFactIndex];

    return (
      <Container
        $country={query}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <LoadingContainer>
          <SpinnerWrapper
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <GlobeIcon size={100} color="white" strokeWidth={1.5} />
          </SpinnerWrapper>
          
          <FunFactContainer
            key={currentFactIndex}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6 }}
          >
            <FunFactText>💡 {currentFact}</FunFactText>
          </FunFactContainer>
          
          <ProgressText>
            Creating cultural snapshot...
          </ProgressText>
          <ProgressText style={{ fontSize: '0.85rem', opacity: 0.6 }}>
            Analyzing your query and gathering cultural content
          </ProgressText>
        </LoadingContainer>
      </Container>
    );
  }

  if (error) {
    return (
      <Container $country={country}>
        <ErrorMessage>
          <h3>Error Loading Cultural Snapshot</h3>
          <p>{error}</p>
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container
      $country={country}
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

