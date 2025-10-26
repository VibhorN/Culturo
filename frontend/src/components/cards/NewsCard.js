import React from 'react';
import styled from 'styled-components';
import { ExternalLink, Newspaper } from 'lucide-react';

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

const Description = styled.p`
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  line-height: 1.8;
  margin-bottom: 1rem;
`;

const ReadMoreLink = styled.a`
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

function NewsCard({ data }) {
  return (
    <Card>
      <Title>
        <Newspaper size={20} />
        {data.title}
      </Title>
      <Description>
        {data.description}
      </Description>
      <ReadMoreLink href={data.link} target="_blank" rel="noopener noreferrer">
        Read more <ExternalLink size={16} />
      </ReadMoreLink>
    </Card>
  );
}

export default NewsCard;

