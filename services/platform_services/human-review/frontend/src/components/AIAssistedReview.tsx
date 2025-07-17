/**
 * AI-Assisted Review Component - Enhanced with 2025 capabilities
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Chip, 
  Alert, 
  CircularProgress,
  Tooltip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Fade,
  Zoom
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Lightbulb as LightbulbIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Psychology as PsychologyIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation } from 'react-query';
import { HfInference } from '@huggingface/inference';
import styled from 'styled-components';
import { debounce } from 'lodash';

// Styled components
const AIContainer = styled(motion.div)`
  position: sticky;
  top: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const InsightCard = styled(Card)`
  margin: 0.5rem 0;
  border-left: 4px solid;
  border-left-color: ${props => 
    props.severity === 'high' ? '#f44336' :
    props.severity === 'medium' ? '#ff9800' :
    props.severity === 'low' ? '#4caf50' : '#2196f3'
  };
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
`;

const ConstitutionalBadge = styled(Chip)`
  background: linear-gradient(45deg, #4caf50, #8bc34a);
  color: white;
  font-weight: bold;
  margin: 0.25rem;
`;

// Types
interface ReviewItem {
  id: string;
  content: string;
  context: any;
  metadata: any;
  constitutional_hash: string;
}

interface AIInsight {
  type: 'warning' | 'suggestion' | 'compliance' | 'bias' | 'sentiment';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  confidence: number;
  automated_action?: string;
  constitutional_implications?: string[];
}

interface AIAnalysis {
  overall_score: number;
  insights: AIInsight[];
  constitutional_compliance: {
    score: number;
    violations: string[];
    recommendations: string[];
  };
  bias_analysis: {
    detected_bias: boolean;
    bias_types: string[];
    mitigation_suggestions: string[];
  };
  sentiment_analysis: {
    overall_sentiment: string;
    emotional_indicators: string[];
    potential_impact: string;
  };
  processing_time: number;
}

interface AIAssistedReviewProps {
  reviewItem: ReviewItem;
  onInsightAction: (insight: AIInsight, action: string) => void;
  onConstitutionalFlag: (violations: string[]) => void;
  isVisible: boolean;
  constitutional_hash: string;
}

const AIAssistedReview: React.FC<AIAssistedReviewProps> = ({
  reviewItem,
  onInsightAction,
  onConstitutionalFlag,
  isVisible,
  constitutional_hash
}) => {
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true);
  const [hfInference] = useState(new HfInference(process.env.REACT_APP_HF_TOKEN));

  // Debounced analysis function
  const debouncedAnalysis = useMemo(
    () => debounce((content: string) => {
      if (content && aiAssistantEnabled) {
        refetchAnalysis();
      }
    }, 500),
    [aiAssistantEnabled]
  );

  // AI Analysis Query
  const { 
    data: aiAnalysis, 
    isLoading: isAnalyzing, 
    error: analysisError,
    refetch: refetchAnalysis
  } = useQuery<AIAnalysis>(
    ['ai-analysis', reviewItem.id],
    async () => {
      const response = await fetch('/api/v1/review/ai-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': constitutional_hash
        },
        body: JSON.stringify({
          content: reviewItem.content,
          context: reviewItem.context,
          metadata: reviewItem.metadata,
          constitutional_hash: constitutional_hash
        })
      });

      if (!response.ok) {
        throw new Error('AI analysis failed');
      }

      return response.json();
    },
    {
      enabled: aiAssistantEnabled && !!reviewItem.content,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  // Zero-shot classification for quick insights
  const performZeroShotClassification = useCallback(async (text: string) => {
    try {
      const result = await hfInference.zeroShotClassification({
        inputs: text,
        parameters: {
          candidate_labels: [
            'harmful content',
            'bias or discrimination',
            'constitutional violation',
            'positive contribution',
            'neutral content',
            'requires human review'
          ]
        }
      });
      
      return result;
    } catch (error) {
      console.error('Zero-shot classification failed:', error);
      return null;
    }
  }, [hfInference]);

  // Real-time sentiment analysis
  const { data: sentimentData } = useQuery(
    ['sentiment', reviewItem.content],
    async () => {
      if (!reviewItem.content) return null;
      
      try {
        const result = await hfInference.textClassification({
          inputs: reviewItem.content,
          model: 'cardiffnlp/twitter-roberta-base-sentiment-latest'
        });
        
        return result;
      } catch (error) {
        console.error('Sentiment analysis failed:', error);
        return null;
      }
    },
    {
      enabled: aiAssistantEnabled && !!reviewItem.content,
      staleTime: 2 * 60 * 1000 // 2 minutes
    }
  );

  // Constitutional compliance mutation
  const constitutionalCheckMutation = useMutation(
    async (content: string) => {
      const response = await fetch('/api/v1/review/constitutional-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': constitutional_hash
        },
        body: JSON.stringify({
          content,
          constitutional_hash: constitutional_hash
        })
      });
      
      return response.json();
    },
    {
      onSuccess: (data) => {
        if (data.violations && data.violations.length > 0) {
          onConstitutionalFlag(data.violations);
        }
      }
    }
  );

  // Effect to trigger analysis when content changes
  useEffect(() => {
    if (reviewItem.content) {
      debouncedAnalysis(reviewItem.content);
      constitutionalCheckMutation.mutate(reviewItem.content);
    }
  }, [reviewItem.content, debouncedAnalysis, constitutionalCheckMutation]);

  // Handle insight expansion
  const handleInsightToggle = (insightId: string) => {
    setExpandedInsights(prev => {
      const newSet = new Set(prev);
      if (newSet.has(insightId)) {
        newSet.delete(insightId);
      } else {
        newSet.add(insightId);
      }
      return newSet;
    });
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return '#f44336';
      case 'medium': return '#ff9800';
      case 'low': return '#4caf50';
      default: return '#2196f3';
    }
  };

  // Get insight icon
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'warning': return <WarningIcon />;
      case 'suggestion': return <LightbulbIcon />;
      case 'compliance': return <CheckCircleIcon />;
      case 'bias': return <ErrorIcon />;
      case 'sentiment': return <PsychologyIcon />;
      default: return <LightbulbIcon />;
    }
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <AIContainer
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 50 }}
        transition={{ duration: 0.3 }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" color="white" display="flex" alignItems="center">
            <PsychologyIcon sx={{ mr: 1 }} />
            AI Assistant
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            <ConstitutionalBadge 
              label={`Hash: ${constitutional_hash.substring(0, 8)}...`}
              size="small"
            />
            <IconButton
              onClick={() => setAiAssistantEnabled(!aiAssistantEnabled)}
              sx={{ color: 'white' }}
            >
              {aiAssistantEnabled ? <VisibilityIcon /> : <VisibilityOffIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Loading State */}
        {isAnalyzing && (
          <Fade in>
            <Box display="flex" alignItems="center" justifyContent="center" p={3}>
              <CircularProgress sx={{ color: 'white', mr: 2 }} />
              <Typography color="white">Analyzing content...</Typography>
            </Box>
          </Fade>
        )}

        {/* Error State */}
        {analysisError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            AI analysis failed. Please try again.
          </Alert>
        )}

        {/* AI Analysis Results */}
        {aiAnalysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Overall Score */}
            <Card sx={{ mb: 2, bgcolor: 'rgba(255, 255, 255, 0.1)', color: 'white' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">Overall Score</Typography>
                  <Typography variant="h4" color="primary">
                    {Math.round(aiAnalysis.overall_score * 100)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={aiAnalysis.overall_score * 100}
                  sx={{ mt: 1, height: 8, borderRadius: 4 }}
                />
              </CardContent>
            </Card>

            {/* Constitutional Compliance */}
            <Accordion sx={{ mb: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircleIcon color={aiAnalysis.constitutional_compliance.score > 0.8 ? 'success' : 'warning'} />
                  <Typography>Constitutional Compliance</Typography>
                  <Chip 
                    label={`${Math.round(aiAnalysis.constitutional_compliance.score * 100)}%`}
                    color={aiAnalysis.constitutional_compliance.score > 0.8 ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                {aiAnalysis.constitutional_compliance.violations.length > 0 && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Violations Detected:</Typography>
                    {aiAnalysis.constitutional_compliance.violations.map((violation, index) => (
                      <Typography key={index} variant="body2">• {violation}</Typography>
                    ))}
                  </Alert>
                )}
                
                {aiAnalysis.constitutional_compliance.recommendations.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>Recommendations:</Typography>
                    {aiAnalysis.constitutional_compliance.recommendations.map((rec, index) => (
                      <Typography key={index} variant="body2">• {rec}</Typography>
                    ))}
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>

            {/* Bias Analysis */}
            {aiAnalysis.bias_analysis.detected_bias && (
              <Accordion sx={{ mb: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <ErrorIcon color="error" />
                    <Typography>Bias Detected</Typography>
                    <Chip 
                      label={aiAnalysis.bias_analysis.bias_types.length}
                      color="error"
                      size="small"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Alert severity="error" sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Bias Types:</Typography>
                    {aiAnalysis.bias_analysis.bias_types.map((type, index) => (
                      <Typography key={index} variant="body2">• {type}</Typography>
                    ))}
                  </Alert>
                  
                  <Typography variant="subtitle2" gutterBottom>Mitigation Suggestions:</Typography>
                  {aiAnalysis.bias_analysis.mitigation_suggestions.map((suggestion, index) => (
                    <Typography key={index} variant="body2">• {suggestion}</Typography>
                  ))}
                </AccordionDetails>
              </Accordion>
            )}

            {/* Sentiment Analysis */}
            {sentimentData && (
              <Accordion sx={{ mb: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PsychologyIcon color="info" />
                    <Typography>Sentiment Analysis</Typography>
                    <Chip 
                      label={sentimentData[0]?.label || 'Unknown'}
                      color={
                        sentimentData[0]?.label === 'POSITIVE' ? 'success' :
                        sentimentData[0]?.label === 'NEGATIVE' ? 'error' : 'default'
                      }
                      size="small"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    {sentimentData.map((sentiment, index) => (
                      <Box key={index} display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">{sentiment.label}</Typography>
                        <Typography variant="body2">
                          {Math.round(sentiment.score * 100)}%
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}

            {/* AI Insights */}
            <Box>
              <Typography variant="h6" color="white" mb={1}>
                AI Insights ({aiAnalysis.insights.length})
              </Typography>
              
              {aiAnalysis.insights.map((insight, index) => (
                <Zoom key={index} in timeout={300 + index * 100}>
                  <InsightCard severity={insight.severity}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box display="flex" alignItems="center" gap={1}>
                          {getInsightIcon(insight.type)}
                          <Typography variant="subtitle1">{insight.title}</Typography>
                        </Box>
                        
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip 
                            label={`${Math.round(insight.confidence * 100)}%`}
                            size="small"
                            color="primary"
                          />
                          <Chip 
                            label={insight.severity}
                            size="small"
                            sx={{ 
                              bgcolor: getSeverityColor(insight.severity),
                              color: 'white'
                            }}
                          />
                        </Box>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" mt={1}>
                        {insight.description}
                      </Typography>
                      
                      {insight.constitutional_implications && (
                        <Alert severity="info" sx={{ mt: 1 }}>
                          <Typography variant="caption">
                            Constitutional implications: {insight.constitutional_implications.join(', ')}
                          </Typography>
                        </Alert>
                      )}
                      
                      {insight.automated_action && (
                        <Box mt={1}>
                          <Chip 
                            label={`Suggested: ${insight.automated_action}`}
                            onClick={() => onInsightAction(insight, insight.automated_action)}
                            clickable
                            color="primary"
                            variant="outlined"
                          />
                        </Box>
                      )}
                    </CardContent>
                  </InsightCard>
                </Zoom>
              ))}
            </Box>

            {/* Processing Time */}
            <Typography variant="caption" color="white" mt={2} display="block">
              Analysis completed in {aiAnalysis.processing_time.toFixed(2)}s
            </Typography>
          </motion.div>
        )}
      </AIContainer>
    </AnimatePresence>
  );
};

export default AIAssistedReview;