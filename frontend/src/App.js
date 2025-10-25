import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Volume2, VolumeX, Globe, Music, Utensils, BookOpen, MessageCircle, Calendar } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import axios from 'axios';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
`;

const Header = styled(motion.div)`
  text-align: center;
  margin-bottom: 3rem;
  color: white;
`;

const Title = styled(motion.h1)`
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Subtitle = styled(motion.p)`
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
`;

const VoiceInterface = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 2rem;
  padding: 3rem;
  margin-bottom: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const VoiceControls = styled.div`
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
`;

const VoiceButton = styled(motion.button)`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  background: ${props => props.$active ? '#ff6b6b' : 'rgba(255, 255, 255, 0.2)'};
  color: white;
  font-size: 2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    transform: scale(1.1);
    background: ${props => props.$active ? '#ff5252' : 'rgba(255, 255, 255, 0.3)'};
  }
`;

const StatusText = styled(motion.div)`
  color: white;
  font-size: 1.1rem;
  text-align: center;
  margin-bottom: 1rem;
  min-height: 1.5rem;
`;

const CountryInput = styled(motion.input)`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  color: white;
  font-size: 1.1rem;
  width: 300px;
  text-align: center;
  backdrop-filter: blur(10px);
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.7);
  }
  
  &:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
  }
`;

const CulturalContent = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
`;

const ContentCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1.5rem;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
`;

const CardContent = styled.div`
  line-height: 1.6;
`;

const LoadingSpinner = styled(motion.div)`
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  margin: 2rem auto;
`;

