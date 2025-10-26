import React from 'react';
import styled from 'styled-components';
import { MapPin, Info } from 'lucide-react';

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
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const AttractionImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.1);
`;

const Description = styled.p`
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  line-height: 1.6;
`;

const CulturalSignificance = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 0.75rem;
  margin-top: 1rem;
  border-left: 3px solid #64b5f6;
`;

const SignificanceLabel = styled.div`
  color: #64b5f6;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

function AttractionCard({ data }) {
  return (
    <Card>
      <Title>
        <MapPin size={20} />
        {data.name}
      </Title>
      {data.photo_url && (
        <AttractionImage src={data.photo_url} alt={data.name} />
      )}
      <Description>{data.description}</Description>
      {data.cultural_significance && (
        <CulturalSignificance>
          <SignificanceLabel>
            <Info size={16} />
            Cultural Significance
          </SignificanceLabel>
          <Description style={{ margin: 0 }}>{data.cultural_significance}</Description>
        </CulturalSignificance>
      )}
    </Card>
  );
}

export default AttractionCard;

