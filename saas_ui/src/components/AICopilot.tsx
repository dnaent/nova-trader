/**
 * Nova Trader - AI Copilot Component
 * Thoughtful, adaptive AI assistance for trading decisions
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  IconButton,
  Stack,
  Chip,
  Avatar,
  Sheet,
  Divider,
  LinearProgress,
  Badge,
} from '@mui/joy';
import {
  Brain,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Info,
  Lightbulb,
  Target,
  Shield,
  X,
  Minimize2,
  Maximize2,
} from 'lucide-react';

interface Insight {
  id: string;
  type: 'opportunity' | 'risk' | 'optimization' | 'market';
  title: string;
  description: string;
  confidence: number;
  priority: 'high' | 'medium' | 'low';
  action?: string;
}

interface MarketRegime {
  regime: 'bullish' | 'bearish' | 'sideways' | 'volatile';
  confidence: number;
  characteristics: string[];
  recommendation: string;
}

const mockInsights: Insight[] = [
  {
    id: '1',
    type: 'opportunity',
    title: 'NVDA Momentum Breakout',
    description: 'Technical indicators suggest NVDA is breaking above key resistance. RSI cooling from overbought.',
    confidence: 87,
    priority: 'high',
    action: 'Consider position increase'
  },
  {
    id: '2',
    type: 'risk',
    title: 'Portfolio Concentration Risk',
    description: 'Technology sector exposure at 45%. Consider diversification into defensive sectors.',
    confidence: 92,
    priority: 'medium',
    action: 'Rebalance allocation'
  },
  {
    id: '3',
    type: 'optimization',
    title: 'Tax Efficiency Opportunity',
    description: 'GIA approaching CGT allowance limit. Consider harvesting losses or ISA transfers.',
    confidence: 95,
    priority: 'high',
    action: 'Review tax strategy'
  },
];

const mockRegime: MarketRegime = {
  regime: 'bullish',
  confidence: 78,
  characteristics: ['Low VIX', 'Strong momentum', 'Sector rotation'],
  recommendation: 'Maintain growth tilt with defensive hedges'
};

function InsightCard({ insight, onDismiss }: { insight: Insight; onDismiss: () => void }) {
  const getIcon = () => {
    switch (insight.type) {
      case 'opportunity': return <TrendingUp size={16} />;
      case 'risk': return <AlertTriangle size={16} />;
      case 'optimization': return <Target size={16} />;
      case 'market': return <Info size={16} />;
    }
  };

  const getColor = () => {
    switch (insight.type) {
      case 'opportunity': return 'success';
      case 'risk': return 'danger';
      case 'optimization': return 'warning';
      case 'market': return 'primary';
    }
  };

  const getPriorityColor = () => {
    switch (insight.priority) {
      case 'high': return 'danger';
      case 'medium': return 'warning';
      case 'low': return 'neutral';
    }
  };

  return (
    <Card variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="start" sx={{ mb: 1 }}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Avatar variant="soft" color={getColor() as any} size="sm">
            {getIcon()}
          </Avatar>
          <Typography level="body-sm" fontWeight="medium">
            {insight.title}
          </Typography>
        </Stack>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Chip
            variant="soft"
            color={getPriorityColor() as any}
            size="sm"
          >
            {insight.priority.toUpperCase()}
          </Chip>
          <IconButton variant="plain" size="sm" onClick={onDismiss}>
            <X size={14} />
          </IconButton>
        </Stack>
      </Stack>

      <Typography level="body-sm" color="neutral" sx={{ mb: 2 }}>
        {insight.description}
      </Typography>

      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box sx={{ flex: 1, mr: 2 }}>
          <Typography level="body-xs" color="neutral" sx={{ mb: 0.5 }}>
            Confidence: {insight.confidence}%
          </Typography>
          <LinearProgress
            determinate
            value={insight.confidence}
            color={insight.confidence >= 80 ? 'success' : insight.confidence >= 60 ? 'warning' : 'danger'}
            sx={{ height: 4 }}
          />
        </Box>
        {insight.action && (
          <Button variant="soft" size="sm" color={getColor() as any}>
            {insight.action}
          </Button>
        )}
      </Stack>
    </Card>
  );
}

function MarketRegimeCard({ regime }: { regime: MarketRegime }) {
  const getRegimeColor = () => {
    switch (regime.regime) {
      case 'bullish': return 'success';
      case 'bearish': return 'danger';
      case 'sideways': return 'neutral';
      case 'volatile': return 'warning';
    }
  };

  const getRegimeIcon = () => {
    switch (regime.regime) {
      case 'bullish': return <TrendingUp size={18} />;
      case 'bearish': return <TrendingDown size={18} />;
      case 'sideways': return <Target size={18} />;
      case 'volatile': return <AlertTriangle size={18} />;
    }
  };

  return (
    <Card variant="outlined" sx={{ p: 3, mb: 2 }}>
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
        <Avatar variant="soft" color={getRegimeColor() as any} size="md">
          {getRegimeIcon()}
        </Avatar>
        <Box>
          <Typography level="h4" textTransform="capitalize">
            {regime.regime} Market
          </Typography>
          <Typography level="body-sm" color="neutral">
            Confidence: {regime.confidence}%
          </Typography>
        </Box>
      </Stack>

      <LinearProgress
        determinate
        value={regime.confidence}
        color={getRegimeColor() as any}
        sx={{ height: 6, mb: 2 }}
      />

      <Typography level="body-sm" fontWeight="medium" sx={{ mb: 1 }}>
        Key Characteristics:
      </Typography>
      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
        {regime.characteristics.map((char, index) => (
          <Chip key={index} variant="soft" size="sm">
            {char}
          </Chip>
        ))}
      </Stack>

      <Box sx={{ p: 2, bgcolor: 'background.level1', borderRadius: 'sm' }}>
        <Typography level="body-sm" color="primary" fontWeight="medium" sx={{ mb: 1 }}>
          AI Recommendation:
        </Typography>
        <Typography level="body-sm">
          {regime.recommendation}
        </Typography>
      </Box>
    </Card>
  );
}

export default function AICopilot({
  isMinimized,
  onToggleMinimize,
  onClose,
}: {
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
  onClose?: () => void;
}) {
  const [insights, setInsights] = useState(mockInsights);
  const [processingCount, setProcessingCount] = useState(0);

  const dismissInsight = (id: string) => {
    setInsights(prev => prev.filter(insight => insight.id !== id));
  };

  // Simulate AI processing
  useEffect(() => {
    const interval = setInterval(() => {
      setProcessingCount(prev => (prev + 1) % 4);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (isMinimized) {
    return (
      <Badge
        badgeContent={insights.length}
        color="primary"
        variant="solid"
        size="sm"
      >
        <Card
          variant="outlined"
          sx={{
            p: 2,
            cursor: 'pointer',
            minWidth: 200,
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: 'primary.300',
              boxShadow: 'md',
            },
          }}
          onClick={onToggleMinimize}
        >
          <Stack direction="row" alignItems="center" spacing={2}>
            <Avatar variant="soft" color="primary" size="sm">
              <Brain size={16} />
            </Avatar>
            <Box>
              <Typography level="body-sm" fontWeight="medium">
                AI Copilot
              </Typography>
              <Typography level="body-xs" color="neutral">
                {insights.length} insights
              </Typography>
            </Box>
          </Stack>
        </Card>
      </Badge>
    );
  }

  return (
    <Sheet
      variant="outlined"
      sx={{
        width: 400,
        height: 'fit-content',
        maxHeight: '80vh',
        overflowY: 'auto',
        borderRadius: 'lg',
        boxShadow: 'xl',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, pb: 2 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" alignItems="center" spacing={2}>
            <Avatar variant="soft" color="primary" size="md">
              <Brain size={20} />
            </Avatar>
            <Box>
              <Typography level="h4">AI Copilot</Typography>
              <Typography level="body-sm" color="neutral">
                Real-time market analysis
              </Typography>
            </Box>
          </Stack>
          <Stack direction="row" spacing={1}>
            {onToggleMinimize && (
              <IconButton variant="plain" size="sm" onClick={onToggleMinimize}>
                <Minimize2 size={16} />
              </IconButton>
            )}
            {onClose && (
              <IconButton variant="plain" size="sm" onClick={onClose}>
                <X size={16} />
              </IconButton>
            )}
          </Stack>
        </Stack>

        {/* Processing Indicator */}
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 2 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: 'primary.500',
              animation: 'pulse 2s infinite',
            }}
          />
          <Typography level="body-xs" color="neutral" fontFamily="code">
            Processing {'.'.repeat(processingCount + 1)}
          </Typography>
        </Stack>
      </Box>

      <Divider />

      {/* Market Regime */}
      <Box sx={{ p: 3, pb: 2 }}>
        <Typography level="body-sm" fontWeight="medium" sx={{ mb: 2 }}>
          Market Regime Analysis
        </Typography>
        <MarketRegimeCard regime={mockRegime} />
      </Box>

      <Divider />

      {/* Insights */}
      <Box sx={{ p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography level="body-sm" fontWeight="medium">
            Active Insights ({insights.length})
          </Typography>
          <Button variant="plain" size="sm" startDecorator={<Lightbulb size={14} />}>
            Generate New
          </Button>
        </Stack>

        {insights.length === 0 ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 4,
              color: 'text.secondary',
            }}
          >
            <Brain size={32} style={{ opacity: 0.3, marginBottom: 8 }} />
            <Typography level="body-sm" color="neutral">
              No active insights
            </Typography>
            <Typography level="body-xs" color="neutral">
              AI is monitoring for opportunities
            </Typography>
          </Box>
        ) : (
          <Box>
            {insights.map((insight) => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onDismiss={() => dismissInsight(insight.id)}
              />
            ))}
          </Box>
        )}
      </Box>
    </Sheet>
  );
}