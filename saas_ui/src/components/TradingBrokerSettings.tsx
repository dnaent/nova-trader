/**
 * Nova Trader - Trading Broker API Settings
 * Configuration interface for connecting to external trading APIs
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Input,
  Select,
  Option,
  Switch,
  FormControl,
  FormLabel,
  FormHelperText,
  Stack,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  Divider,
  Avatar,
  Sheet,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/joy';
import {
  Settings,
  Wifi,
  WifiOff,
  CheckCircle,
  AlertTriangle,
  Info,
  Eye,
  EyeOff,
  TestTube,
  Zap,
  Shield,
  Globe,
  Key,
  Server,
  ChevronDown,
} from 'lucide-react';

interface BrokerConfig {
  id: string;
  name: string;
  logo: string;
  status: 'connected' | 'disconnected' | 'error' | 'testing';
  apiEndpoint: string;
  apiKey: string;
  apiSecret: string;
  environment: 'paper' | 'live';
  autoConnect: boolean;
  enabled: boolean;
  features: string[];
  lastConnected?: Date;
  latency?: number;
}

const brokerConfigs: BrokerConfig[] = [
  {
    id: 'ibkr',
    name: 'Interactive Brokers (IBKR)',
    logo: '⚡',
    status: 'disconnected',
    apiEndpoint: 'localhost:7497',
    apiKey: '',
    apiSecret: '',
    environment: 'paper',
    autoConnect: false,
    enabled: true,
    features: ['Direct Market Access', 'Ultra-Low Latency', 'Level 2 Data', 'Options', 'Futures'],
    latency: 0.8
  },
  {
    id: 'alpaca',
    name: 'Alpaca Trading',
    logo: '🦙',
    status: 'disconnected',
    apiEndpoint: 'https://paper-api.alpaca.markets',
    apiKey: '',
    apiSecret: '',
    environment: 'paper',
    autoConnect: false,
    enabled: false,
    features: ['Stocks', 'ETFs', 'Crypto'],
    latency: 45
  },
  {
    id: 'td',
    name: 'TD Ameritrade',
    logo: '📈',
    status: 'disconnected',
    apiEndpoint: 'https://api.tdameritrade.com',
    apiKey: '',
    apiSecret: '',
    environment: 'paper',
    autoConnect: false,
    enabled: false,
    features: ['Stocks', 'Options', 'ETFs', 'Futures'],
    latency: 28
  },
];

function BrokerCard({ config, onUpdate, onTest, onConnect }: {
  config: BrokerConfig;
  onUpdate: (id: string, updates: Partial<BrokerConfig>) => void;
  onTest: (id: string) => void;
  onConnect: (id: string) => void;
}) {
  const [showCredentials, setShowCredentials] = useState(false);
  const [isExpanded, setIsExpanded] = useState(config.id === 'ibkr'); // IBKR expanded by default

  const getStatusColor = () => {
    switch (config.status) {
      case 'connected': return 'success';
      case 'error': return 'danger';
      case 'testing': return 'warning';
      default: return 'neutral';
    }
  };

  const getStatusIcon = () => {
    switch (config.status) {
      case 'connected': return <CheckCircle size={16} />;
      case 'error': return <AlertTriangle size={16} />;
      case 'testing': return <TestTube size={16} />;
      default: return <WifiOff size={16} />;
    }
  };

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <Accordion expanded={isExpanded} onChange={() => setIsExpanded(!isExpanded)}>
        <AccordionSummary>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ width: '100%', pr: 2 }}>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Avatar variant="soft" size="md">
                {config.logo}
              </Avatar>
              <Box>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Typography level="h4">{config.name}</Typography>
                  <Chip
                    variant="soft"
                    color={getStatusColor() as any}
                    size="sm"
                    startDecorator={getStatusIcon()}
                  >
                    {config.status.toUpperCase()}
                  </Chip>
                </Stack>
                <Typography level="body-sm" color="neutral">
                  {config.features.join(' • ')}
                  {config.latency && ` • ${config.latency}ms latency`}
                </Typography>
              </Box>
            </Stack>
            <Switch
              checked={config.enabled}
              onChange={(e) => onUpdate(config.id, { enabled: e.target.checked })}
            />
          </Stack>
        </AccordionSummary>

        <AccordionDetails>
          <Stack spacing={3}>
            {/* Environment Selection */}
            <FormControl>
              <FormLabel>Trading Environment</FormLabel>
              <Select
                value={config.environment}
                onChange={(_, value) => onUpdate(config.id, { environment: value as 'paper' | 'live' })}
              >
                <Option value="paper">Paper Trading (Safe)</Option>
                <Option value="live">Live Trading (Real Money)</Option>
              </Select>
              <FormHelperText>
                {config.environment === 'paper'
                  ? '✅ Paper trading mode - no real money at risk'
                  : '⚠️ Live trading mode - real money will be used'}
              </FormHelperText>
            </FormControl>

            {/* API Endpoint */}
            <FormControl>
              <FormLabel>API Endpoint</FormLabel>
              <Input
                value={config.apiEndpoint}
                onChange={(e) => onUpdate(config.id, { apiEndpoint: e.target.value })}
                placeholder="localhost:7497 or https://api.broker.com"
                startDecorator={<Server size={16} />}
              />
              <FormHelperText>
                {config.id === 'ibkr'
                  ? 'TWS Gateway: 7496 (live), 7497 (paper)'
                  : 'Broker API base URL'}
              </FormHelperText>
            </FormControl>

            {/* API Credentials */}
            <Stack spacing={2}>
              <FormControl>
                <FormLabel>API Key / Client ID</FormLabel>
                <Input
                  type={showCredentials ? 'text' : 'password'}
                  value={config.apiKey}
                  onChange={(e) => onUpdate(config.id, { apiKey: e.target.value })}
                  placeholder="Your API key or client ID"
                  startDecorator={<Key size={16} />}
                  endDecorator={
                    <IconButton
                      variant="plain"
                      size="sm"
                      onClick={() => setShowCredentials(!showCredentials)}
                    >
                      {showCredentials ? <EyeOff size={14} /> : <Eye size={14} />}
                    </IconButton>
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>API Secret / Password</FormLabel>
                <Input
                  type={showCredentials ? 'text' : 'password'}
                  value={config.apiSecret}
                  onChange={(e) => onUpdate(config.id, { apiSecret: e.target.value })}
                  placeholder="Your API secret or password"
                  startDecorator={<Shield size={16} />}
                />
              </FormControl>
            </Stack>

            {/* Connection Settings */}
            <FormControl>
              <FormLabel>Auto-Connect on Startup</FormLabel>
              <Switch
                checked={config.autoConnect}
                onChange={(e) => onUpdate(config.id, { autoConnect: e.target.checked })}
                endDecorator={config.autoConnect ? "Enabled" : "Disabled"}
              />
              <FormHelperText>
                Automatically connect to this broker when Nova Trader starts
              </FormHelperText>
            </FormControl>

            {/* Action Buttons */}
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => onTest(config.id)}
                startDecorator={<TestTube size={16} />}
                disabled={!config.apiKey || config.status === 'testing'}
              >
                Test Connection
              </Button>
              <Button
                variant="solid"
                color={config.status === 'connected' ? 'danger' : 'success'}
                onClick={() => onConnect(config.id)}
                startDecorator={config.status === 'connected' ? <WifiOff size={16} /> : <Wifi size={16} />}
                disabled={!config.apiKey || config.status === 'testing'}
              >
                {config.status === 'connected' ? 'Disconnect' : 'Connect'}
              </Button>
            </Stack>

            {/* Status Information */}
            {config.status === 'connected' && config.lastConnected && (
              <Alert color="success" startDecorator={<CheckCircle />}>
                Connected successfully at {config.lastConnected.toLocaleTimeString()}
              </Alert>
            )}

            {config.status === 'error' && (
              <Alert color="danger" startDecorator={<AlertTriangle />}>
                Connection failed. Please check your credentials and API endpoint.
              </Alert>
            )}
          </Stack>
        </AccordionDetails>
      </Accordion>
    </Card>
  );
}

