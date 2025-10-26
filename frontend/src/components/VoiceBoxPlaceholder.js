import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Mic, MicOff, Phone, PhoneOff } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const Container = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
`;

const IconContainer = styled.div`
  width: 120px;
  height: 120px;
  background: ${props => props.isActive 
    ? 'radial-gradient(circle, rgba(76, 175, 80, 0.3) 0%, rgba(76, 175, 80, 0.1) 100%)'
    : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: ${props => props.isActive ? '3px solid #4CAF50' : '2px solid rgba(255, 255, 255, 0.2)'};
  cursor: pointer;
  transition: all 0.3s ease;
  animation: ${props => props.isActive ? 'pulse 2s infinite' : 'none'};
  position: relative;

  &:hover {
    background: ${props => props.isActive
      ? 'radial-gradient(circle, rgba(76, 175, 80, 0.4) 0%, rgba(76, 175, 80, 0.2) 100%)'
      : 'rgba(255, 255, 255, 0.15)'};
    transform: scale(1.05);
  }

  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
    50% { box-shadow: 0 0 0 20px rgba(76, 175, 80, 0); }
  }
`;

const Label = styled.div`
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  opacity: 0.8;
`;

const Description = styled.div`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  text-align: center;
  max-width: 200px;
`;

const StatusText = styled.div`
  color: ${props => props.isActive ? '#4CAF50' : 'rgba(255, 255, 255, 0.8)'};
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
  min-height: 1.5rem;
  margin-top: 0.5rem;
`;

const PulseRing = styled(motion.div)`
  position: absolute;
  width: 120px;
  height: 120px;
  border: 3px solid #4CAF50;
  border-radius: 50%;
  opacity: 0.3;
`;

const HiddenAudio = styled.audio`
  display: none;
