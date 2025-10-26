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
  const [currentAudio, setCurrentAudio] = useState(null);
  const [country, setCountry] = useState('');
  const [culturalData, setCulturalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('Ready to explore cultures!');
  const [transcript, setTranscript] = useState('');
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const recordingStartTimeRef = useRef(null);


  const handleVoiceInput = async (audioBlob) => {
    setStatus('Transcribing audio...');
    console.log('Sending audio to Deepgram:', audioBlob.size, 'bytes, type:', audioBlob.type);
    
    try {
      // Try multiple language settings for better Spanish recognition
      const languageAttempts = [
        { language: 'auto', description: 'auto-detect' },
        { language: 'es', description: 'Spanish' },
        { language: 'es-US', description: 'Spanish (US)' },
        { language: 'es-ES', description: 'Spanish (Spain)' },
        { language: 'en-US', description: 'English (fallback)' }
      ];
      
      let lastError = null;
      
      for (const attempt of languageAttempts) {
        try {
          console.log(`Trying transcription with ${attempt.description}...`);
          
          const formData = new FormData();
          let filename = 'audio.webm';
          if (audioBlob.type.includes('mp4')) {
            filename = 'audio.mp4';
          } else if (audioBlob.type.includes('wav')) {
            filename = 'audio.wav';
          }
          
          formData.append('audio', audioBlob, filename);
          formData.append('language', attempt.language);
          
          const response = await axios.post('http://localhost:5001/api/voice/transcribe', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            timeout: 30000,
          });
          
          console.log(`Deepgram response (${attempt.description}):`, response.data);
          
          if (response.data.transcript && response.data.transcript.trim()) {
            console.log(`✅ Success with ${attempt.description}:`, response.data.transcript);
            const transcript = response.data.transcript;
            setTranscript(transcript);
    setStatus('Processing your request...');
    
            // Always send voice transcripts to the agentic system for intelligent processing
            await handleGeneralQuery(transcript, true);
            return; // Success, exit the function
          } else if (response.data.error) {
            lastError = new Error(response.data.error);
            console.log(`❌ ${attempt.description} failed:`, response.data.error);
          }
        } catch (error) {
          lastError = error;
          console.log(`❌ ${attempt.description} failed:`, error.message);
        }
      }
      
      // If all attempts failed, throw the last error
      throw lastError || new Error('All language attempts failed');
      
    } catch (error) {
      console.error('Error transcribing audio:', error);
      setStatus('Error transcribing audio. Please try again.');
      toast.error('Failed to transcribe audio: ' + (error.response?.data?.error || error.message));
    }
  };

  useEffect(() => {
    // Initialize audio recording
    const initializeAudioRecording = async () => {
      try {
        // Try to get the best possible audio quality with fallback options
        const audioConstraints = {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000, // Higher sample rate for better quality
          channelCount: 1, // Mono for better speech recognition
          latency: 0.01 // Low latency
        };
        
        console.log('Requesting audio with constraints:', audioConstraints);
        
        let stream;
        try {
          stream = await navigator.mediaDevices.getUserMedia({ 
            audio: audioConstraints
          });
        } catch (error) {
          console.warn('Failed with high-quality constraints, trying basic constraints:', error);
          // Fallback to basic constraints
          stream = await navigator.mediaDevices.getUserMedia({ 
            audio: true
          });
        }
        
        console.log('Audio stream obtained:', stream.getAudioTracks()[0].getSettings());
        
        // Try multiple audio formats for better compatibility
        let options = {};
        
        // Try different formats in order of preference
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          options = { 
            mimeType: 'audio/webm;codecs=opus',
            audioBitsPerSecond: 128000
          };
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          options = { 
            mimeType: 'audio/webm',
            audioBitsPerSecond: 128000
          };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          options = { 
            mimeType: 'audio/mp4',
            audioBitsPerSecond: 128000
          };
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
          options = { 
            mimeType: 'audio/wav',
            audioBitsPerSecond: 128000
          };
        } else {
          // Fallback to default
          options = {};
        }
        
        console.log('Using MediaRecorder options:', options);
        
        const mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorderRef.current = mediaRecorder;
        
        mediaRecorder.ondataavailable = (event) => {
          console.log('Audio data available:', event.data.size, 'bytes');
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          } else {
            console.warn('Empty audio chunk received');
          }
        };
        
        mediaRecorder.onstop = async () => {
          console.log('Recording stopped, processing audio...');
          const audioBlob = new Blob(audioChunksRef.current, { 
            type: mediaRecorder.mimeType || 'audio/webm' 
          });
          audioChunksRef.current = [];
          
          console.log('Audio blob created:', audioBlob.size, 'bytes, type:', audioBlob.type);
          console.log('MediaRecorder mimeType:', mediaRecorder.mimeType);
          console.log('Audio track settings:', stream.getAudioTracks()[0].getSettings());
          
          if (audioBlob.size > 1000) { // Require at least 1KB of audio data
            await handleVoiceInput(audioBlob);
          } else {
            console.error('Insufficient audio data recorded:', audioBlob.size, 'bytes');
            setStatus('No audio detected. Please speak louder and try again.');
            toast.error('No audio detected. Please speak louder and try again.');
          }
        };
        
        mediaRecorder.onerror = (event) => {
          console.error('MediaRecorder error:', event.error);
          setStatus('Recording error. Please try again.');
          toast.error('Recording error occurred');
        };
        
        console.log('Audio recording initialized successfully');
      } catch (error) {
        console.error('Error accessing microphone:', error);
        setStatus('Microphone access denied. Please allow microphone access.');
        toast.error('Microphone access denied. Please allow microphone access.');
      }
    };
    
    initializeAudioRecording();
    
    // Cleanup on unmount
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);


  const startListening = () => {
    console.log('Starting recording...');
    if (mediaRecorderRef.current) {
      if (mediaRecorderRef.current.state === 'inactive') {
        audioChunksRef.current = [];
        try {
          recordingStartTimeRef.current = Date.now();
          mediaRecorderRef.current.start(250); // Collect data every 250ms for better chunks
          setIsListening(true);
          setStatus('Listening... Speak now!');
          console.log('Recording started successfully');
          
          // Show helpful tip for Spanish speakers
          if (navigator.language.startsWith('es') || window.location.search.includes('lang=es')) {
            toast.info('💡 Tip: Speak clearly and at normal pace for better Spanish recognition');
          }
        } catch (error) {
          console.error('Error starting recording:', error);
          setStatus('Error starting recording. Please try again.');
          toast.error('Failed to start recording');
        }
    } else {
        console.log('Recorder already active, state:', mediaRecorderRef.current.state);
        setStatus('Already recording...');
      }
    } else {
      console.error('MediaRecorder not initialized');
      setStatus('Audio recording not available');
      toast.error('Audio recording not available. Please refresh the page.');
    }
  };

  const stopListening = () => {
    console.log('Stopping recording...');
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      try {
        // Ensure minimum recording duration for better speech recognition
        const recordingDuration = Date.now() - (recordingStartTimeRef.current || Date.now());
        if (recordingDuration < 1000) { // Less than 1 second
          console.log('Recording too short, waiting for minimum duration...');
          setTimeout(() => {
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
              mediaRecorderRef.current.stop();
              setIsListening(false);
              setStatus('Processing your request...');
              console.log('Recording stopped successfully');
            }
          }, 1000 - recordingDuration);
        } else {
          mediaRecorderRef.current.stop();
          setIsListening(false);
          setStatus('Processing your request...');
          console.log('Recording stopped successfully');
        }
      } catch (error) {
        console.error('Error stopping recording:', error);
        setIsListening(false);
        setStatus('Error stopping recording');
        toast.error('Failed to stop recording');
      }
    } else {
      console.log('No active recording to stop');
      setIsListening(false);
      setStatus('Ready to explore cultures!');
    }
  };

  // Language detection function
  const detectLanguageFromText = (text) => {
    const textLower = text.toLowerCase();
    
    // Spanish indicators
    const spanishWords = ['hola', 'gracias', 'por favor', 'adiós', 'sí', 'no', 'cómo', 'qué', 'dónde', 'cuándo', 'español', 'cultura', 'país'];
    const spanishChars = ['ñ', 'á', 'é', 'í', 'ó', 'ú', 'ü'];
    
    // French indicators
    const frenchWords = ['bonjour', 'merci', 's\'il vous plaît', 'au revoir', 'oui', 'non', 'comment', 'où', 'quand', 'français', 'culture', 'pays'];
    const frenchChars = ['à', 'è', 'é', 'ê', 'ë', 'î', 'ï', 'ô', 'ù', 'û', 'ü', 'ÿ', 'ç'];
    
    // German indicators
    const germanWords = ['hallo', 'danke', 'bitte', 'auf wiedersehen', 'ja', 'nein', 'wie', 'wo', 'wann', 'deutsch', 'kultur', 'land'];
    const germanChars = ['ä', 'ö', 'ü', 'ß'];
    
    // Italian indicators
    const italianWords = ['ciao', 'grazie', 'prego', 'arrivederci', 'sì', 'no', 'come', 'dove', 'quando', 'italiano', 'cultura', 'paese'];
    
    // Portuguese indicators
    const portugueseWords = ['olá', 'obrigado', 'por favor', 'tchau', 'sim', 'não', 'como', 'onde', 'quando', 'português', 'cultura', 'país'];
    
    // Check for language indicators
    if (spanishWords.some(word => textLower.includes(word)) || spanishChars.some(char => text.includes(char))) {
      return 'es';
    } else if (frenchWords.some(word => textLower.includes(word)) || frenchChars.some(char => text.includes(char))) {
      return 'fr';
    } else if (germanWords.some(word => textLower.includes(word)) || germanChars.some(char => text.includes(char))) {
      return 'de';
    } else if (italianWords.some(word => textLower.includes(word))) {
      return 'it';
    } else if (portugueseWords.some(word => textLower.includes(word))) {
      return 'pt';
    } else {
      return 'en'; // Default to English
    }
  };

  const speak = async (text) => {
    try {
      setStatus('Generating speech...');
      
      // Stop any current audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      
      // Validate text input
      if (!text || !text.trim()) {
        console.error('Empty text provided for speech synthesis');
        setStatus('Error: No text to speak');
        toast.error('No text provided for speech synthesis');
        return;
      }
      
      // Let the backend LLM detect the language automatically
      console.log('Using LLM-based language detection for speech synthesis');
      console.log(`Synthesizing text: "${text.substring(0, 100)}..."`);
      
      // Send text to VAPI for synthesis with auto language detection
      const response = await axios.post('http://localhost:5001/api/voice/synthesize', {
        text: text,
        voice: 'alloy',
        language: 'auto'  // Let the backend LLM detect the language
      });
      
      console.log('Speech synthesis response:', response.data);
      
      if (response.data.audio_url) {
        // Create audio element and play
        const audio = new Audio(response.data.audio_url);
        audioRef.current = audio;
        
        audio.onloadstart = () => {
          setIsSpeaking(true);
          setStatus('Speaking...');
        };
        
        audio.onended = () => {
          setIsSpeaking(false);
          setStatus('Ready to explore cultures!');
        };
        
        audio.onerror = () => {
          setIsSpeaking(false);
          setStatus('Error playing audio');
          toast.error('Failed to play audio');
        };
        
        await audio.play();
      } else if (response.data.vapi_call) {
        // VAPI created a voice assistant
        console.log('VAPI voice assistant created:', response.data.assistant_id);
        setStatus('Voice assistant created! Check the VAPI dashboard.');
        toast.success('Voice assistant created with VAPI!');
        
        // Open VAPI dashboard in new tab
        if (response.data.assistant_url) {
          window.open(response.data.assistant_url, '_blank');
        }
        
        // Fallback to browser speech synthesis for immediate feedback
        if (response.data.text) {
          await speakWithBrowser(response.data.text);
        }
      } else if (response.data.fallback_to_browser) {
        // Fallback to browser speech synthesis
        console.log('VAPI failed, using browser speech synthesis');
        await speakWithBrowser(response.data.text);
      } else {
        throw new Error('No audio URL received');
      }
    } catch (error) {
      console.error('Error synthesizing speech:', error);
      setIsSpeaking(false);
      setStatus('Error generating speech');
      
      // Check if it's a fallback response
      if (error.response?.data?.fallback_to_browser && error.response.data.text) {
        console.log('Using fallback browser speech synthesis');
        await speakWithBrowser(error.response.data.text);
        return;
      }
      
      // Show user-friendly error message
      const errorMessage = error.response?.data?.error || error.message || 'Failed to generate speech';
      toast.error(`Speech synthesis failed: ${errorMessage}`);
      
      // Try browser fallback as last resort
      if (text) {
        console.log('Attempting browser speech synthesis as last resort');
        await speakWithBrowser(text);
      }
    }
  };

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsSpeaking(false);
      setStatus('Ready to explore cultures!');
    }
  };

  const speakWithBrowser = (text) => {
    return new Promise((resolve, reject) => {
      if ('speechSynthesis' in window) {
        // Stop any current speech
        window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
        
        // Detect language and set appropriate voice
        const detectedLanguage = detectLanguageFromText(text);
        console.log(`Using browser TTS for language: ${detectedLanguage}`);
        
        // Get available voices
        const voices = window.speechSynthesis.getVoices();
        
        // Try to find a voice for the detected language
        let selectedVoice = null;
        if (detectedLanguage === 'es') {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('es') || 
            voice.name.toLowerCase().includes('spanish') ||
            voice.name.toLowerCase().includes('mexican')
          );
        } else if (detectedLanguage === 'fr') {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('fr') || 
            voice.name.toLowerCase().includes('french')
          );
        } else if (detectedLanguage === 'de') {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('de') || 
            voice.name.toLowerCase().includes('german')
          );
        } else if (detectedLanguage === 'it') {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('it') || 
            voice.name.toLowerCase().includes('italian')
          );
        } else if (detectedLanguage === 'pt') {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('pt') || 
            voice.name.toLowerCase().includes('portuguese')
          );
        }
        
        // Fallback to English voice
        if (!selectedVoice) {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('en') || 
            voice.name.toLowerCase().includes('english')
          );
        }
        
        if (selectedVoice) {
          utterance.voice = selectedVoice;
          utterance.lang = selectedVoice.lang;
          console.log(`Selected voice: ${selectedVoice.name} (${selectedVoice.lang})`);
        }
      
      utterance.onstart = () => {
        setIsSpeaking(true);
          setStatus('Speaking...');
      };
        
      utterance.onend = () => {
        setIsSpeaking(false);
          setStatus('Ready to explore cultures!');
          resolve();
      };
        
        utterance.onerror = (event) => {
        setIsSpeaking(false);
          setStatus('Error with speech synthesis');
          console.error('Speech synthesis error:', event.error);
          reject(event.error);
        };
        
        window.speechSynthesis.speak(utterance);
      } else {
        reject(new Error('Speech synthesis not supported'));
      }
    });
  };

  const handleGeneralQuery = async (query, isVoiceInput = false) => {
    setLoading(true);
    setStatus('Processing your request...');
    
    try {
      const response = await axios.post('http://localhost:5001/api/agent/process', {
        user_id: 'test',
        query: query,
        language: 'en',
        input_type: isVoiceInput ? 'voice' : 'text',
        audio_confidence: isVoiceInput ? 0.8 : 1.0, // Voice input might have lower confidence
        session_data: {
          previous_interactions: culturalData ? [culturalData.response] : [],
          current_context: 'cultural_learning'
        }
      });
      
      if (response.data.status === 'success' || response.data.status === 'clarification_needed') {
        // Display the response
        setCulturalData({
          country: 'General',
          response: response.data.response,
          metadata: response.data.metadata,
          isGeneralResponse: true
        });
        
        // Speak the response
        await speak(response.data.response);
        
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



  const handleCountrySubmit = (e) => {
    e.preventDefault();
    console.log('📝 handleCountrySubmit called with query:', country);
    
    if (country.trim()) {
      console.log('💬 Calling handleGeneralQuery for:', country.trim());
      // Let the LLM handle all queries - it's smart enough to recognize countries and intents
      handleGeneralQuery(country.trim(), false); // false indicates this is text input
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

        {/* Debug info for Spanish speech recognition */}
        {process.env.NODE_ENV === 'development' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ 
              color: 'rgba(255, 255, 255, 0.6)', 
              textAlign: 'center', 
              marginBottom: '1rem',
              fontSize: '0.8rem'
            }}
          >
            💡 Tip: Speak clearly and hold the microphone button for at least 1 second
          </motion.div>
        )}

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
            placeholder="🌍 Ask me anything... 'Who are you?', 'Tell me about Japan', 'Cuéntame sobre España', 'How are you?'"
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
                  
                  {/* Agent Thinking Process */}
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

                  {/* Agent Execution Logs */}
                  {culturalData.metadata?.agents_activated && (
                    <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'rgba(255, 165, 0, 0.1)', borderRadius: '10px', border: '1px solid rgba(255, 165, 0, 0.3)' }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#ffa500', textTransform: 'uppercase', letterSpacing: '1px' }}>
                        🤖 Agent Execution Log
                      </h4>
                      <div style={{ fontSize: '0.8rem', color: '#ffd700' }}>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Agents Activated:</strong> {culturalData.metadata.agents_activated.join(', ')}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Execution Plan:</strong>
                          <div style={{ marginTop: '5px', fontSize: '0.7rem', backgroundColor: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '4px' }}>
                            <div><strong>Intent:</strong> {culturalData.metadata.execution_plan?.intent || 'Unknown'}</div>
                            <div><strong>Target Country:</strong> {culturalData.metadata.execution_plan?.target_country || 'Unknown'}</div>
                            <div><strong>Data Sources:</strong> {culturalData.metadata.execution_plan?.data_sources?.join(', ') || 'None'}</div>
                            <div><strong>Confidence:</strong> {culturalData.metadata.execution_plan?.confidence || 'Unknown'}</div>
                            <div><strong>Reasoning:</strong> {culturalData.metadata.execution_plan?.reasoning || 'No reasoning provided'}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Data Retrieval Logs */}
                  {culturalData.metadata?.agent_responses?.data_retrieval?.data?._retrieval_log && (
                    <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'rgba(0, 150, 255, 0.1)', borderRadius: '10px', border: '1px solid rgba(0, 150, 255, 0.3)' }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#60b0ff', textTransform: 'uppercase', letterSpacing: '1px' }}>
                        📊 Data Retrieval Log
                      </h4>
                      <div style={{ fontSize: '0.8rem', color: '#b0d0ff' }}>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Timestamp:</strong> {culturalData.metadata.agent_responses.data_retrieval.data._retrieval_log.timestamp}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Country:</strong> {culturalData.metadata.agent_responses.data_retrieval.data._retrieval_log.country}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Sources Requested:</strong> {culturalData.metadata.agent_responses.data_retrieval.data._retrieval_log.sources_requested.join(', ')}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Sources Retrieved:</strong> {culturalData.metadata.agent_responses.data_retrieval.data._retrieval_log.sources_retrieved.join(', ')}
                        </div>
                        <div style={{ marginTop: '10px' }}>
                          <strong>Data Summary:</strong>
                          <ul style={{ margin: '5px 0 0 20px', fontSize: '0.75rem' }}>
                            {Object.entries(culturalData.metadata.agent_responses.data_retrieval.data._retrieval_log.data_summary).map(([source, summary]) => (
                              <li key={source} style={{ marginBottom: '3px' }}>
                                <strong>{source}:</strong> {summary.status === 'success' ? 
                                  `✅ ${summary.location_count || summary.article_count || summary.playlist_count || 'data'} items` : 
                                  `❌ ${summary.error || 'error'}`
                                }
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div style={{ marginTop: '10px' }}>
                          <strong>Actual Data Retrieved:</strong>
                          <div style={{ marginTop: '5px', fontSize: '0.7rem', maxHeight: '200px', overflowY: 'auto', backgroundColor: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '4px' }}>
                            {Object.entries(culturalData.metadata.agent_responses.data_retrieval.data).filter(([key]) => key !== '_retrieval_log').map(([source, data]) => (
                              <div key={source} style={{ marginBottom: '8px' }}>
                                <strong style={{ color: '#60b0ff' }}>{source.toUpperCase()}:</strong>
                                <pre style={{ margin: '2px 0', fontSize: '0.65rem', color: '#e0e0e0', whiteSpace: 'pre-wrap' }}>
                                  {JSON.stringify(data, null, 2).substring(0, 500)}
                                  {JSON.stringify(data, null, 2).length > 500 ? '...' : ''}
                                </pre>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
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