export default function TradingBrokerSettings() {
  const [configs, setConfigs] = useState<BrokerConfig[]>(brokerConfigs);
  const [testingBroker, setTestingBroker] = useState<string | null>(null);

  const updateConfig = (id: string, updates: Partial<BrokerConfig>) => {
    setConfigs(prev => prev.map(config =>
      config.id === id ? { ...config, ...updates } : config
    ));
  };

  const testConnection = async (brokerId: string) => {
    setTestingBroker(brokerId);
    updateConfig(brokerId, { status: 'testing' });

    // Simulate connection test
    setTimeout(() => {
      const success = Math.random() > 0.3; // 70% success rate for demo
      updateConfig(brokerId, {
        status: success ? 'connected' : 'error',
        lastConnected: success ? new Date() : undefined
      });
      setTestingBroker(null);
    }, 2000);
  };

  const toggleConnection = (brokerId: string) => {
    const config = configs.find(c => c.id === brokerId);
    if (config?.status === 'connected') {
      updateConfig(brokerId, { status: 'disconnected' });
    } else {
      testConnection(brokerId);
    }
  };

  const connectedBrokers = configs.filter(c => c.status === 'connected').length;
  const enabledBrokers = configs.filter(c => c.enabled).length;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography level="h3">Trading Broker Settings</Typography>
          <Typography level="body-sm" color="neutral">
            Configure connections to external trading APIs
          </Typography>
        </Box>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Chip variant="soft" color="success">
            {connectedBrokers} Connected
          </Chip>
          <Chip variant="soft" color="primary">
            {enabledBrokers} Enabled
          </Chip>
        </Stack>
      </Stack>

      {/* Connection Status Overview */}
      <Card variant="outlined" sx={{ mb: 3, p: 2 }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Avatar variant="soft" color="primary" size="md">
            <Settings size={20} />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography level="body-sm" fontWeight="medium">
              Broker API Status
            </Typography>
            <Typography level="body-xs" color="neutral">
              {connectedBrokers > 0
                ? `${connectedBrokers} broker(s) connected and ready for trading`
                : 'No brokers connected - configure below to start trading'
              }
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography level="h4" color={connectedBrokers > 0 ? 'success' : 'warning'}>
              {connectedBrokers > 0 ? 'READY' : 'SETUP REQUIRED'}
            </Typography>
          </Box>
        </Stack>
      </Card>

      {/* Important Security Notice */}
      <Alert color="warning" sx={{ mb: 3 }} startDecorator={<Shield />}>
        <Box>
          <Typography level="body-sm" fontWeight="medium">
            Security Notice
          </Typography>
          <Typography level="body-xs">
            API credentials are stored locally and encrypted. Always use paper trading mode for testing.
            Never share your API keys or run in live mode without proper risk management.
          </Typography>
        </Box>
      </Alert>

      {/* Broker Configuration Cards */}
      <Stack spacing={2}>
        {configs.map(config => (
          <BrokerCard
            key={config.id}
            config={config}
            onUpdate={updateConfig}
            onTest={testConnection}
            onConnect={toggleConnection}
          />
        ))}
      </Stack>

      {/* Add New Broker */}
      <Card variant="outlined" sx={{ mt: 3, p: 3, textAlign: 'center', borderStyle: 'dashed' }}>
        <Stack spacing={2} alignItems="center">
          <Avatar variant="soft" color="neutral" size="lg">
            <Globe size={24} />
          </Avatar>
          <Box>
            <Typography level="body-sm" fontWeight="medium">
              Need another broker?
            </Typography>
            <Typography level="body-xs" color="neutral">
              Contact support to request additional broker integrations
            </Typography>
          </Box>
          <Button variant="outlined" size="sm">
            Request Integration
          </Button>
        </Stack>
      </Card>
    </Box>
  );
}