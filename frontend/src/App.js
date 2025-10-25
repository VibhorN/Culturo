import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Volume2, VolumeX, Globe, Music, Utensils, BookOpen, MessageCircle, Calendar } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import axios from 'axios';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: 
    radial-gradient(circle at 20% 80%, rgba(34, 139, 34, 0.4) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(0, 100, 0, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(70, 130, 180, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 60% 70%, rgba(32, 178, 170, 0.2) 0%, transparent 50%),
    linear-gradient(135deg, #0a3d62 0%, #1e3c72 25%, #2a5298 50%, #0a3d62 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow-x: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 20%),
      radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 20%),
      radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.03) 0%, transparent 30%),
      url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="earth" patternUnits="userSpaceOnUse" width="100" height="100"><circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/><circle cx="30" cy="30" r="8" fill="rgba(34,139,34,0.2)"/><circle cx="70" cy="40" r="6" fill="rgba(0,100,0,0.2)"/><circle cx="20" cy="70" r="10" fill="rgba(70,130,180,0.2)"/><circle cx="80" cy="80" r="7" fill="rgba(32,178,170,0.2)"/></pattern></defs><rect width="100" height="100" fill="url(%23earth)"/></svg>');
    pointer-events: none;
    opacity: 0.3;
  }

  @media (max-width: 768px) {
    padding: 1rem;
  }

  @media (max-width: 480px) {
    padding: 0.5rem;
  }
`;

const Header = styled(motion.div)`
  text-align: center;
  margin-bottom: 3rem;
  color: white;
`;

const Title = styled(motion.h1)`
  font-size: 4rem;
  font-weight: 900;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #ffffff, #e0e7ff, #c7d2fe, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    animation: shimmer 3s infinite;
  }
  
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  @media (max-width: 768px) {
    font-size: 3rem;
  }

  @media (max-width: 480px) {
    font-size: 2.5rem;
  }
`;

const Subtitle = styled(motion.p)`
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;

  @media (max-width: 768px) {
    font-size: 1rem;
    max-width: 90%;
  }

  @media (max-width: 480px) {
    font-size: 0.9rem;
    max-width: 95%;
  }
`;

const VoiceInterface = styled(motion.div)`
  background: 
    linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  backdrop-filter: blur(20px);
  border-radius: 2rem;
  padding: 3rem;
  margin-bottom: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 2rem;
    background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    pointer-events: none;
  }

  @media (max-width: 768px) {
    padding: 2rem;
    margin-bottom: 2rem;
  }

  @media (max-width: 480px) {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border-radius: 1.5rem;
  }
`;

const VoiceControls = styled.div`
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;

  @media (max-width: 480px) {
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
`;

const VoiceButton = styled(motion.button)`
  width: 90px;
  height: 90px;
  border-radius: 50%;
  border: none;
  background: ${props => props.$active 
    ? 'linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%)' 
    : 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%)'};
  color: white;
  font-size: 2.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 50%;
    background: ${props => props.$active 
      ? 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3) 0%, transparent 50%)'
      : 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)'};
    pointer-events: none;
  }
  
  &:hover {
    transform: scale(1.1);
    background: ${props => props.$active 
      ? 'linear-gradient(135deg, #ff5252 0%, #f44336 100%)' 
      : 'linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%)'};
    box-shadow: 
      0 12px 40px rgba(0, 0, 0, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
  
  &:active {
    transform: scale(0.95);
  }

  @media (max-width: 768px) {
    width: 80px;
    height: 80px;
    font-size: 2rem;
  }

  @media (max-width: 480px) {
    width: 70px;
    height: 70px;
    font-size: 1.8rem;
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
  background: 
    linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 1.5rem;
  padding: 1.2rem 2rem;
  color: white;
  font-size: 1.1rem;
  width: 350px;
  text-align: center;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
    font-style: italic;
  }
  
  &:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.6);
    box-shadow: 
      0 0 0 3px rgba(255, 255, 255, 0.1),
      0 8px 24px rgba(0, 0, 0, 0.3);
    transform: scale(1.02);
  }
  
  &:hover {
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 
      0 6px 20px rgba(0, 0, 0, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.15);
  }

  @media (max-width: 768px) {
    width: 300px;
    padding: 1rem 1.5rem;
  }

  @media (max-width: 480px) {
    width: 250px;
    padding: 0.8rem 1.2rem;
    font-size: 1rem;
  }
