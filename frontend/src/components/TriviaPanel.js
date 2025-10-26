import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Trophy } from 'lucide-react';

const Container = styled.div`
  width: 90%;
  max-width: 600px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const QuestionCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 1.5rem;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
`;

const QuestionHeader = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  text-align: center;
`;

const QuestionText = styled.h2`
  color: white;
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 2rem;
  line-height: 1.6;
`;

const OptionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const OptionButton = styled.button`
  background: ${props => 
    props.$selected && props.$correct 
      ? 'rgba(76, 175, 80, 0.3)' 
      : props.$selected && !props.$correct
      ? 'rgba(244, 67, 54, 0.3)'
      : 'rgba(255, 255, 255, 0.1)'};
  border: 2px solid ${props => 
    props.$selected && props.$correct
      ? '#4caf50'
      : props.$selected && !props.$correct
      ? '#f44336'
      : 'rgba(255, 255, 255, 0.2)'};
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  color: white;
  font-size: 1rem;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 1rem;

  &:hover {
    ${props => !props.disabled && `
      background: rgba(255, 255, 255, 0.2);
      transform: translateX(4px);
    `}
  }
`;

const OptionLetter = styled.div`
  font-weight: 700;
  font-size: 1.1rem;
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
`;

const OptionText = styled.div`
  flex: 1;
`;

const Feedback = styled(motion.div)`
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
`;

const CorrectFeedback = styled(Feedback)`
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
`;

const IncorrectFeedback = styled(Feedback)`
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
`;

const SubmitButton = styled.button`
  background: linear-gradient(135deg, #64b5f6 0%, #1976d2 100%);
  border: none;
  border-radius: 0.75rem;
  padding: 1rem 2rem;
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 1.5rem;
  transition: all 0.3s ease;
  width: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CompletionScreen = styled(motion.div)`
  text-align: center;
  color: white;
`;

const TrophyIcon = styled(Trophy)`
  width: 80px;
  height: 80px;
  color: #ffd700;
  margin-bottom: 1rem;
`;

const CompletionTitle = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #ffd700, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const CompletionMessage = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
`;

function TriviaPanel({ questions, country }) {
  const [questionQueue, setQuestionQueue] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (questions && questions.length > 0) {
      setQuestionQueue(questions.map((q, idx) => ({ ...q, originalIndex: idx })));
    }
  }, [questions]);

  const currentQuestion = questionQueue[currentIndex];
  
  if (completed) {
    return (
      <CompletionScreen
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <TrophyIcon />
      <CompletionTitle>Congratulations! 🎉</CompletionTitle>
      <CompletionMessage>
        You've completed today's daily cultural quiz for {country}!
      </CompletionMessage>
      <CompletionMessage style={{ fontSize: '1rem', marginTop: '1rem' }}>
        You answered all questions correctly. Great work!
      </CompletionMessage>
    </CompletionScreen>
    );
  }

  if (!currentQuestion) {
    return (
      <Container>
        <div style={{ color: 'white', textAlign: 'center' }}>
          Loading trivia questions...
        </div>
      </Container>
    );
  }

  const handleAnswerSelect = (index) => {
    if (!showFeedback) {
      setSelectedAnswer(index);
    }
  };

  const handleSubmit = () => {
    if (selectedAnswer === null) return;

    setShowFeedback(true);
    
    setTimeout(() => {
      const isCorrect = selectedAnswer === currentQuestion.correct_answer;
      
      if (isCorrect) {
        // Move to next question
        if (currentIndex < questionQueue.length - 1) {
          setCurrentIndex(currentIndex + 1);
        } else {
          setCompleted(true);
          return;
        }
      } else {
        // Wrong answer: move to end of queue
        const reorderedQueue = [...questionQueue];
        const wrongQuestion = reorderedQueue[currentIndex];
        reorderedQueue.splice(currentIndex, 1);
        reorderedQueue.push(wrongQuestion);
        setQuestionQueue(reorderedQueue);
        // Keep same index to show next question
      }
      
      // Reset for next question
      setSelectedAnswer(null);
      setShowFeedback(false);
    }, 2000);
  };

  return (
    <Container>
      <AnimatePresence mode="wait">
        <QuestionCard
          key={currentQuestion.originalIndex}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.3 }}
        >
          <QuestionHeader>
            Question {currentIndex + 1} of {questionQueue.length}
          </QuestionHeader>
          
          <QuestionText>{currentQuestion.question}</QuestionText>
          
          <OptionsList>
            {currentQuestion.options.map((option, index) => {
              const isSelected = selectedAnswer === index;
              const isCorrect = index === currentQuestion.correct_answer;
              const showCorrect = showFeedback && isCorrect;
              const showIncorrect = showFeedback && isSelected && !isCorrect;
              
              return (
                <OptionButton
                  key={index}
                  onClick={() => handleAnswerSelect(index)}
                  disabled={showFeedback}
                  $selected={isSelected}
                  $correct={isCorrect}
                  $showFeedback={showFeedback}
                >
                  <OptionLetter>
                    {String.fromCharCode(65 + index)}
                  </OptionLetter>
                  <OptionText>{option}</OptionText>
                  {showCorrect && <CheckCircle size={20} color="#4caf50" />}
                  {showIncorrect && <XCircle size={20} color="#f44336" />}
                </OptionButton>
              );
            })}
          </OptionsList>

          {showFeedback && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {selectedAnswer === currentQuestion.correct_answer ? (
                <CorrectFeedback>
                  <CheckCircle size={24} />
                  Correct! {currentQuestion.explanation}
                </CorrectFeedback>
              ) : (
                <IncorrectFeedback>
                  <XCircle size={24} />
                  Incorrect. {currentQuestion.explanation} This question will return to the queue.
                </IncorrectFeedback>
              )}
            </motion.div>
          )}

          <SubmitButton
            onClick={handleSubmit}
            disabled={selectedAnswer === null}
          >
            Submit Answer
          </SubmitButton>
        </QuestionCard>
      </AnimatePresence>
    </Container>
  );
}

export default TriviaPanel;

