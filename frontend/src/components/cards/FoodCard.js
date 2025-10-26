import React from 'react';
import styled from 'styled-components';
import { Utensils, ExternalLink, DollarSign } from 'lucide-react';

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

const RestaurantImage = styled.img`
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
  margin-bottom: 1rem;
  font-style: italic;
`;

const PriceLevel = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const WebsiteLink = styled.a`
  color: #64b5f6;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.3s ease;

  &:hover {
    color: #90caf9;
    text-decoration: underline;
  }
`;

function FoodCard({ data }) {
  return (
    <Card>
      <Title>
        <Utensils size={20} />
        {data.restaurant_name}
      </Title>
      {data.photo_url && (
        <RestaurantImage src={data.photo_url} alt={data.restaurant_name} />
      )}
      <Description>{data.description}</Description>
      <PriceLevel>
        <DollarSign size={16} />
        Price Level: {data.price_level}
      </PriceLevel>
      {data.website && (
        <WebsiteLink href={data.website} target="_blank" rel="noopener noreferrer">
          Learn more <ExternalLink size={16} />
        </WebsiteLink>
      )}
    </Card>
  );
}

export default FoodCard;

