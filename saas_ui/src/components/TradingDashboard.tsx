/**
 * Nova Trader - Clean Trading Dashboard
 * High-density information with frictionless, calm user experience
 */
import React, { useState, useEffect } from 'react';
import {
  CssVarsProvider,
  useColorScheme,
  Box,
  Card,
  Typography,
  Button,
  IconButton,
  Chip,
  Divider,
  LinearProgress,
  Sheet,
  Stack,
  Grid,
  Avatar,
  Badge,
  Switch,
  FormControl,
  FormLabel,
  Slider,
  Input,
  Select,
  Option,
} from '@mui/joy';
import {
  DarkMode,
  LightMode,
  Activity,
  TrendingUp,
  TrendingDown,
  Brain,
  Shield,
  Zap,
  Settings,
  PieChart,
  BarChart3,
  Target,
  Users,
  Cpu,
  Calculator,
  Globe,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts';
import theme from '../theme/theme';
import { BentoGrid, BentoItem } from './layout/BentoGrid';
import AICopilot from './AICopilot';

// Mock data for clean trading interface
const portfolioData = [
  { time: '09:30', price: 122500, volume: 1200, ma20: 121800 },
  { time: '10:00', price: 123100, volume: 1450, ma20: 121950 },
  { time: '10:30', price: 122800, volume: 980, ma20: 122100 },
  { time: '11:00', price: 124200, volume: 1680, ma20: 122300 },
  { time: '11:30', price: 123950, volume: 1320, ma20: 122500 },
  { time: '12:00', price: 125100, volume: 2100, ma20: 122750 },
];

const positions = [
  { symbol: 'NVDA', qty: 15, price: 950.10, change: 2.3, value: 14251.50, book: 'GIA' },
  { symbol: 'VWRL', qty: 50, price: 112.50, change: 0.8, value: 5625.00, book: 'ISA' },
  { symbol: 'SPY', qty: 20, price: 505.20, change: 1.2, value: 10104.00, book: 'SIPP' },
  { symbol: 'TSLA', qty: 8, price: 245.80, change: -1.5, value: 1966.40, book: 'GIA' },
];

const aiMetrics = [
  { metric: 'Prediction Accuracy', value: 87.3, trend: 2.1 },
  { metric: 'Risk Assessment', value: 92.1, trend: -0.8 },
  { metric: 'Signal Quality', value: 84.7, trend: 3.4 },
  { metric: 'Market Regime', value: 78.9, trend: 1.2 },
];

const riskMetrics = {
  var95: 2450,
  maxDrawdown: 8.3,
  sharpe: 1.42,
  beta: 0.73,
  correlation: 0.45,
  volatility: 18.2,
};

function ColorSchemeToggle() {
  const { mode, setMode } = useColorScheme();

  return (
    <IconButton
      onClick={() => setMode(mode === 'light' ? 'dark' : 'light')}
      variant="outlined"
      size="sm"
    >
      {mode === 'light' ? <DarkMode /> : <LightMode />}
    </IconButton>
  );
}

function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  color = 'neutral',
}: {
  title: string;
  value: string | number;
  change?: number;
  icon: any;
  color?: 'primary' | 'success' | 'danger' | 'warning' | 'neutral';
}) {
  return (
    <Card variant="outlined" sx={{ height: '100%', p: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="start">
        <Box>
          <Typography level="body-sm" color="neutral">
            {title}
          </Typography>
          <Typography level="h3" fontFamily="code" sx={{ mt: 0.5 }}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Typography>
          {change !== undefined && (
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1 }}>
              {change >= 0 ? (
                <ArrowUpRight size={16} color="#4caf50" />
              ) : (
                <ArrowDownRight size={16} color="#f44336" />
              )}
              <Typography
                level="body-sm"
                color={change >= 0 ? 'success' : 'danger'}
                fontFamily="code"
              >
                {change >= 0 ? '+' : ''}{change.toFixed(1)}%
              </Typography>
            </Stack>
          )}
        </Box>
        <Avatar variant="soft" color={color} size="sm">
          <Icon size={18} />
        </Avatar>
      </Stack>
    </Card>
  );
}

function PositionRow({ position }: { position: typeof positions[0] }) {
  const isProfit = position.change >= 0;

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: '1fr 80px 100px 80px 120px 60px',
        alignItems: 'center',
        py: 1.5,
        px: 2,
        '&:hover': {
          backgroundColor: 'background.level1',
        },
      }}
    >
      <Box>
        <Typography fontWeight="medium" fontFamily="code">
          {position.symbol}
        </Typography>
        <Typography level="body-xs" color="neutral">
          {position.book}
        </Typography>
      </Box>
      <Typography fontFamily="code" textAlign="right">
        {position.qty}
      </Typography>
      <Typography fontFamily="code" textAlign="right">
        £{position.price.toFixed(2)}
      </Typography>
      <Typography
        fontFamily="code"
        textAlign="right"
        color={isProfit ? 'success' : 'danger'}
      >
        {isProfit ? '+' : ''}{position.change}%
      </Typography>
      <Typography fontFamily="code" textAlign="right" fontWeight="medium">
        £{position.value.toLocaleString()}
      </Typography>
      <IconButton variant="plain" size="sm">
        <ChevronRight size={16} />
      </IconButton>
    </Box>
  );
}

