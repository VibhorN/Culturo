import React from 'react';
import styled from 'styled-components';
import { Play } from 'lucide-react';

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
`;

const Title = styled.h3`
  color: white;
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-align: center;
`;

const VideoWrapper = styled.div`
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #000;
`;

const Video = styled.iframe`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
`;

const Description = styled.p`
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  line-height: 1.6;
  text-align: center;
`;

const PlayButton = styled.button`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 2;

  &:hover {
    background: white;
    transform: translate(-50%, -50%) scale(1.1);
  }
`;

const PlayIcon = styled(Play)`
  color: #0a3d62;
  margin-left: 3px;
`;

function MovieCard({ data }) {
  function extractYouTubeId(url) {
    if (!url) return null;
    
    // Handle YouTube video URLs (embeddable)
    const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
    const match = url.match(regex);
    
    if (match) {
      console.log('✅ Embeddable URL found:', url, '→ Video ID:', match[1]);
      return match[1];
    }
    
    // Check if it's a search URL (not embeddable)
    if (url.includes('youtube.com/results?')) {
      console.log('❌ Search URL (not embeddable):', url);
    }
    
    return null;
  }

  const trailerId = extractYouTubeId(data.trailer_link);
  const embedUrl = trailerId ? `https://www.youtube.com/embed/${trailerId}` : null;
  
  console.log('Movie:', data.title, '| Trailer URL:', data.trailer_link, '| Can embed:', !!embedUrl);

  return (
    <Card>
      <Title>{data.title}</Title>
      <VideoWrapper>
        {embedUrl ? (
          <Video
            src={embedUrl}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <>
            <PlayButton onClick={() => window.open(data.trailer_link, '_blank')}>
              <PlayIcon size={24} />
            </PlayButton>
            <Description style={{ position: 'absolute', top: '60%', width: '100%', textAlign: 'center' }}>
              Click to watch trailer
            </Description>
          </>
        )}
      </VideoWrapper>
      <Description>{data.description}</Description>
    </Card>
  );
}

export default MovieCard;

