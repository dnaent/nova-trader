/**
 * Nova Trader - Modern Trading Dashboard
 * Complete infrastructure with MUI, Bento Grid, AI Copilot, and Light/Dark Mode
 */
import React, { useState, useEffect } from 'react';
import {
  CssVarsProvider,
  useColorScheme,
  Box,
  Card,
  CardContent,
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
} from '@mui/joy';
import {
  Moon,
  Sun,
  Activity,
  TrendingUp,
  Brain,
  Shield,
  Zap,
  Settings,
  BarChart3,
  Globe,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  PieChart,
} from 'lucide-react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar,
  ComposedChart,
} from 'recharts';
import theme from '../theme/theme';
import { BentoGrid, BentoItem } from './layout/BentoGrid';
import AICopilot from './AICopilot';
import TradingBrokerSettings from './TradingBrokerSettings';
import LatencyMonitor from './LatencyMonitor';

// Enhanced mock data for infrastructure demo
const portfolioData = [
  { time: '09:30', price: 122500, volume: 1200, ma20: 121800, benchmark: 121500 },
  { time: '10:00', price: 123100, volume: 1450, ma20: 121950, benchmark: 122000 },
  { time: '10:30', price: 122800, volume: 980, ma20: 122100, benchmark: 122200 },
  { time: '11:00', price: 124200, volume: 1680, ma20: 122300, benchmark: 122800 },
  { time: '11:30', price: 123950, volume: 1320, ma20: 122500, benchmark: 123000 },
  { time: '12:00', price: 125100, volume: 2100, ma20: 122750, benchmark: 123500 },
];

const positions = [
  { symbol: 'NVDA', qty: 15, price: 950.10, change: 2.3, value: 14251.50, book: 'GIA', sector: 'Technology' },
  { symbol: 'VWRL', qty: 50, price: 112.50, change: 0.8, value: 5625.00, book: 'ISA', sector: 'Global ETF' },
  { symbol: 'SPY', qty: 20, price: 505.20, change: 1.2, value: 10104.00, book: 'SIPP', sector: 'US Market' },
  { symbol: 'TSLA', qty: 8, price: 245.80, change: -1.5, value: 1966.40, book: 'GIA', sector: 'Technology' },
  { symbol: 'MSFT', qty: 12, price: 385.60, change: 0.9, value: 4627.20, book: 'ISA', sector: 'Technology' },
];

const aiMetrics = [
  { metric: 'Prediction Accuracy', value: 87.3, trend: 2.1, target: 90 },
  { metric: 'Risk Assessment', value: 92.1, trend: -0.8, target: 95 },
  { metric: 'Signal Quality', value: 84.7, trend: 3.4, target: 88 },
  { metric: 'Market Regime Detection', value: 78.9, trend: 1.2, target: 85 },
];

const riskMetrics = {
  var95: 2450,
  maxDrawdown: 8.3,
  sharpe: 1.42,
  beta: 0.73,
  correlation: 0.45,
  volatility: 18.2,
  calmar: 0.74,
  sortino: 1.89,
};

const engineConfig = {
  gateMin: 40,
  execThreshold: 75,
  aggressiveLiquidation: false,
  topN: 10,
  universe: ['SPY', 'NVDA', 'VWRL', 'TSLA', 'MSFT'],
};

// Color scheme toggle component
function ColorSchemeToggle() {
  const { mode, setMode } = useColorScheme();

  return (
    <IconButton
      onClick={() => setMode(mode === 'light' ? 'dark' : 'light')}
      variant="outlined"
      size="sm"
      sx={{ borderRadius: 'xl' }}
    >
      {mode === 'light' ? <Moon /> : <Sun />}
    </IconButton>
  );
}