`;

const CulturalContent = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  width: 100%;
  max-width: 1200px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 100%;
  }

  @media (max-width: 480px) {
    gap: 1rem;
  }
`;

const ContentCard = styled(motion.div)`
  background: 
    linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  backdrop-filter: blur(20px);
  border-radius: 1.5rem;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.05), transparent);
    pointer-events: none;
  }
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 
      0 12px 40px rgba(0, 0, 0, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
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
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #a5b4fc;
  border-radius: 50%;
  margin: 2rem auto;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    border: 2px solid rgba(165, 180, 252, 0.2);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(1.2); opacity: 0; }
  }
`;

const FloatingElement = styled(motion.div)`
  position: absolute;
  font-size: 2rem;
  opacity: 0.1;
  pointer-events: none;
  z-index: 0;
`;


function App() {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentUtterance, setCurrentUtterance] = useState(null);
  const [country, setCountry] = useState('');
  const [culturalData, setCulturalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('Ready to explore cultures!');
  const [transcript, setTranscript] = useState('');
  
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);


  const handleVoiceInput = async (input) => {
    setStatus('Processing your request...');
    
    // Check if it's a country-specific query
    const countryMatch = input.match(/(?:about|teach me about|tell me about)\s+(\w+)/i);
    const extractedCountry = countryMatch ? countryMatch[1] : null;
    
    if (extractedCountry) {
      setCountry(extractedCountry);
      await fetchCulturalData(extractedCountry);
    } else {
      // Handle as general query
      await handleGeneralQuery(input);
    }
  };

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
  }, [handleVoiceInput]);


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
      // Stop any current speech
      if (currentUtterance) {
        synthesisRef.current.cancel();
      }
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onstart = () => {
        setIsSpeaking(true);
        setCurrentUtterance(utterance);
      };
      utterance.onend = () => {
        setIsSpeaking(false);
        setCurrentUtterance(null);
      };
      utterance.onerror = () => {
        setIsSpeaking(false);
        setCurrentUtterance(null);
      };
      
      synthesisRef.current.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (synthesisRef.current && currentUtterance) {
      synthesisRef.current.cancel();
      setIsSpeaking(false);
      setCurrentUtterance(null);
    }
  };

  const handleGeneralQuery = async (query) => {
    setLoading(true);
    setStatus('Processing your request...');
    
    try {
      const response = await axios.post('http://localhost:5001/api/agent/process', {
        user_id: 'default',
        query: query,
        language: 'en'
      });
      
      if (response.data.status === 'success') {
        // Display the response
        setCulturalData({
          country: 'General',
          response: response.data.response,
          metadata: response.data.metadata,
          isGeneralResponse: true
        });
        
        // Speak the response
        speak(response.data.response);
        
        setStatus('Response ready!');
        toast.success('Got your response!');
      } else {
        throw new Error(response.data.response || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error processing query:', error);
      setStatus('Error processing your request. Please try again.');
      toast.error('Failed to process your request');
    } finally {
      setLoading(false);
    }
  };

  const fetchCulturalData = async (countryName) => {
    setLoading(true);
    setStatus(`Gathering cultural data for ${countryName}...`);
    
    try {
      const response = await axios.post('http://localhost:5001/api/agent/process', {
        user_id: 'default',
        query: `Tell me about ${countryName}`,
        language: 'en'
      });
      
      if (response.data.status === 'success') {
        // Set the response as cultural data for display
        setCulturalData({
          country: countryName,
          response: response.data.response,
          metadata: response.data.metadata
        });
        
        // Generate and speak cultural summary
        const summary = response.data.response;
        speak(summary);
        
        setStatus(`Cultural immersion complete for ${countryName}!`);
        toast.success(`Cultural data loaded for ${countryName}!`);
      } else {
        throw new Error(response.data.response || 'Failed to get cultural data');
      }
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
      // Check if it's a country-specific query
      const countryMatch = country.match(/(?:about|teach me about|tell me about)\s+(\w+)/i);
      const extractedCountry = countryMatch ? countryMatch[1] : null;
      
      if (extractedCountry) {
        fetchCulturalData(extractedCountry);
      } else {
        // Handle as general query
        handleGeneralQuery(country.trim());
      }
    }
  };

  return (
    <AppContainer>
      <Toaster position="top-right" />
      
      {/* Floating World Elements */}
      <FloatingElement
        initial={{ x: -100, y: 100, rotate: 0 }}
        animate={{ x: window.innerWidth + 100, y: 100, rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        style={{ top: '10%', left: '-100px' }}
      >
        🌍
      </FloatingElement>
      
      <FloatingElement
        initial={{ x: window.innerWidth + 100, y: 200, rotate: 0 }}
        animate={{ x: -100, y: 200, rotate: -360 }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        style={{ top: '20%', right: '-100px' }}
      >
        ✨
      </FloatingElement>
      
      <FloatingElement
        initial={{ x: -100, y: 300, rotate: 0 }}
        animate={{ x: window.innerWidth + 100, y: 300, rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        style={{ top: '30%', left: '-100px' }}
      >
        🌟
      </FloatingElement>
      
      <FloatingElement
        initial={{ x: window.innerWidth + 100, y: 400, rotate: 0 }}
        animate={{ x: -100, y: 400, rotate: -360 }}
        transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
        style={{ top: '40%', right: '-100px' }}
      >
        🌈
      </FloatingElement>

      
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
          🌍✨ Better Than Duolingo ✨🌍
        </Title>
        <Subtitle
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          🌟 Tryna learn some cool shit? Try this out this cool ahh app 🌟<br/>
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
            onClick={isSpeaking ? stopSpeaking : () => speak('Hello! I\'m WorldWise, your cultural immersion companion. Ask me about any country!')}
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
            placeholder="🌍 Ask me anything... 'Who are you?', 'Tell me about Japan', 'How are you?'"
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
            {culturalData.isGeneralResponse ? (
              <ContentCard
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                style={{ gridColumn: '1 / -1', maxWidth: '800px', margin: '0 auto' }}
              >
                <CardHeader>
                  <MessageCircle size={24} />
                  <CardTitle>Response</CardTitle>
                </CardHeader>
                <CardContent>
                  <p style={{ fontSize: '1.1rem', lineHeight: '1.6', margin: 0 }}>
                    {culturalData.response}
                  </p>
                  
                  {/* Agent Thinking Process - Always show if available */}
                  {culturalData.metadata?.agent_responses?.conversation?.thinking_process && (
                    <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#a0a0a0', textTransform: 'uppercase', letterSpacing: '1px' }}>
                        🤖 Agent Thinking Process
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.85rem', lineHeight: '1.5' }}>
                        {culturalData.metadata.agent_responses.conversation.thinking_process.map((step, index) => (
                          <li key={index} style={{ marginBottom: '5px', color: '#e0e0e0' }}>
                            {step}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Debug: Show raw thinking process if available */}
                  {culturalData.metadata?.agent_responses?.conversation?.thinking_process && (
                    <div style={{ marginTop: '10px', padding: '10px', backgroundColor: 'rgba(255, 0, 0, 0.1)', borderRadius: '5px', fontSize: '0.8rem' }}>
                      <strong>Debug:</strong> Found {culturalData.metadata.agent_responses.conversation.thinking_process.length} thinking steps
                    </div>
                  )}
                </CardContent>
              </ContentCard>
            ) : (
              <>
                {/* Original cultural data cards for country-specific queries */}
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
                {/* ... rest of the cultural cards ... */}
              </>
            )}
          </CulturalContent>
        )}
      </AnimatePresence>

    </AppContainer>
  );
}

export default App;