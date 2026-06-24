/**
 * Nova Trading - AI Model Training & Validation Dashboard
 * Local model training progress and performance validation for 3080Ti deployment
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Stack,
  Chip,
  LinearProgress,
  Alert,
  Table,
  Divider,
  Avatar,
  Switch,
  FormControl,
  FormLabel,
} from '@mui/joy';
import {
  Brain,
  Target,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Shield,
  BarChart3,
  Zap,
  PlayCircle,
  PauseCircle,
  RotateCcw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Area,
  AreaChart,
} from 'recharts';

interface ModelPerformance {
  totalTrades: number;
  winRate: number;
  sharpeRatio: number;
  maxDrawdown: number;
  avgReturn: number;
  riskAdjustedReturn: number;
  consecutiveWins: number;
  consecutiveLosses: number;
  profitFactor: number;
}

interface TradeRecord {
  id: string;
  timestamp: Date;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  entryPrice: number;
  exitPrice?: number;
  pnl?: number;
  book: 'GIA' | 'ISA' | 'SIPP';
  status: 'OPEN' | 'CLOSED';
  confidence: number;
  success?: boolean;
}

interface ValidationCriteria {
  id: string;
  name: string;
  current: number;
  target: number;
  unit: string;
  passed: boolean;
  weight: number;
}

const mockPerformance: ModelPerformance = {
  totalTrades: 127,
  winRate: 68.5,
  sharpeRatio: 0.85,
  maxDrawdown: 3.2,
  avgReturn: 2.4,
  riskAdjustedReturn: 1.8,
  consecutiveWins: 7,
  consecutiveLosses: 2,
  profitFactor: 1.45
};

const validationCriteria: ValidationCriteria[] = [
  {
    id: 'win_rate',
    name: 'Win Rate (All Books)',
    current: 68.5,
    target: 75.0,
    unit: '%',
    passed: false,
    weight: 25
  },
  {
    id: 'total_trades',
    name: 'Minimum Trade Count',
    current: 127,
    target: 200,
    unit: ' trades',
    passed: false,
    weight: 15
  },
  {
    id: 'sharpe_ratio',
    name: 'Sharpe Ratio',
    current: 0.85,
    target: 1.0,
    unit: '',
    passed: false,
    weight: 25
  },
  {
    id: 'max_drawdown',
    name: 'Maximum Drawdown',
    current: 3.2,
    target: 5.0,
    unit: '%',
    passed: true,
    weight: 20
  },
  {
    id: 'consecutive_losses',
    name: 'Max Consecutive Losses',
    current: 2,
    target: 5,
    unit: ' trades',
    passed: true,
    weight: 10
  },
  {
    id: 'profit_factor',
    name: 'Profit Factor',
    current: 1.45,
    target: 1.25,
    unit: '',
    passed: true,
    weight: 5
  }
];

const performanceHistory = [
  { day: 1, winRate: 45, sharpe: 0.2, drawdown: 2.1 },
  { day: 5, winRate: 52, sharpe: 0.35, drawdown: 2.8 },
  { day: 10, winRate: 58, sharpe: 0.48, drawdown: 3.1 },
  { day: 15, winRate: 62, sharpe: 0.55, drawdown: 2.9 },
  { day: 20, winRate: 65, sharpe: 0.68, drawdown: 3.2 },
  { day: 25, winRate: 67, sharpe: 0.78, drawdown: 2.7 },
  { day: 30, winRate: 68.5, sharpe: 0.85, drawdown: 3.2 }
];

const mockTrades: TradeRecord[] = [
  {
    id: 'TRD001',
    timestamp: new Date(Date.now() - 3600000),
    symbol: 'NVDA',
    side: 'BUY',
    quantity: 10,
    entryPrice: 945.20,
    exitPrice: 952.15,
    pnl: 69.50,
    book: 'GIA',
    status: 'CLOSED',
    confidence: 87,
    success: true
  },
  {
    id: 'TRD002',
    timestamp: new Date(Date.now() - 7200000),
    symbol: 'SPY',
    side: 'SELL',
    quantity: 20,
    entryPrice: 505.80,
    exitPrice: 503.45,
    pnl: 47.00,
    book: 'ISA',
    status: 'CLOSED',
    confidence: 92,
    success: true
  },
  {
    id: 'TRD003',
    timestamp: new Date(Date.now() - 10800000),
    symbol: 'TSLA',
    side: 'BUY',
    quantity: 5,
    entryPrice: 248.90,
    exitPrice: 245.20,
    pnl: -18.50,
    book: 'SIPP',
    status: 'CLOSED',
    confidence: 76,
    success: false
  }
];

function ValidationProgress() {
  const totalWeight = validationCriteria.reduce((sum, criteria) => sum + criteria.weight, 0);
  const passedWeight = validationCriteria
    .filter(c => c.passed)
    .reduce((sum, criteria) => sum + criteria.weight, 0);
  const overallProgress = (passedWeight / totalWeight) * 100;

  return (
    <Card variant="outlined" sx={{ p: 3, mb: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography level="h4">Live Trading Validation Progress</Typography>
        <Chip
          variant="soft"
          color={overallProgress >= 75 ? 'success' : 'warning'}
          size="lg"
        >
          {overallProgress.toFixed(1)}% Ready
        </Chip>
      </Stack>

      {overallProgress < 75 && (
        <Alert color="warning" sx={{ mb: 3 }} startDecorator={<AlertTriangle />}>
          <Box>
            <Typography level="body-sm" fontWeight="medium">
              Model Not Ready for Live Trading
            </Typography>
            <Typography level="body-xs">
              Continue paper trading until all validation criteria are met. Current progress: {overallProgress.toFixed(1)}%
            </Typography>
          </Box>
        </Alert>
      )}

      {overallProgress >= 75 && (
        <Alert color="success" sx={{ mb: 3 }} startDecorator={<CheckCircle />}>
          <Box>
            <Typography level="body-sm" fontWeight="medium">
              Model Ready for Live Trading Deployment
            </Typography>
            <Typography level="body-xs">
              All validation criteria met. Model can be safely deployed for live trading.
            </Typography>
          </Box>
        </Alert>
      )}

      <Table>
        <thead>
          <tr>
            <th>Validation Criteria</th>
            <th>Current</th>
            <th>Target</th>
            <th>Status</th>
            <th>Weight</th>
          </tr>
        </thead>
        <tbody>
          {validationCriteria.map(criteria => (
            <tr key={criteria.id}>
              <td>
                <Typography level="body-sm" fontWeight="medium">
                  {criteria.name}
                </Typography>
              </td>
              <td>
                <Typography level="body-sm" fontFamily="mono">
                  {criteria.current.toFixed(1)}{criteria.unit}
                </Typography>
              </td>
              <td>
                <Typography level="body-sm" fontFamily="mono">
                  {criteria.target.toFixed(1)}{criteria.unit}
                </Typography>
              </td>
              <td>
                <Chip
                  size="sm"
                  variant="soft"
                  color={criteria.passed ? 'success' : 'warning'}
                  startDecorator={criteria.passed ? <CheckCircle size={12} /> : <Clock size={12} />}
                >
                  {criteria.passed ? 'PASSED' : 'PENDING'}
                </Chip>
              </td>
              <td>
                <Typography level="body-sm">
                  {criteria.weight}%
                </Typography>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Card>
  );
}

function PerformanceCharts() {
  return (
    <Stack direction="row" spacing={3} sx={{ mb: 3 }}>
      <Card variant="outlined" sx={{ flex: 1, p: 3 }}>
        <Typography level="h4" sx={{ mb: 2 }}>Win Rate Evolution</Typography>
        <Box sx={{ height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={performanceHistory}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="day" />
              <YAxis domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--joy-palette-background-surface)',
                  border: '1px solid var(--joy-palette-divider)',
                  borderRadius: '8px',
                }}
              />
              <Line
                type="monotone"
                dataKey="winRate"
                stroke="var(--joy-palette-success-500)"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </Card>

      <Card variant="outlined" sx={{ flex: 1, p: 3 }}>
        <Typography level="h4" sx={{ mb: 2 }}>Sharpe Ratio Progress</Typography>
        <Box sx={{ height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={performanceHistory}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="day" />
              <YAxis domain={[0, 2]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--joy-palette-background-surface)',
                  border: '1px solid var(--joy-palette-divider)',
                  borderRadius: '8px',
                }}
              />
              <Area
                type="monotone"
                dataKey="sharpe"
                stroke="var(--joy-palette-primary-500)"
                fill="var(--joy-palette-primary-200)"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      </Card>
    </Stack>
  );
}

export default function AIModelTraining() {
  const [isTraining, setIsTraining] = useState(true);
  const [paperTradingEnabled, setPaperTradingEnabled] = useState(true);
  const [liveTradingEnabled, setLiveTradingEnabled] = useState(false);

  // Calculate overall validation status
  const validationPassed = validationCriteria.every(c => c.passed);
  const canEnableLiveTrading = validationPassed && mockPerformance.totalTrades >= 200;

  const handleToggleLiveTrading = () => {
    if (canEnableLiveTrading) {
      setLiveTradingEnabled(!liveTradingEnabled);
    }
  };

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography level="h3">AI Model Training & Validation</Typography>
          <Typography level="body-sm" color="neutral">
            Local 3080Ti model training progress and live trading readiness
          </Typography>
        </Box>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Chip
            variant="soft"
            color={isTraining ? 'primary' : 'neutral'}
            startDecorator={isTraining ? <PlayCircle size={14} /> : <PauseCircle size={14} />}
          >
            {isTraining ? 'Training Active' : 'Training Paused'}
          </Chip>
          <Button
            variant="outlined"
            onClick={() => setIsTraining(!isTraining)}
            startDecorator={isTraining ? <PauseCircle size={16} /> : <PlayCircle size={16} />}
          >
            {isTraining ? 'Pause' : 'Resume'}
          </Button>
        </Stack>
      </Stack>

      {/* Model Configuration */}
      <Card variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Typography level="h4" sx={{ mb: 2 }}>Model Configuration (3080Ti)</Typography>
        <Stack direction="row" spacing={4}>
          <Box>
            <Typography level="body-sm" color="neutral">Model Type</Typography>
            <Typography level="body-sm" fontWeight="medium">LLaMA-based Quantitative Trading Model</Typography>
          </Box>
          <Box>
            <Typography level="body-sm" color="neutral">Hardware</Typography>
            <Typography level="body-sm" fontWeight="medium">NVIDIA RTX 3080Ti (Local)</Typography>
          </Box>
          <Box>
            <Typography level="body-sm" color="neutral">Framework</Typography>
            <Typography level="body-sm" fontWeight="medium">Ollama + PyTorch</Typography>
          </Box>
          <Box>
            <Typography level="body-sm" color="neutral">Market Focus</Typography>
            <Typography level="body-sm" fontWeight="medium">UK Equities & ETFs</Typography>
          </Box>
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Stack direction="row" spacing={4}>
          <FormControl>
            <FormLabel>Paper Trading</FormLabel>
            <Switch
              checked={paperTradingEnabled}
              onChange={(e) => setPaperTradingEnabled(e.target.checked)}
              endDecorator={paperTradingEnabled ? "Enabled" : "Disabled"}
            />
          </FormControl>
          <FormControl>
            <FormLabel>Live Trading</FormLabel>
            <Switch
              checked={liveTradingEnabled}
              onChange={handleToggleLiveTrading}
              disabled={!canEnableLiveTrading}
              endDecorator={liveTradingEnabled ? "Enabled" : "Disabled"}
            />
          </FormControl>
        </Stack>

        {!canEnableLiveTrading && (
          <Alert color="warning" sx={{ mt: 2 }} startDecorator={<Shield />}>
            <Typography level="body-sm">
              Live trading disabled until model achieves 75%+ win rate across 200+ paper trades
            </Typography>
          </Alert>
        )}
      </Card>

      {/* Validation Progress */}
      <ValidationProgress />

      {/* Current Performance Metrics */}
      <Card variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Typography level="h4" sx={{ mb: 3 }}>Current Performance Metrics</Typography>
        <Stack direction="row" spacing={3}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography level="h2" color={mockPerformance.winRate >= 75 ? 'success' : 'warning'}>
              {mockPerformance.winRate.toFixed(1)}%
            </Typography>
            <Typography level="body-sm" color="neutral">Win Rate</Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography level="h2" color={mockPerformance.sharpeRatio >= 1.0 ? 'success' : 'warning'}>
              {mockPerformance.sharpeRatio.toFixed(2)}
            </Typography>
            <Typography level="body-sm" color="neutral">Sharpe Ratio</Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography level="h2" color={mockPerformance.maxDrawdown <= 5 ? 'success' : 'danger'}>
              {mockPerformance.maxDrawdown.toFixed(1)}%
            </Typography>
            <Typography level="body-sm" color="neutral">Max Drawdown</Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography level="h2" color="primary">
              {mockPerformance.totalTrades}
            </Typography>
            <Typography level="body-sm" color="neutral">Total Trades</Typography>
          </Box>
        </Stack>
      </Card>

      {/* Performance Charts */}
      <PerformanceCharts />

      {/* Recent Trades */}
      <Card variant="outlined" sx={{ p: 3 }}>
        <Typography level="h4" sx={{ mb: 2 }}>Recent Paper Trades</Typography>
        <Table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Quantity</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>P&L</th>
              <th>Book</th>
              <th>Confidence</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {mockTrades.map(trade => (
              <tr key={trade.id}>
                <td>
                  <Typography level="body-sm">
                    {trade.timestamp.toLocaleTimeString()}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm" fontWeight="medium">
                    {trade.symbol}
                  </Typography>
                </td>
                <td>
                  <Chip
                    size="sm"
                    variant="soft"
                    color={trade.side === 'BUY' ? 'success' : 'danger'}
                  >
                    {trade.side}
                  </Chip>
                </td>
                <td>
                  <Typography level="body-sm" fontFamily="mono">
                    {trade.quantity}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm" fontFamily="mono">
                    ${trade.entryPrice.toFixed(2)}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm" fontFamily="mono">
                    {trade.exitPrice ? `$${trade.exitPrice.toFixed(2)}` : '-'}
                  </Typography>
                </td>
                <td>
                  <Typography
                    level="body-sm"
                    fontFamily="mono"
                    color={trade.pnl && trade.pnl >= 0 ? 'success' : 'danger'}
                  >
                    {trade.pnl ? `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}` : '-'}
                  </Typography>
                </td>
                <td>
                  <Chip size="sm" variant="soft" color={
                    trade.book === 'GIA' ? 'warning' :
                    trade.book === 'ISA' ? 'success' : 'primary'
                  }>
                    {trade.book}
                  </Chip>
                </td>
                <td>
                  <Typography level="body-sm" fontFamily="mono">
                    {trade.confidence}%
                  </Typography>
                </td>
                <td>
                  {trade.success !== undefined && (
                    <Chip
                      size="sm"
                      variant="soft"
                      color={trade.success ? 'success' : 'danger'}
                      startDecorator={trade.success ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    >
                      {trade.success ? 'WIN' : 'LOSS'}
                    </Chip>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </Box>
  );
}