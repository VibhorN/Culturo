import React from 'react';
import styled from 'styled-components';
import { Music2, Play } from 'lucide-react';

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
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Playlist = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const SongItem = styled.div`
  display: flex;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const AlbumArt = styled.img`
  width: 56px;
  height: 56px;
  border-radius: 0.5rem;
  object-fit: cover;
  margin-right: 1rem;
  background: rgba(255, 255, 255, 0.1);
`;

const PlaceholderArt = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
`;

const SongInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const SongName = styled.div`
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
`;

const ArtistName = styled.div`
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
`;

const PlayButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
  }
`;

function MusicCard({ data }) {
  const songs = data.songs || [];

  const handlePlay = (song) => {
    if (song.spotify_link) {
      window.open(song.spotify_link, '_blank');
    }
  };

  return (
    <Card>
      <Title>
        <Music2 size={20} />
        Popular Songs from {data.country}
      </Title>
      <Playlist>
        {songs.map((song, index) => (
          <SongItem key={index}>
            {song.album_art ? (
              <AlbumArt src={song.album_art} alt={song.name} />
            ) : (
              <PlaceholderArt>
                <Music2 size={24} color="rgba(255,255,255,0.5)" />
              </PlaceholderArt>
            )}
            <SongInfo>
              <SongName>{song.name}</SongName>
              <ArtistName>{song.artist}</ArtistName>
            </SongInfo>
            <PlayButton onClick={() => handlePlay(song)}>
              <Play size={18} color="white" />
            </PlayButton>
          </SongItem>
        ))}
      </Playlist>
    </Card>
  );
}

export default MusicCard;