// Enhanced metric card component
function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  color = 'neutral',
  subtitle,
}: {
  title: string;
  value: string | number;
  change?: number;
  icon: any;
  color?: 'primary' | 'success' | 'danger' | 'warning' | 'neutral';
  subtitle?: string;
}) {
  return (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="start">
          <Box sx={{ flex: 1 }}>
            <Typography level="body-sm" color="neutral">
              {title}
            </Typography>
            <Typography level="h3" fontFamily="code" sx={{ mt: 0.5, mb: subtitle ? 0.5 : 1 }}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            {subtitle && (
              <Typography level="body-xs" color="neutral">
                {subtitle}
              </Typography>
            )}
            {change !== undefined && (
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1 }}>
                {change >= 0 ? (
                  <ArrowUpRight size={16} color="var(--joy-palette-success-500)" />
                ) : (
                  <ArrowDownRight size={16} color="var(--joy-palette-danger-500)" />
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
      </CardContent>
    </Card>
  );
}

// Enhanced position row component
function PositionRow({ position }: { position: typeof positions[0] }) {
  const isProfit = position.change >= 0;

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: '1fr 80px 100px 80px 120px 80px 60px',
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
        <Stack direction="row" spacing={1} alignItems="center">
          <Chip variant="soft" size="sm" color="neutral">
            {position.book}
          </Chip>
          <Typography level="body-xs" color="neutral">
            {position.sector}
          </Typography>
        </Stack>
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
      <Chip
        variant="soft"
        size="sm"
        color={isProfit ? 'success' : 'danger'}
      >
        {isProfit ? 'PROFIT' : 'LOSS'}
      </Chip>
      <IconButton variant="plain" size="sm">
        <ChevronRight size={16} />
      </IconButton>
    </Box>
  );
}

export default function Dashboard() {
  // State management for dashboard
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'brokers' | 'latency' | 'engine' | 'ai' | 'risk' | 'forex'>('overview');

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
    activePositions: positions.length,
    totalReturn: 7.8,
  });

  // Engine configuration state
  const [config, setConfig] = useState(engineConfig);

  // Simulate live updates for infrastructure demo
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveMetrics(prev => ({
        ...prev,
        totalValue: prev.totalValue + (Math.random() - 0.5) * 100,
        todayPnL: prev.todayPnL + (Math.random() - 0.5) * 50,
        unrealizedPnL: prev.unrealizedPnL + (Math.random() - 0.5) * 75,
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
        {/* Enhanced Top Navigation */}
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
            {/* Left side - Branding and Status */}
            <Stack direction="row" alignItems="center" spacing={3}>
              <Typography level="h3" fontWeight="bold" color="primary">
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
                    {engineStatus.active ? 'ENGINE ACTIVE' : 'ENGINE OFFLINE'}
                  </Typography>
                </Stack>
              </Badge>

              <Stack direction="row" spacing={3}>
                <Box>
                  <Typography level="body-xs" color="neutral">AI Confidence</Typography>
                  <Typography level="body-sm" fontFamily="code" color="primary">
                    {engineStatus.confidence.toFixed(1)}%
                  </Typography>
                </Box>
                <Box>
                  <Typography level="body-xs" color="neutral">Risk Level</Typography>
                  <Typography level="body-sm" fontFamily="code" color={engineStatus.riskLevel === 'LOW' ? 'success' : 'warning'}>
                    {engineStatus.riskLevel}
                  </Typography>
                </Box>
              </Stack>
            </Stack>

            {/* Right side - Metrics and Controls */}
            <Stack direction="row" alignItems="center" spacing={3}>
              <Stack direction="row" spacing={2}>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography level="body-xs" color="neutral">Portfolio Value</Typography>
                  <Typography level="body-sm" fontFamily="code" fontWeight="medium">
                    £{liveMetrics.totalValue.toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography level="body-xs" color="neutral">Today P&L</Typography>
                  <Typography
                    level="body-sm"
                    color={liveMetrics.todayPnL >= 0 ? 'success' : 'danger'}
                    fontFamily="code"
                    fontWeight="medium"
                  >
                    {liveMetrics.todayPnL >= 0 ? '+' : ''}£{liveMetrics.todayPnL}
                  </Typography>
                </Box>
              </Stack>

              <ColorSchemeToggle />

              <Avatar size="sm" variant="soft" color="primary">
                PH
              </Avatar>
            </Stack>
          </Box>

          {/* Navigation Tabs */}
          <Divider />
          <Box sx={{ px: 3, py: 1 }}>
            <Stack direction="row" spacing={1}>
              {[
                { key: 'overview', label: 'Overview', icon: Activity },
                { key: 'analytics', label: 'Analytics', icon: BarChart3 },
                { key: 'brokers', label: 'Broker APIs', icon: Settings },
                { key: 'latency', label: 'Latency Monitor', icon: Zap },
                { key: 'ai', label: 'AI Performance', icon: Brain },
                { key: 'risk', label: 'Risk Monitor', icon: Shield },
                { key: 'engine', label: 'Engine Config', icon: Settings },
                { key: 'forex', label: 'Forex Hub', icon: Globe },
              ].map(({ key, label, icon: Icon }) => (
                <Button
                  key={key}
                  variant={activeTab === key ? 'solid' : 'plain'}
                  size="sm"
                  startDecorator={<Icon size={16} />}
                  onClick={() => setActiveTab(key as any)}
                  sx={{ textTransform: 'none' }}
                >
                  {label}
                </Button>
              ))}
            </Stack>
          </Box>
        </Sheet>

        {/* Main Dashboard Content with Bento Grid */}
        <Box sx={{ p: 3 }}>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <BentoGrid columns={12} gap={3}>
              {/* Portfolio Performance Chart - Large */}
              <BentoItem colSpan={8} minHeight="400px">
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent sx={{ height: '100%' }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
                      <Box>
                        <Typography level="h4">Portfolio Performance</Typography>
                        <Typography level="body-sm" color="neutral">
                          Real-time NAV tracking vs benchmark
                        </Typography>
                      </Box>
                      <Stack direction="row" spacing={1}>
                        <Button variant="soft" size="sm">1D</Button>
                        <Button variant="outlined" size="sm">1W</Button>
                        <Button variant="outlined" size="sm">1M</Button>
                        <Button variant="outlined" size="sm">1Y</Button>
                      </Stack>
                    </Stack>

                    <Box sx={{ height: '300px' }}>
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
                            dataKey="benchmark"
                            stroke="var(--joy-palette-neutral-400)"
                            strokeWidth={1}
                            strokeDasharray="5 5"
                            dot={false}
                          />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </BentoItem>

              {/* Key Metrics Cards */}
              <BentoItem colSpan={4}>
                <Stack spacing={2} height="100%">
                  <MetricCard
                    title="Total Portfolio Value"
                    value={`£${liveMetrics.totalValue.toLocaleString()}`}
                    change={liveMetrics.totalReturn}
                    icon={TrendingUp}
                    color="primary"
                    subtitle="Across all wrappers"
                  />
                  <MetricCard
                    title="Today's P&L"
                    value={`£${liveMetrics.todayPnL}`}
                    change={0.8}
                    icon={DollarSign}
                    color={liveMetrics.todayPnL >= 0 ? 'success' : 'danger'}
                  />
                  <MetricCard
                    title="Active Positions"
                    value={liveMetrics.activePositions}
                    icon={PieChart}
                    color="neutral"
                    subtitle={`£${liveMetrics.cashBalance.toLocaleString()} cash`}
                  />
                </Stack>
              </BentoItem>

              {/* AI Performance Metrics */}
              <BentoItem colSpan={6} minHeight="300px">
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                      <Brain size={24} color="var(--joy-palette-primary-500)" />
                      <Box>
                        <Typography level="h4">AI Performance Metrics</Typography>
                        <Typography level="body-sm" color="neutral">
                          Model confidence and accuracy
                        </Typography>
                      </Box>
                    </Stack>

                    <Stack spacing={3}>
                      {aiMetrics.map((metric) => (
                        <Box key={metric.metric}>
                          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                            <Typography level="body-sm">{metric.metric}</Typography>
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <Typography level="body-sm" fontFamily="code" fontWeight="medium">
                                {metric.value}% / {metric.target}%
                              </Typography>
                              <Typography
                                level="body-xs"
                                color={metric.trend >= 0 ? 'success' : 'danger'}
                                fontFamily="code"
                              >
                                {metric.trend >= 0 ? '+' : ''}{metric.trend}%
                              </Typography>
                            </Stack>
                          </Stack>
                          <LinearProgress
                            determinate
                            value={(metric.value / metric.target) * 100}
                            color={metric.value >= metric.target * 0.9 ? 'success' : metric.value >= metric.target * 0.7 ? 'warning' : 'danger'}
                            sx={{ height: 6 }}
                          />
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </BentoItem>

              {/* Risk Monitor */}
              <BentoItem colSpan={6} minHeight="300px">
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                      <Shield size={24} color="var(--joy-palette-success-500)" />
                      <Box>
                        <Typography level="h4">Risk Monitor</Typography>
                        <Typography level="body-sm" color="neutral">
                          Portfolio risk metrics
                        </Typography>
                      </Box>
                    </Stack>

                    <Grid container spacing={2}>
                      <Grid xs={6}>
                        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.level1', borderRadius: 'md' }}>
                          <Typography level="body-xs" color="neutral">VaR 95%</Typography>
                          <Typography level="h4" fontFamily="code" color="danger">
                            £{riskMetrics.var95}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid xs={6}>
                        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.level1', borderRadius: 'md' }}>
                          <Typography level="body-xs" color="neutral">Max Drawdown</Typography>
                          <Typography level="h4" fontFamily="code" color="warning">
                            {riskMetrics.maxDrawdown}%
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid xs={6}>
                        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.level1', borderRadius: 'md' }}>
                          <Typography level="body-xs" color="neutral">Sharpe Ratio</Typography>
                          <Typography level="h4" fontFamily="code" color="success">
                            {riskMetrics.sharpe}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid xs={6}>
                        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.level1', borderRadius: 'md' }}>
                          <Typography level="body-xs" color="neutral">Portfolio Beta</Typography>
                          <Typography level="h4" fontFamily="code">
                            {riskMetrics.beta}
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    <Divider sx={{ my: 2 }} />

                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography level="body-sm">Portfolio Volatility</Typography>
                      <Typography level="body-sm" fontFamily="code" fontWeight="medium">
                        {riskMetrics.volatility}%
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              </BentoItem>

              {/* Current Positions Table */}
              <BentoItem colSpan={12} minHeight="400px">
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent sx={{ p: 0 }}>
                    <Box sx={{ p: 3, pb: 2 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography level="h4">Current Holdings</Typography>
                          <Typography level="body-sm" color="neutral">
                            Active positions across all wrappers
                          </Typography>
                        </Box>
                        <Button variant="soft" startDecorator={<Settings size={16} />} size="sm">
                          Manage Portfolio
                        </Button>
                      </Stack>
                    </Box>

                    <Divider />

                    {/* Table Headers */}
                    <Box
                      sx={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 80px 100px 80px 120px 80px 60px',
                        py: 1.5,
                        px: 2,
                        backgroundColor: 'background.level1',
                      }}
                    >
                      <Typography level="body-sm" fontWeight="medium" color="neutral">
                        Asset / Wrapper
                      </Typography>
                      <Typography level="body-sm" fontWeight="medium" color="neutral" textAlign="right">
                        Quantity
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
                      <Typography level="body-sm" fontWeight="medium" color="neutral" textAlign="right">
                        Status
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
                  </CardContent>
                </Card>
              </BentoItem>
            </BentoGrid>
          )}

          {/* Trading Broker Settings Tab */}
          {activeTab === 'brokers' && <TradingBrokerSettings />}

          {/* Latency Monitor Tab */}
          {activeTab === 'latency' && <LatencyMonitor />}

          {/* Other tabs placeholder */}
          {!['overview', 'brokers', 'latency'].includes(activeTab) && (
            <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
              <Typography level="h4" sx={{ mb: 2 }}>
                {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Tab
              </Typography>
              <Typography level="body-sm" color="neutral">
                Infrastructure ready for {activeTab} dashboard implementation
              </Typography>
              <Typography level="body-xs" color="neutral" sx={{ mt: 1 }}>
                MUI components, Bento Grid layout, and theming system available
              </Typography>
            </Card>
          )}
        </Box>

        {/* AI Copilot Integration */}
        {copilotState.isVisible && (
          <Box
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000,
            }}
          >
            <AICopilot
              isMinimized={copilotState.isMinimized}
              onToggleMinimize={() =>
                setCopilotState(prev => ({ ...prev, isMinimized: !prev.isMinimized }))
              }
              onClose={() => setCopilotState(prev => ({ ...prev, isVisible: false }))}
            />
          </Box>
        )}
      </Box>
    </CssVarsProvider>
  );
}