export default function TradingDashboard() {
  const [engineStatus, setEngineStatus] = useState({
    active: true,
    lastUpdate: new Date(),
    confidence: 87.3,
    riskLevel: 'LOW',
  });

  const [copilotState, setCopilotState] = useState({
    isVisible: true,
    isMinimized: true,
  });

  const [liveMetrics, setLiveMetrics] = useState({
    totalValue: 125100,
    todayPnL: 1850,
    unrealizedPnL: 3420,
    cashBalance: 15420,
  });

  // Simulate live updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveMetrics(prev => ({
        ...prev,
        totalValue: prev.totalValue + (Math.random() - 0.5) * 100,
        todayPnL: prev.todayPnL + (Math.random() - 0.5) * 50,
      }));

      setEngineStatus(prev => ({
        ...prev,
        confidence: 85 + Math.random() * 5,
        lastUpdate: new Date(),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <CssVarsProvider theme={theme}>
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.body' }}>
        {/* Top Navigation */}
        <Sheet
          variant="outlined"
          sx={{
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            backdropFilter: 'blur(8px)',
            borderRadius: 0,
            borderLeft: 'none',
            borderRight: 'none',
            borderTop: 'none',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              py: 2,
              px: 3,
            }}
          >
            <Stack direction="row" alignItems="center" spacing={3}>
              <Typography level="h4" fontWeight="bold">
                Nova Trader
              </Typography>

              <Badge
                color={engineStatus.active ? 'success' : 'danger'}
                variant="soft"
                size="sm"
              >
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Activity size={16} />
                  <Typography level="body-sm" fontFamily="code" fontWeight="medium">
                    {engineStatus.active ? 'ACTIVE' : 'OFFLINE'}
                  </Typography>
                </Stack>
              </Badge>

              <Typography level="body-sm" color="neutral">
                AI Confidence: {engineStatus.confidence.toFixed(1)}%
              </Typography>

              <Typography level="body-sm" color="neutral">
                Risk: {engineStatus.riskLevel}
              </Typography>
            </Stack>

            <Stack direction="row" alignItems="center" spacing={2}>
              <Typography level="body-sm" color="neutral" fontFamily="code">
                £{liveMetrics.totalValue.toLocaleString()}
              </Typography>

              <Typography
                level="body-sm"
                color={liveMetrics.todayPnL >= 0 ? 'success' : 'danger'}
                fontFamily="code"
              >
                {liveMetrics.todayPnL >= 0 ? '+' : ''}£{liveMetrics.todayPnL}
              </Typography>

              <ColorSchemeToggle />

              <Avatar size="sm" variant="soft">
                PH
              </Avatar>
            </Stack>
          </Box>
        </Sheet>

        {/* Main Dashboard Content */}
        <Box sx={{ p: 3 }}>
          <BentoGrid columns={12} gap={3}>
            {/* Portfolio Performance - Large Chart */}
            <BentoItem colSpan={8} minHeight="400px">
              <Card variant="outlined" sx={{ height: '100%', p: 3 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
                  <Box>
                    <Typography level="h4">Portfolio Performance</Typography>
                    <Typography level="body-sm" color="neutral">
                      Real-time NAV tracking
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1}>
                    <Button variant="soft" size="sm">1D</Button>
                    <Button variant="outlined" size="sm">1W</Button>
                    <Button variant="outlined" size="sm">1M</Button>
                    <Button variant="outlined" size="sm">1Y</Button>
                  </Stack>
                </Stack>

                <Box sx={{ height: '300px', mt: 2 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={portfolioData}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="time" />
                      <YAxis yAxisId="price" orientation="right" />
                      <YAxis yAxisId="volume" orientation="left" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'var(--joy-palette-background-surface)',
                          border: '1px solid var(--joy-palette-divider)',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar yAxisId="volume" dataKey="volume" fill="var(--joy-palette-primary-200)" opacity={0.3} />
                      <Line
                        yAxisId="price"
                        type="monotone"
                        dataKey="price"
                        stroke="var(--joy-palette-primary-500)"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        yAxisId="price"
                        type="monotone"
                        dataKey="ma20"
                        stroke="var(--joy-palette-neutral-400)"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </Box>
              </Card>
            </BentoItem>

            {/* Key Metrics */}
            <BentoItem colSpan={4}>
              <Stack spacing={2} height="100%">
                <MetricCard
                  title="Total Value"
                  value={`£${liveMetrics.totalValue.toLocaleString()}`}
                  change={1.2}
                  icon={TrendingUp}
                  color="primary"
                />
                <MetricCard
                  title="Today P&L"
                  value={`£${liveMetrics.todayPnL}`}
                  change={0.8}
                  icon={DollarSign}
                  color="success"
                />
                <MetricCard
                  title="Cash Balance"
                  value={`£${liveMetrics.cashBalance.toLocaleString()}`}
                  icon={Users}
                  color="neutral"
                />
              </Stack>
            </BentoItem>

            {/* AI Performance */}
            <BentoItem colSpan={6} minHeight="300px">
              <Card variant="outlined" sx={{ height: '100%', p: 3 }}>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                  <Brain size={24} />
                  <Box>
                    <Typography level="h4">AI Performance</Typography>
                    <Typography level="body-sm" color="neutral">
                      Model metrics and confidence
                    </Typography>
                  </Box>
                </Stack>

                <Stack spacing={3}>
                  {aiMetrics.map((metric) => (
                    <Box key={metric.metric}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                        <Typography level="body-sm">{metric.metric}</Typography>
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <Typography level="body-sm" fontFamily="code" fontWeight="medium">
                            {metric.value}%
                          </Typography>
                          <Typography
                            level="body-xs"
                            color={metric.trend >= 0 ? 'success' : 'danger'}
                            fontFamily="code"
                          >
                            {metric.trend >= 0 ? '+' : ''}{metric.trend}
                          </Typography>
                        </Stack>
                      </Stack>
                      <LinearProgress
                        determinate
                        value={metric.value}
                        color={metric.value >= 85 ? 'success' : metric.value >= 70 ? 'warning' : 'danger'}
                        sx={{ height: 6 }}
                      />
                    </Box>
                  ))}
                </Stack>
              </Card>
            </BentoItem>

            {/* Risk Monitor */}
            <BentoItem colSpan={6} minHeight="300px">
              <Card variant="outlined" sx={{ height: '100%', p: 3 }}>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                  <Shield size={24} />
                  <Box>
                    <Typography level="h4">Risk Monitor</Typography>
                    <Typography level="body-sm" color="neutral">
                      Real-time risk assessment
                    </Typography>
                  </Box>
                </Stack>

                <Grid container spacing={2}>
                  <Grid xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography level="body-xs" color="neutral">VaR 95%</Typography>
                      <Typography level="h4" fontFamily="code" color="danger">
                        £{riskMetrics.var95}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography level="body-xs" color="neutral">Max Drawdown</Typography>
                      <Typography level="h4" fontFamily="code" color="warning">
                        {riskMetrics.maxDrawdown}%
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography level="body-xs" color="neutral">Sharpe Ratio</Typography>
                      <Typography level="h4" fontFamily="code" color="success">
                        {riskMetrics.sharpe}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography level="body-xs" color="neutral">Beta</Typography>
                      <Typography level="h4" fontFamily="code">
                        {riskMetrics.beta}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Typography level="body-sm">Portfolio Volatility</Typography>
                  <Typography level="body-sm" fontFamily="code" fontWeight="medium">
                    {riskMetrics.volatility}%
                  </Typography>
                </Stack>
              </Card>
            </BentoItem>

            {/* Current Positions */}
            <BentoItem colSpan={12} minHeight="400px">
              <Card variant="outlined" sx={{ height: '100%', p: 0 }}>
                <Box sx={{ p: 3, pb: 2 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography level="h4">Current Positions</Typography>
                      <Typography level="body-sm" color="neutral">
                        Active holdings across all wrappers
                      </Typography>
                    </Box>
                    <Button variant="soft" startDecorator={<Settings size={16} />} size="sm">
                      Manage
                    </Button>
                  </Stack>
                </Box>

                <Divider />

                {/* Position Headers */}
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 80px 100px 80px 120px 60px',
                    py: 1.5,
                    px: 2,
                    backgroundColor: 'background.level1',
                  }}
                >
                  <Typography level="body-sm" fontWeight="medium" color="neutral">
                    Symbol / Wrapper
                  </Typography>
                  <Typography level="body-sm" fontWeight="medium" color="neutral" textAlign="right">
                    Qty
                  </Typography>
                  <Typography level="body-sm" fontWeight="medium" color="neutral" textAlign="right">
                    Price
                  </Typography>
                  <Typography level="body-sm" fontWeight="medium" color="neutral" textAlign="right">
                    Change
                  </Typography>
                  <Typography level="body-sm" fontWeight="medium" color="neutral" textAlign="right">
                    Value
                  </Typography>
                  <Box />
                </Box>

                <Divider />

                {/* Position Rows */}
                {positions.map((position, index) => (
                  <React.Fragment key={position.symbol}>
                    <PositionRow position={position} />
                    {index < positions.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </Card>
            </BentoItem>
          </BentoGrid>
        </Box>
      </Box>
    </CssVarsProvider>
  );
}