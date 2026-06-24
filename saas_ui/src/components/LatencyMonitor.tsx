/**
 * Nova Trading - Ultra-Low Latency Data Pipeline Monitor
 * Real-time latency tracking and optimization for high-frequency trading
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Stack,
  Chip,
  Avatar,
  LinearProgress,
  Alert,
  Button,
  IconButton,
  Switch,
} from '@mui/joy';
import {
  Zap,
  Activity,
  Wifi,
  Server,
  Timer,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Settings,
  Cpu,
  Network,
  HardDrive,
} from 'lucide-react';

interface LatencyMetrics {
  marketData: number;
  orderExecution: number;
  networkRTT: number;
  cpuLatency: number;
  memoryLatency: number;
  diskLatency: number;
  totalPipeline: number;
}

interface OptimizationSetting {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  impact: string;
  risk: 'low' | 'medium' | 'high';
}

const mockLatency: LatencyMetrics = {
  marketData: 0.12,
  orderExecution: 0.08,
  networkRTT: 0.15,
  cpuLatency: 0.02,
  memoryLatency: 0.01,
  diskLatency: 0.05,
  totalPipeline: 0.43
};

const optimizationSettings: OptimizationSetting[] = [
  {
    id: 'kernel_bypass',
    name: 'Kernel Bypass Networking',
    description: 'Direct hardware access bypassing OS network stack',
    enabled: true,
    impact: '-60% network latency',
    risk: 'high'
  },
  {
    id: 'cpu_affinity',
    name: 'CPU Core Affinity',
    description: 'Pin critical threads to dedicated CPU cores',
    enabled: true,
    impact: '-30% CPU jitter',
    risk: 'low'
  },
  {
    id: 'memory_lock',
    name: 'Memory Page Locking',
    description: 'Lock trading data in physical RAM',
    enabled: true,
    impact: '-90% memory swap latency',
    risk: 'medium'
  },
  {
    id: 'tick_batching',
    name: 'Tick Data Batching',
    description: 'Batch process market data for efficiency',
    enabled: false,
    impact: '+25% throughput, +2ms latency',
    risk: 'low'
  },
  {
    id: 'hw_timestamping',
    name: 'Hardware Timestamping',
    description: 'NIC-level packet timestamping',
    enabled: true,
    impact: '-95% timestamp uncertainty',
    risk: 'low'
  }
];

function LatencyBar({ label, value, target, unit = 'ms' }: {
  label: string;
  value: number;
  target: number;
  unit?: string;
}) {
  const percentage = (value / target) * 100;
  const color = value <= target * 0.5 ? 'success' : value <= target ? 'warning' : 'danger';

  return (
    <Box sx={{ mb: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
        <Typography level="body-sm">{label}</Typography>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography level="body-xs" color={color} fontFamily="mono">
            {value.toFixed(2)}{unit}
          </Typography>
          <Typography level="body-xs" color="neutral">
            / {target.toFixed(2)}{unit}
          </Typography>
        </Stack>
      </Stack>
      <LinearProgress
        determinate
        value={Math.min(percentage, 100)}
        color={color}
        sx={{ height: 6 }}
      />
    </Box>
  );
}

export default function LatencyMonitor() {
  const [latency, setLatency] = useState<LatencyMetrics>(mockLatency);
  const [optimizations, setOptimizations] = useState(optimizationSettings);
  const [isOptimizing, setIsOptimizing] = useState(false);

  // Simulate real-time latency updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLatency(prev => ({
        marketData: prev.marketData + (Math.random() - 0.5) * 0.02,
        orderExecution: prev.orderExecution + (Math.random() - 0.5) * 0.01,
        networkRTT: prev.networkRTT + (Math.random() - 0.5) * 0.05,
        cpuLatency: prev.cpuLatency + (Math.random() - 0.5) * 0.005,
        memoryLatency: prev.memoryLatency + (Math.random() - 0.5) * 0.002,
        diskLatency: prev.diskLatency + (Math.random() - 0.5) * 0.01,
        totalPipeline: 0.43 + (Math.random() - 0.5) * 0.1
      }));
    }, 100); // Update every 100ms for real-time feel

    return () => clearInterval(interval);
  }, []);

  const toggleOptimization = (id: string) => {
    setOptimizations(prev => prev.map(opt =>
      opt.id === id ? { ...opt, enabled: !opt.enabled } : opt
    ));
  };

  const runOptimization = async () => {
    setIsOptimizing(true);
    // Simulate optimization process
    setTimeout(() => {
      setLatency(prev => ({
        ...prev,
        totalPipeline: prev.totalPipeline * 0.7 // 30% improvement
      }));
      setIsOptimizing(false);
    }, 3000);
  };

  const getTotalLatencyColor = () => {
    if (latency.totalPipeline <= 0.5) return 'success';
    if (latency.totalPipeline <= 1.0) return 'warning';
    return 'danger';
  };

  const enabledOptimizations = optimizations.filter(opt => opt.enabled).length;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography level="h3">Latency Monitor</Typography>
          <Typography level="body-sm" color="neutral">
            Ultra-low latency trading pipeline optimization
          </Typography>
        </Box>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Chip
            variant="soft"
            color={getTotalLatencyColor()}
            startDecorator={<Zap size={14} />}
          >
            {latency.totalPipeline.toFixed(2)}ms Total
          </Chip>
        </Stack>
      </Stack>

      {/* Critical Performance Alert */}
      {latency.totalPipeline > 1.0 && (
        <Alert color="danger" sx={{ mb: 3 }} startDecorator={<AlertTriangle />}>
          <Box>
            <Typography level="body-sm" fontWeight="medium">
              High Latency Detected
            </Typography>
            <Typography level="body-xs">
              Total pipeline latency exceeds 1ms - this may impact high-frequency trading performance.
              Consider enabling additional optimizations below.
            </Typography>
          </Box>
        </Alert>
      )}

      {/* Real-Time Latency Metrics */}
      <Card variant="outlined" sx={{ mb: 3, p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Typography level="h4">Pipeline Latency Breakdown</Typography>
          <Stack direction="row" spacing={1}>
            <Avatar variant="soft" color="success" size="sm">
              <Activity size={14} />
            </Avatar>
            <Typography level="body-xs" color="success" fontFamily="mono">
              LIVE
            </Typography>
          </Stack>
        </Stack>

        <Stack spacing={2}>
          <LatencyBar label="Market Data Feed" value={latency.marketData} target={0.5} />
          <LatencyBar label="Order Execution" value={latency.orderExecution} target={0.2} />
          <LatencyBar label="Network Round-Trip" value={latency.networkRTT} target={0.3} />
          <LatencyBar label="CPU Processing" value={latency.cpuLatency} target={0.1} />
          <LatencyBar label="Memory Access" value={latency.memoryLatency} target={0.05} />
          <LatencyBar label="Disk I/O" value={latency.diskLatency} target={0.1} />

          <Box sx={{ pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <LatencyBar
              label="Total Pipeline Latency"
              value={latency.totalPipeline}
              target={1.0}
            />
          </Box>
        </Stack>
      </Card>

      {/* Performance Optimizations */}
      <Card variant="outlined" sx={{ mb: 3, p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Typography level="h4">Performance Optimizations</Typography>
          <Stack direction="row" alignItems="center" spacing={2}>
            <Typography level="body-xs" color="neutral">
              {enabledOptimizations}/{optimizations.length} enabled
            </Typography>
            <Button
              variant="outlined"
              size="sm"
              onClick={runOptimization}
              loading={isOptimizing}
              startDecorator={<Settings size={14} />}
            >
              {isOptimizing ? 'Optimizing...' : 'Apply Changes'}
            </Button>
          </Stack>
        </Stack>

        <Stack spacing={2}>
          {optimizations.map(opt => (
            <Box key={opt.id} sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 'sm' }}>
              <Stack direction="row" justifyContent="space-between" alignItems="start">
                <Box sx={{ flex: 1 }}>
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                    <Typography level="body-sm" fontWeight="medium">
                      {opt.name}
                    </Typography>
                    <Chip
                      variant="soft"
                      size="sm"
                      color={opt.risk === 'low' ? 'success' : opt.risk === 'medium' ? 'warning' : 'danger'}
                    >
                      {opt.risk.toUpperCase()} RISK
                    </Chip>
                  </Stack>
                  <Typography level="body-xs" color="neutral" sx={{ mb: 1 }}>
                    {opt.description}
                  </Typography>
                  <Typography level="body-xs" color="primary" fontWeight="medium">
                    Impact: {opt.impact}
                  </Typography>
                </Box>
                <Switch
                  checked={opt.enabled}
                  onChange={() => toggleOptimization(opt.id)}
                />
              </Stack>
            </Box>
          ))}
        </Stack>
      </Card>

      {/* System Recommendations */}
      <Card variant="outlined" sx={{ p: 3 }}>
        <Typography level="h4" sx={{ mb: 2 }}>Ultra-Low Latency Recommendations</Typography>
        <Stack spacing={2}>
          <Box sx={{ p: 2, bgcolor: 'background.level1', borderRadius: 'sm' }}>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Avatar variant="soft" color="warning" size="sm">
                <Cpu size={16} />
              </Avatar>
              <Box>
                <Typography level="body-sm" fontWeight="medium">
                  Hardware Upgrade
                </Typography>
                <Typography level="body-xs" color="neutral">
                  Consider Intel i9-13900K or AMD 7950X3D for sub-microsecond trading
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Box sx={{ p: 2, bgcolor: 'background.level1', borderRadius: 'sm' }}>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Avatar variant="soft" color="primary" size="sm">
                <Network size={16} />
              </Avatar>
              <Box>
                <Typography level="body-sm" fontWeight="medium">
                  Co-location Services
                </Typography>
                <Typography level="body-xs" color="neutral">
                  Deploy to Equinix NY4/LD5 for microsecond proximity to exchanges
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Box sx={{ p: 2, bgcolor: 'background.level1', borderRadius: 'sm' }}>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Avatar variant="soft" color="success" size="sm">
                <HardDrive size={16} />
              </Avatar>
              <Box>
                <Typography level="body-sm" fontWeight="medium">
                  Memory Configuration
                </Typography>
                <Typography level="body-xs" color="neutral">
                  32GB+ DDR5-6000 with ECC for zero-latency market data caching
                </Typography>
              </Box>
            </Stack>
          </Box>
        </Stack>
      </Card>
    </Box>
  );
}