`;

function VoiceBoxPlaceholder({ country = null }) {
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState(country ? `Discuss ${country}'s culture` : 'Cultural conversation');
  const [error, setError] = useState(null);
  const assistantConfigRef = useRef(null);
  const vapiCallRef = useRef(null);
  const vapiInstanceRef = useRef(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (vapiInstanceRef.current) {
        try {
          vapiInstanceRef.current.vapi.stop();
        } catch (e) {
          console.log('Error ending call on unmount');
        }
        vapiInstanceRef.current = null;
      }
      if (vapiCallRef.current) {
        vapiCallRef.current = null;
      }
    };
  }, []);

  const handleClick = async () => {
    if (isConnected) {
      // End call
      if (vapiInstanceRef.current) {
        try {
          if (vapiInstanceRef.current.vapi) {
            await vapiInstanceRef.current.vapi.stop();
          }
        } catch (e) {
          console.log('Call already ended');
        }
        vapiInstanceRef.current = null;
        vapiCallRef.current = null;
      }
      setIsConnected(false);
      setStatus(country ? `Discuss ${country}'s culture` : 'Cultural conversation');
      setError(null);
    } else {
      // Start call
      await startVapiCall();
    }
  };

  const startVapiCall = async () => {
    try {
      setStatus('Connecting...');
      setError(null);

      // Clean up any existing instance first
      if (vapiInstanceRef.current) {
        try {
          if (vapiInstanceRef.current.vapi) {
            await vapiInstanceRef.current.vapi.stop();
          }
        } catch (e) {
          console.log('Error cleaning up old instance:', e);
        }
        vapiInstanceRef.current = null;
      }

      // Get assistant configuration from backend
      const response = await axios.post('http://localhost:5001/api/voice/start-vapi', {
        query: country || 'Japan'
      });

      // Extract assistant_id from response
      assistantConfigRef.current = response.data;
      
      // Get the public key for client-side calls
      const token = await getVapiKey();
      console.log('Got Vapi token, length:', token?.length);
      
      // Import Vapi SDK
      console.log('Importing Vapi SDK...');
      let Vapi;
      try {
        const VapiModule = await import('@vapi-ai/web');
        Vapi = VapiModule.default || VapiModule.Vapi;
        if (!Vapi) {
          throw new Error('Vapi class not found in module');
        }
        console.log('Vapi SDK imported successfully');
      } catch (importError) {
        console.error('Failed to import Vapi SDK:', importError);
        setError('Failed to load voice assistant library: ' + (importError?.message || 'Unknown error'));
        setIsConnected(false);
        setStatus('Error - try again');
        return;
      }
      
      const assistantId = response.data.assistant_id;
      console.log('Creating Vapi call with assistant:', assistantId, 'token length:', token?.length);
      
      if (!assistantId) {
        setError('Assistant ID is missing');
        setIsConnected(false);
        setStatus('Error - try again');
        return;
      }
      
      // Initialize Vapi with token and assistant ID
      let vapi;
      try {
        vapi = new Vapi(token);
        console.log('Vapi instance created successfully');
      } catch (initError) {
        console.error('Failed to initialize Vapi SDK:', initError);
        setError('Failed to initialize voice assistant: ' + (initError?.message || 'Unknown error'));
        setIsConnected(false);
        setStatus('Error - try again');
        return;
      }
      
      // Set up event listeners
      vapi.on('error', (error) => {
        console.error('Vapi error object:', error);
        
        // Handle [object Object] issue properly
        let errorMsg = 'Connection error occurred';
        
        try {
          // Try multiple ways to extract error message
          if (typeof error === 'string' && error !== '[object Object]') {
            errorMsg = error;
          } else if (error instanceof Error) {
            errorMsg = error.message || 'Vapi error occurred';
          } else if (error?.message) {
            errorMsg = error.message;
          } else if (error?.error?.message) {
            errorMsg = error.error.message;
          } else if (error?.error) {
            errorMsg = String(error.error);
          } else if (error?.code) {
            errorMsg = `Error code: ${error.code}`;
          } else if (error?.toString && error.toString() !== '[object Object]') {
            errorMsg = error.toString();
          } else if (typeof error === 'object') {
            // Try to get useful info from object
            const keys = Object.keys(error || {});
            if (keys.length > 0) {
              errorMsg = `Error: ${keys.join(', ')}`;
            }
          }
        } catch (e) {
          console.error('Failed to parse error:', e);
          errorMsg = 'Connection error (check console)';
        }
        
        console.error('Final error message:', errorMsg);
        setError(errorMsg);
        setIsConnected(false);
        setStatus('Error - try again');
      });
      
      vapi.on('call-start-failed', (event) => {
        console.error('Vapi call start failed:', event);
        let errorMsg = 'Unknown error';
        if (event?.error?.message) {
          errorMsg = event.error.message;
        } else if (event?.error) {
          errorMsg = String(event.error);
        } else if (typeof event?.error === 'string') {
          errorMsg = event.error;
        }
        setError('Failed to start call: ' + errorMsg);
        setIsConnected(false);
        setStatus('Error - try again');
      });
      
      vapi.on('call-end', () => {
        console.log('Vapi call ended event');
        setIsConnected(false);
        setStatus('Call ended');
        vapiInstanceRef.current = null;
        vapiCallRef.current = null;
      });
      
      vapi.on('message', (message) => {
        console.log('Vapi message received:', message);
      });
      
      // Start the call with assistant ID
      try {
        setStatus('Starting call...');
        console.log('Calling vapi.start() with assistant:', assistantId);
        
        const call = await vapi.start(assistantId);
        console.log('Call started successfully! Call object:', call);
        
        if (!call) {
          throw new Error('Call started but no call object returned');
        }
        
        vapiInstanceRef.current = { vapi, call };
        vapiCallRef.current = call;
        setIsConnected(true);
        setStatus('In conversation');
        
        console.log('Voice call fully connected and ready');
      } catch (startError) {
        console.error('Error during call start:', startError);
        let errorMsg = 'Unknown error';
        if (startError?.message) {
          errorMsg = startError.message;
        } else if (startError?.error) {
          errorMsg = String(startError.error);
        } else {
          try {
            errorMsg = JSON.stringify(startError);
          } catch (e) {
            errorMsg = 'Failed to start call';
          }
        }
        setError('Failed to start: ' + errorMsg);
        setIsConnected(false);
        setStatus('Error - try again');
        throw startError;
      }
    } catch (error) {
      console.error('Error starting Vapi call:', error);
      let errorMsg = 'Unknown error';
      if (error?.message) {
        errorMsg = error.message;
      } else if (error?.error) {
        errorMsg = String(error.error);
      } else if (typeof error === 'string') {
        errorMsg = error;
      } else {
        try {
          errorMsg = JSON.stringify(error);
        } catch (e) {
          errorMsg = 'Failed to start conversation';
        }
      }
      setError(errorMsg);
      setIsConnected(false);
      setStatus('Error - try again');
    }
  };

  const getVapiKey = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/vapi/key');
      const key = response.data.key;
      if (!key) {
        throw new Error('Vapi key not found in response');
      }
      console.log('Got Vapi key, length:', key.length);
      return key;
    } catch (error) {
      console.error('Error getting Vapi key:', error);
      // Fallback to environment variable on client
      const fallbackKey = process.env.REACT_APP_VAPI_PUBLIC_KEY || process.env.REACT_APP_VAPI_API_KEY;
      if (!fallbackKey) {
        throw new Error('No Vapi key available');
      }
      return fallbackKey;
    }
  };

  return (
    <Container
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {isConnected && (
        <PulseRing
          animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
      <IconContainer onClick={handleClick} isActive={isConnected}>
        {isConnected ? <PhoneOff size={48} color="white" /> : <Phone size={48} color="white" />}
      </IconContainer>
      <Label>Voice Assistant</Label>
      <Description>
        {country ? `Discuss ${country}'s culture` : 'Cultural conversation'}
      </Description>
      <StatusText isActive={isConnected}>{status}</StatusText>
      {error && (
        <StatusText style={{ color: '#ff6b6b', fontSize: '0.75rem' }}>
          {error}
        </StatusText>
      )}
    </Container>
  );
}

export default VoiceBoxPlaceholder;
