/**
 * Nova Trader - Advanced Risk Management Dashboard
 * Real-time risk monitoring, correlation analysis, and portfolio protection
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Stack,
  Chip,
  IconButton,
  Avatar,
  LinearProgress,
  Alert,
  Switch,
  FormControl,
  FormLabel,
  Input,
  Divider,
  Table,
  Slider,
} from '@mui/joy';
import {
  Shield,
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  Target,
  Activity,
  Zap,
  BarChart3,
  PieChart,
  Settings,
  Bell,
  CheckCircle,
  X,
  Pause,
  Play,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';

interface RiskMetrics {
  portfolioValue: number;
  dailyPnL: number;
  var95: number;
  var99: number;
  maxDrawdown: number;
  currentDrawdown: number;
  sharpeRatio: number;
  volatility: number;
  beta: number;
  correlation: number;
  leverage: number;
}

interface RiskLimit {
  id: string;
  name: string;
  type: 'ABSOLUTE' | 'PERCENTAGE' | 'VaR';
  currentValue: number;
  limit: number;
  breached: boolean;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  enabled: boolean;
}

interface CorrelationData {
  symbol: string;
  correlation: number;
  exposure: number;
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
}

const mockRiskMetrics: RiskMetrics = {
  portfolioValue: 125000,
  dailyPnL: 1250,
  var95: 2450,
  var99: 3750,
  maxDrawdown: 8.3,
  currentDrawdown: 2.1,
  sharpeRatio: 1.42,
  volatility: 18.2,
  beta: 0.73,
  correlation: 0.45,
  leverage: 1.2
};

const mockRiskLimits: RiskLimit[] = [
  {
    id: 'daily_loss',
    name: 'Daily Loss Limit',
    type: 'ABSOLUTE',
    currentValue: -850,
    limit: -2000,
    breached: false,
    severity: 'MEDIUM',
    enabled: true
  },
  {
    id: 'max_drawdown',
    name: 'Maximum Drawdown',
    type: 'PERCENTAGE',
    currentValue: 2.1,
    limit: 5.0,
    breached: false,
    severity: 'HIGH',
    enabled: true
  },
  {
    id: 'concentration',
    name: 'Single Position Limit',
    type: 'PERCENTAGE',
    currentValue: 15.2,
    limit: 20.0,
    breached: false,
    severity: 'MEDIUM',
    enabled: true
  },
  {
    id: 'var_breach',
    name: 'VaR 95% Breach',
    type: 'VaR',
    currentValue: 1950,
    limit: 2500,
    breached: false,
    severity: 'HIGH',
    enabled: true
  },
  {
    id: 'leverage',
    name: 'Portfolio Leverage',
    type: 'ABSOLUTE',
    currentValue: 1.2,
    limit: 2.0,
    breached: false,
    severity: 'CRITICAL',
    enabled: true
  }
];

const mockCorrelationData: CorrelationData[] = [
  { symbol: 'NVDA', correlation: 0.85, exposure: 15.2, risk: 'HIGH' },
  { symbol: 'TSLA', correlation: 0.72, exposure: 8.5, risk: 'MEDIUM' },
  { symbol: 'MSFT', correlation: 0.45, exposure: 12.1, risk: 'LOW' },
  { symbol: 'SPY', correlation: 0.38, exposure: 25.0, risk: 'LOW' },
  { symbol: 'VWRL', correlation: 0.22, exposure: 18.3, risk: 'LOW' }
];

const drawdownData = [
  { time: '09:30', drawdown: 0.5 },
  { time: '10:00', drawdown: 1.2 },
  { time: '10:30', drawdown: 0.8 },
  { time: '11:00', drawdown: 2.1 },
  { time: '11:30', drawdown: 1.5 },
  { time: '12:00', drawdown: 0.9 },
];

const sectorExposure = [
  { name: 'Technology', value: 45.2, color: '#8b5cf6' },
  { name: 'Healthcare', value: 15.8, color: '#10b981' },
  { name: 'Finance', value: 12.3, color: '#f59e0b' },
  { name: 'Consumer', value: 18.1, color: '#3b82f6' },
  { name: 'Energy', value: 8.6, color: '#ef4444' }
];

function RiskGauge({
  label,
  value,
  limit,
  unit = '',
  color = 'primary'
}: {
  label: string;
  value: number;
  limit: number;
  unit?: string;
  color?: 'primary' | 'success' | 'warning' | 'danger';
}) {
  const percentage = Math.abs(value / limit) * 100;
  const isBreached = Math.abs(value) > Math.abs(limit);

  return (
    <Card variant="outlined" sx={{ p: 2 }}>
      <Stack spacing={1}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography level="body-sm" color="neutral">
            {label}
          </Typography>
          <Chip
            size="sm"
            variant="soft"
            color={isBreached ? 'danger' : percentage > 80 ? 'warning' : 'success'}
          >
            {percentage.toFixed(1)}%
          </Chip>
        </Stack>

        <Typography level="h4" fontFamily="mono">
          {value > 0 && !label.includes('Loss') ? '+' : ''}{value.toFixed(2)}{unit}
        </Typography>

        <Box>
          <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
            <Typography level="body-xs" color="neutral">
              Current
            </Typography>
            <Typography level="body-xs" color="neutral">
              Limit: {limit.toFixed(2)}{unit}
            </Typography>
          </Stack>
          <LinearProgress
            determinate
            value={Math.min(percentage, 100)}
            color={isBreached ? 'danger' : percentage > 80 ? 'warning' : color}
            sx={{ height: 6 }}
          />
        </Box>
      </Stack>
    </Card>
  );
}

function RiskLimitRow({
  limit,
  onToggle,
  onUpdate
}: {
  limit: RiskLimit;
  onToggle: (id: string) => void;
  onUpdate: (id: string, newLimit: number) => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(limit.limit.toString());

  const getSeverityColor = () => {
    switch (limit.severity) {
      case 'LOW': return 'success';
      case 'MEDIUM': return 'warning';
      case 'HIGH': return 'danger';
      case 'CRITICAL': return 'danger';
    }
  };

  const isBreached = limit.type === 'ABSOLUTE'
    ? Math.abs(limit.currentValue) > Math.abs(limit.limit)
    : limit.currentValue > limit.limit;

  const handleSave = () => {
    onUpdate(limit.id, parseFloat(editValue));
    setIsEditing(false);
  };

  return (
    <tr>
      <td>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography level="body-sm" fontWeight="medium">
            {limit.name}
          </Typography>
          {isBreached && (
            <Chip size="sm" color="danger" startDecorator={<AlertTriangle size={12} />}>
              BREACH
            </Chip>
          )}
        </Stack>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          {limit.currentValue.toFixed(2)}
        </Typography>
      </td>
      <td>
        {isEditing ? (
          <Stack direction="row" spacing={1} alignItems="center">
            <Input
              size="sm"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              sx={{ width: 80 }}
            />
            <IconButton size="sm" color="success" onClick={handleSave}>
              <CheckCircle size={14} />
            </IconButton>
            <IconButton size="sm" color="neutral" onClick={() => setIsEditing(false)}>
              <X size={14} />
            </IconButton>
          </Stack>
        ) : (
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography level="body-sm" fontFamily="mono">
              {limit.limit.toFixed(2)}
            </Typography>
            <IconButton size="sm" onClick={() => setIsEditing(true)}>
              <Settings size={14} />
            </IconButton>
          </Stack>
        )}
      </td>
      <td>
        <Chip size="sm" variant="soft" color={getSeverityColor()}>
          {limit.severity}
        </Chip>
      </td>
      <td>
        <Switch
          checked={limit.enabled}
          onChange={() => onToggle(limit.id)}
          size="sm"
        />
      </td>
    </tr>
  );
}

export default function RiskManagement() {
  const [riskMetrics, setRiskMetrics] = useState(mockRiskMetrics);
  const [riskLimits, setRiskLimits] = useState(mockRiskLimits);
  const [emergencyStop, setEmergencyStop] = useState(false);
  const [autoRiskManagement, setAutoRiskManagement] = useState(true);

  // Simulate real-time risk updates
  useEffect(() => {
    const interval = setInterval(() => {
      setRiskMetrics(prev => ({
        ...prev,
        dailyPnL: prev.dailyPnL + (Math.random() - 0.5) * 50,
        currentDrawdown: Math.max(0, prev.currentDrawdown + (Math.random() - 0.5) * 0.5),
        var95: prev.var95 + (Math.random() - 0.5) * 100
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const toggleRiskLimit = (id: string) => {
    setRiskLimits(prev => prev.map(limit =>
      limit.id === id ? { ...limit, enabled: !limit.enabled } : limit
    ));
  };

  const updateRiskLimit = (id: string, newLimit: number) => {
    setRiskLimits(prev => prev.map(limit =>
      limit.id === id ? { ...limit, limit: newLimit } : limit
    ));
  };

  const activeBreach = riskLimits.some(limit =>
    limit.enabled && (
      limit.type === 'ABSOLUTE'
        ? Math.abs(limit.currentValue) > Math.abs(limit.limit)
        : limit.currentValue > limit.limit
    )
  );

  const criticalRisks = riskLimits.filter(limit =>
    limit.enabled && limit.severity === 'CRITICAL'
  ).length;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography level="h3">Risk Management</Typography>
          <Typography level="body-sm" color="neutral">
            Real-time portfolio risk monitoring and protection
          </Typography>
        </Box>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Chip
            variant="soft"
            color={activeBreach ? 'danger' : 'success'}
            startDecorator={activeBreach ? <AlertTriangle size={14} /> : <CheckCircle size={14} />}
          >
            {activeBreach ? 'RISK BREACH' : 'ALL CLEAR'}
          </Chip>
          <Button
            variant={emergencyStop ? 'solid' : 'outlined'}
            color="danger"
            onClick={() => setEmergencyStop(!emergencyStop)}
            startDecorator={emergencyStop ? <Pause size={16} /> : <Shield size={16} />}
          >
            {emergencyStop ? 'STOP ACTIVE' : 'Emergency Stop'}
          </Button>
        </Stack>
      </Stack>

      {/* Critical Breach Alert */}
      {activeBreach && (
        <Alert color="danger" sx={{ mb: 3 }} startDecorator={<AlertTriangle />}>
          <Box>
            <Typography level="body-sm" fontWeight="medium">
              Risk Limit Breach Detected
            </Typography>
            <Typography level="body-xs">
              One or more risk limits have been breached. Consider reducing positions immediately.
            </Typography>
          </Box>
        </Alert>
      )}

      {/* Real-time Risk Gauges */}
      <Stack spacing={3} sx={{ mb: 4 }}>
        <Typography level="h4">Real-time Risk Metrics</Typography>
        <Stack direction="row" spacing={2}>
          <Box sx={{ flex: 1 }}>
            <Stack direction="row" spacing={2}>
              <RiskGauge
                label="Daily P&L"
                value={riskMetrics.dailyPnL}
                limit={5000}
                unit=""
                color={riskMetrics.dailyPnL >= 0 ? 'success' : 'danger'}
              />
              <RiskGauge
                label="Current Drawdown"
                value={riskMetrics.currentDrawdown}
                limit={5.0}
                unit="%"
                color="warning"
              />
              <RiskGauge
                label="VaR 95%"
                value={riskMetrics.var95}
                limit={3000}
                unit=""
                color="primary"
              />
              <RiskGauge
                label="Portfolio Leverage"
                value={riskMetrics.leverage}
                limit={2.0}
                unit="x"
                color="warning"
              />
            </Stack>
          </Box>
        </Stack>
      </Stack>

      {/* Risk Charts */}
      <Stack direction="row" spacing={3} sx={{ mb: 4 }}>
        {/* Drawdown Chart */}
        <Card variant="outlined" sx={{ flex: 1, p: 3 }}>
          <Typography level="h4" sx={{ mb: 2 }}>Intraday Drawdown</Typography>
          <Box sx={{ height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={drawdownData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--joy-palette-background-surface)',
                    border: '1px solid var(--joy-palette-divider)',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke="var(--joy-palette-danger-500)"
                  fill="var(--joy-palette-danger-200)"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        </Card>

        {/* Sector Exposure */}
        <Card variant="outlined" sx={{ flex: 1, p: 3 }}>
          <Typography level="h4" sx={{ mb: 2 }}>Sector Exposure</Typography>
          <Box sx={{ height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  dataKey="value"
                  data={sectorExposure}
                  cx="50%"
                  cy="50%"
                  outerRadius={60}
                  label={({ name, value }: { name?: string; value?: number }) => `${name}: ${value}%`}
                >
                  {sectorExposure.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          </Box>
        </Card>
      </Stack>

      {/* Risk Limits Configuration */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <Box sx={{ p: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography level="h4">Risk Limits</Typography>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Typography level="body-sm">Auto Risk Management</Typography>
              <Switch
                checked={autoRiskManagement}
                onChange={(e) => setAutoRiskManagement(e.target.checked)}
              />
            </Stack>
          </Stack>

          <Table>
            <thead>
              <tr>
                <th>Risk Limit</th>
                <th>Current</th>
                <th>Limit</th>
                <th>Severity</th>
                <th>Enabled</th>
              </tr>
            </thead>
            <tbody>
              {riskLimits.map(limit => (
                <RiskLimitRow
                  key={limit.id}
                  limit={limit}
                  onToggle={toggleRiskLimit}
                  onUpdate={updateRiskLimit}
                />
              ))}
            </tbody>
          </Table>
        </Box>
      </Card>

      {/* Position Correlation Analysis */}
      <Card variant="outlined" sx={{ p: 3 }}>
        <Typography level="h4" sx={{ mb: 2 }}>Position Correlation Matrix</Typography>
        <Table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Correlation</th>
              <th>Exposure (%)</th>
              <th>Risk Level</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {mockCorrelationData.map(item => (
              <tr key={item.symbol}>
                <td>
                  <Typography level="body-sm" fontWeight="medium">
                    {item.symbol}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm" fontFamily="mono">
                    {item.correlation.toFixed(2)}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm" fontFamily="mono">
                    {item.exposure.toFixed(1)}%
                  </Typography>
                </td>
                <td>
                  <Chip
                    size="sm"
                    variant="soft"
                    color={item.risk === 'HIGH' ? 'danger' : item.risk === 'MEDIUM' ? 'warning' : 'success'}
                  >
                    {item.risk}
                  </Chip>
                </td>
                <td>
                  {item.risk === 'HIGH' && (
                    <Button size="sm" variant="outlined" color="warning">
                      Reduce Exposure
                    </Button>
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