function App() {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [country, setCountry] = useState('');
  const [culturalData, setCulturalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('Ready to explore cultures!');
  const [transcript, setTranscript] = useState('');
  
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setStatus('Listening... Speak now!');
      };

      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('');
        
        setTranscript(transcript);
        
        if (event.results[0].isFinal) {
          handleVoiceInput(transcript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setStatus('Speech recognition error. Please try again.');
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        setStatus('Processing your request...');
      };
    }

    // Initialize speech synthesis
    synthesisRef.current = window.speechSynthesis;
  }, []);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    } else {
      toast.error('Speech recognition not supported in this browser');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const speak = (text) => {
    if (synthesisRef.current) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      
      synthesisRef.current.speak(utterance);
    }
  };

  const handleVoiceInput = async (input) => {
    setStatus('Processing your request...');
    
    // Extract country from voice input
    const countryMatch = input.match(/(?:about|teach me about|tell me about)\s+(\w+)/i);
    const extractedCountry = countryMatch ? countryMatch[1] : input;
    
    if (extractedCountry) {
      setCountry(extractedCountry);
      await fetchCulturalData(extractedCountry);
    }
  };

  const fetchCulturalData = async (countryName) => {
    setLoading(true);
    setStatus(`Gathering cultural data for ${countryName}...`);
    
    try {
      const response = await axios.get(`http://localhost:5001/api/cultural-data/${countryName}`);
      setCulturalData(response.data);
      
      // Generate and speak cultural summary
      const summary = generateCulturalSummary(response.data);
      speak(summary);
      
      setStatus(`Cultural immersion complete for ${countryName}!`);
      toast.success(`Cultural data loaded for ${countryName}!`);
    } catch (error) {
      console.error('Error fetching cultural data:', error);
      setStatus('Error loading cultural data. Please try again.');
      toast.error('Failed to load cultural data');
    } finally {
      setLoading(false);
    }
  };

  const generateCulturalSummary = (data) => {
    if (!data) return 'No cultural data available.';
    
    const country = data.country || 'this country';
    let summary = `Welcome to ${country}! `;
    
    if (data.government) {
      summary += `The government is ${data.government.title}. `;
    }
    
    if (data.food && data.food.popular_foods) {
      summary += `Popular foods include ${data.food.popular_foods.slice(0, 3).join(', ')}. `;
    }
    
    if (data.slang && data.slang.slang_expressions) {
      const firstSlang = data.slang.slang_expressions[0];
      if (firstSlang) {
        summary += `A common expression is ${firstSlang.term}, which means ${firstSlang.meaning}. `;
      }
    }
    
    if (data.festivals && data.festivals.major_festivals) {
      summary += `Major festivals include ${data.festivals.major_festivals.slice(0, 2).join(' and ')}. `;
    }
    
    summary += 'Enjoy your cultural journey!';
    return summary;
  };

  const handleCountrySubmit = (e) => {
    e.preventDefault();
    if (country.trim()) {
      fetchCulturalData(country.trim());
    }
  };

  return (
    <AppContainer>
      <Toaster position="top-right" />
      
      <Header
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Title
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          🌍 WorldWise
        </Title>
        <Subtitle
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          Duolingo meets ChatGPT — but instead of just learning a language, you live the culture.
        </Subtitle>
      </Header>

      <VoiceInterface
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <VoiceControls>
          <VoiceButton
            $active={isListening}
            onClick={isListening ? stopListening : startListening}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {isListening ? <MicOff /> : <Mic />}
          </VoiceButton>
          
          <VoiceButton
            $active={isSpeaking}
            onClick={() => speak('Hello! I am WorldWise, your cultural immersion companion.')}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {isSpeaking ? <VolumeX /> : <Volume2 />}
          </VoiceButton>
        </VoiceControls>

        <StatusText
          key={status}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {status}
        </StatusText>

        {transcript && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ color: 'rgba(255, 255, 255, 0.8)', textAlign: 'center', marginBottom: '1rem' }}
          >
            "{transcript}"
          </motion.div>
        )}

        <form onSubmit={handleCountrySubmit}>
          <CountryInput
            type="text"
            placeholder="Or type a country name..."
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          />
        </form>
      </VoiceInterface>

      {loading && (
        <LoadingSpinner
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      )}

      <AnimatePresence>
        {culturalData && !loading && (
          <CulturalContent
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.6 }}
          >
            {culturalData.government && (
              <ContentCard
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <CardHeader>
                  <Globe size={24} />
                  <CardTitle>Government & History</CardTitle>
                </CardHeader>
                <CardContent>
                  <h4>{culturalData.government.title}</h4>
                  <p>{culturalData.government.summary}</p>
                  <a href={culturalData.government.url} target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'underline' }}>
                    Learn more on Wikipedia
                  </a>
                </CardContent>
              </ContentCard>
            )}

            {culturalData.food && (
              <ContentCard
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <CardHeader>
                  <Utensils size={24} />
                  <CardTitle>Food & Cuisine</CardTitle>
                </CardHeader>
                <CardContent>
                  <h4>Popular Foods:</h4>
                  <ul>
                    {culturalData.food.popular_foods.map((food, index) => (
                      <li key={index}>{food}</li>
                    ))}
                  </ul>
                  <h4>Etiquette Tips:</h4>
                  <ul>
                    {culturalData.food.etiquette_tips.map((tip, index) => (
                      <li key={index}>{tip}</li>
                    ))}
                  </ul>
                </CardContent>
              </ContentCard>
            )}

            {culturalData.slang && (
              <ContentCard
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <CardHeader>
                  <MessageCircle size={24} />
                  <CardTitle>Slang & Expressions</CardTitle>
                </CardHeader>
                <CardContent>
                  {culturalData.slang.slang_expressions.map((expression, index) => (
                    <div key={index} style={{ marginBottom: '1rem' }}>
                      <strong>{expression.term}</strong>
                      <p style={{ margin: '0.5rem 0' }}>{expression.meaning}</p>
                      <small style={{ opacity: 0.8 }}>{expression.usage}</small>
                    </div>
                  ))}
                </CardContent>
              </ContentCard>
            )}

            {culturalData.festivals && (
              <ContentCard
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <CardHeader>
                  <Calendar size={24} />
                  <CardTitle>Festivals & Events</CardTitle>
                </CardHeader>
                <CardContent>
                  <h4>Major Festivals:</h4>
                  <ul>
                    {culturalData.festivals.major_festivals.map((festival, index) => (
                      <li key={index}>{festival}</li>
                    ))}
                  </ul>
                  <h4>Cultural Notes:</h4>
                  <ul>
                    {culturalData.festivals.cultural_notes.map((note, index) => (
                      <li key={index}>{note}</li>
                    ))}
                  </ul>
                </CardContent>
              </ContentCard>
            )}

            {culturalData.music && (
              <ContentCard
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <CardHeader>
                  <Music size={24} />
                  <CardTitle>Music & Culture</CardTitle>
                </CardHeader>
                <CardContent>
                  {culturalData.music.playlists && culturalData.music.playlists.length > 0 ? (
                    <>
                      <h4>Trending Playlists:</h4>
                      {culturalData.music.playlists.map((playlist, index) => (
                        <div key={index} style={{ marginBottom: '1rem' }}>
                          <strong>{playlist.name}</strong>
                          <p style={{ margin: '0.5rem 0', opacity: 0.8 }}>
                            {playlist.description}
                          </p>
                          <small>Tracks: {playlist.tracks?.total || 'N/A'}</small>
                        </div>
                      ))}
                    </>
                  ) : (
                    <p>Music data will be available soon!</p>
                  )}
                </CardContent>
              </ContentCard>
            )}

            {culturalData.news && (
              <ContentCard
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <CardHeader>
                  <BookOpen size={24} />
                  <CardTitle>Current News</CardTitle>
                </CardHeader>
                <CardContent>
                  {culturalData.news.articles && culturalData.news.articles.length > 0 ? (
                    <>
                      {culturalData.news.articles.map((article, index) => (
                        <div key={index} style={{ marginBottom: '1rem' }}>
                          <h4>{article.title}</h4>
                          <p style={{ margin: '0.5rem 0', opacity: 0.8 }}>
                            {article.description}
                          </p>
                          <a href={article.url} target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'underline' }}>
                            Read more
                          </a>
                        </div>
                      ))}
                    </>
                  ) : (
                    <p>News data will be available soon!</p>
                  )}
                </CardContent>
              </ContentCard>
            )}
          </CulturalContent>
        )}
      </AnimatePresence>
    </AppContainer>
  );
}

export default App;