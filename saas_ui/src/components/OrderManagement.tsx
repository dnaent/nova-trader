/**
 * Nova Trader - Order Management System
 * Ultra-fast order entry, execution, and management for professional trading
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Input,
  Select,
  Option,
  Stack,
  Chip,
  IconButton,
  Avatar,
  Sheet,
  Divider,
  Alert,
  Badge,
  LinearProgress,
  FormControl,
  FormLabel,
  Table,
  Slider,
} from '@mui/joy';
import {
  TrendingUp,
  TrendingDown,
  Square,
  Play,
  Pause,
  X,
  Clock,
  CheckCircle,
  AlertTriangle,
  Zap,
  Target,
  Shield,
  DollarSign,
  BarChart3,
  Activity,
  Timer,
  ArrowUpRight,
  ArrowDownRight,
  RotateCcw,
} from 'lucide-react';

interface Order {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  type: 'MARKET' | 'LIMIT' | 'STOP' | 'STOP_LIMIT';
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: 'PENDING' | 'WORKING' | 'FILLED' | 'CANCELLED' | 'REJECTED';
  timeInForce: 'DAY' | 'GTC' | 'IOC' | 'FOK';
  account: 'GIA' | 'ISA' | 'SIPP';
  filled: number;
  avgFillPrice?: number;
  timestamp: Date;
  latency?: number;
}

interface Position {
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  realizedPnL: number;
  account: string;
}

const mockOrders: Order[] = [
  {
    id: 'ORD001',
    symbol: 'NVDA',
    side: 'BUY',
    type: 'LIMIT',
    quantity: 10,
    price: 945.00,
    status: 'WORKING',
    timeInForce: 'DAY',
    account: 'GIA',
    filled: 0,
    timestamp: new Date(Date.now() - 300000),
    latency: 0.12
  },
  {
    id: 'ORD002',
    symbol: 'SPY',
    side: 'SELL',
    type: 'MARKET',
    quantity: 20,
    status: 'FILLED',
    timeInForce: 'DAY',
    account: 'ISA',
    filled: 20,
    avgFillPrice: 504.85,
    timestamp: new Date(Date.now() - 180000),
    latency: 0.08
  },
  {
    id: 'ORD003',
    symbol: 'TSLA',
    side: 'BUY',
    type: 'STOP_LIMIT',
    quantity: 5,
    price: 250.00,
    stopPrice: 248.00,
    status: 'PENDING',
    timeInForce: 'GTC',
    account: 'SIPP',
    filled: 0,
    timestamp: new Date(Date.now() - 120000),
    latency: 0.15
  }
];

const mockPositions: Position[] = [
  {
    symbol: 'NVDA',
    quantity: 15,
    avgPrice: 950.10,
    currentPrice: 955.25,
    unrealizedPnL: 77.25,
    realizedPnL: 0,
    account: 'GIA'
  },
  {
    symbol: 'SPY',
    quantity: 50,
    avgPrice: 502.20,
    currentPrice: 505.80,
    unrealizedPnL: 180.00,
    realizedPnL: 125.50,
    account: 'ISA'
  }
];

function QuickOrderEntry({ onSubmitOrder }: { onSubmitOrder: (order: any) => void }) {
  const [symbol, setSymbol] = useState('');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [type, setType] = useState<'MARKET' | 'LIMIT'>('MARKET');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [account, setAccount] = useState<'GIA' | 'ISA' | 'SIPP'>('GIA');
  const symbolInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Auto-focus symbol input for rapid trading
    if (symbolInputRef.current) {
      symbolInputRef.current.focus();
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol || !quantity) return;

    const order = {
      symbol: symbol.toUpperCase(),
      side,
      type,
      quantity: parseInt(quantity),
      price: type === 'LIMIT' ? parseFloat(price) : undefined,
      account,
      timeInForce: 'DAY' as const,
    };

    onSubmitOrder(order);

    // Reset form for next order
    setSymbol('');
    setQuantity('');
    setPrice('');
    if (symbolInputRef.current) {
      symbolInputRef.current.focus();
    }
  };

  return (
    <Card variant="outlined" sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography level="h4">Quick Order Entry</Typography>
        <Chip variant="soft" color="primary" startDecorator={<Zap size={14} />}>
          Ultra-Fast
        </Chip>
      </Stack>

      <form onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <Stack direction="row" spacing={2}>
            <FormControl sx={{ flex: 1 }}>
              <FormLabel>Symbol</FormLabel>
              <Input
                ref={symbolInputRef}
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="NVDA"
                required
                sx={{ textTransform: 'uppercase' }}
              />
            </FormControl>
            <FormControl>
              <FormLabel>Account</FormLabel>
              <Select value={account} onChange={(_, value) => setAccount(value as any)}>
                <Option value="GIA">GIA</Option>
                <Option value="ISA">ISA</Option>
                <Option value="SIPP">SIPP</Option>
              </Select>
            </FormControl>
          </Stack>

          <Stack direction="row" spacing={2}>
            <FormControl>
              <FormLabel>Side</FormLabel>
              <Select value={side} onChange={(_, value) => setSide(value as any)}>
                <Option value="BUY">
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <TrendingUp size={16} color="green" />
                    <span>BUY</span>
                  </Stack>
                </Option>
                <Option value="SELL">
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <TrendingDown size={16} color="red" />
                    <span>SELL</span>
                  </Stack>
                </Option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Type</FormLabel>
              <Select value={type} onChange={(_, value) => setType(value as any)}>
                <Option value="MARKET">Market</Option>
                <Option value="LIMIT">Limit</Option>
              </Select>
            </FormControl>
            <FormControl sx={{ flex: 1 }}>
              <FormLabel>Quantity</FormLabel>
              <Input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="100"
                required
              />
            </FormControl>
            {type === 'LIMIT' && (
              <FormControl sx={{ flex: 1 }}>
                <FormLabel>Price</FormLabel>
                <Input
                  type="number"
                  step="0.01"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  placeholder="950.00"
                  required
                />
              </FormControl>
            )}
          </Stack>

          <Button
            type="submit"
            variant="solid"
            color={side === 'BUY' ? 'success' : 'danger'}
            size="lg"
            startDecorator={side === 'BUY' ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
            disabled={!symbol || !quantity}
            sx={{ mt: 2 }}
          >
            {side} {quantity} {symbol.toUpperCase()}
          </Button>
        </Stack>
      </form>
    </Card>
  );
}

function OrderRow({ order, onCancel }: { order: Order; onCancel: (id: string) => void }) {
  const getStatusColor = () => {
    switch (order.status) {
      case 'FILLED': return 'success';
      case 'WORKING': return 'primary';
      case 'PENDING': return 'warning';
      case 'CANCELLED': case 'REJECTED': return 'danger';
    }
  };

  const getStatusIcon = () => {
    switch (order.status) {
      case 'FILLED': return <CheckCircle size={14} />;
      case 'WORKING': return <Activity size={14} />;
      case 'PENDING': return <Clock size={14} />;
      case 'CANCELLED': case 'REJECTED': return <X size={14} />;
    }
  };

  return (
    <tr>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          {order.id}
        </Typography>
      </td>
      <td>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography level="body-sm" fontWeight="medium">
            {order.symbol}
          </Typography>
          <Chip size="sm" variant="soft" color={order.account === 'GIA' ? 'warning' : order.account === 'ISA' ? 'success' : 'primary'}>
            {order.account}
          </Chip>
        </Stack>
      </td>
      <td>
        <Chip
          size="sm"
          variant="soft"
          color={order.side === 'BUY' ? 'success' : 'danger'}
          startDecorator={order.side === 'BUY' ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
        >
          {order.side}
        </Chip>
      </td>
      <td>
        <Typography level="body-sm">
          {order.type}
        </Typography>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          {order.quantity}
        </Typography>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          {order.price ? `$${order.price.toFixed(2)}` : '-'}
        </Typography>
      </td>
      <td>
        <Chip
          size="sm"
          variant="soft"
          color={getStatusColor()}
          startDecorator={getStatusIcon()}
        >
          {order.status}
        </Chip>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono" color="neutral">
          {order.filled}/{order.quantity}
        </Typography>
      </td>
      <td>
        <Typography level="body-xs" color="neutral" fontFamily="mono">
          {order.latency}ms
        </Typography>
      </td>
      <td>
        <Typography level="body-xs" color="neutral">
          {order.timestamp.toLocaleTimeString()}
        </Typography>
      </td>
      <td>
        {order.status === 'WORKING' || order.status === 'PENDING' ? (
          <IconButton
            size="sm"
            variant="plain"
            color="danger"
            onClick={() => onCancel(order.id)}
          >
            <X size={14} />
          </IconButton>
        ) : null}
      </td>
    </tr>
  );
}

function PositionRow({ position }: { position: Position }) {
  const pnlColor = position.unrealizedPnL >= 0 ? 'success' : 'danger';

  return (
    <tr>
      <td>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography level="body-sm" fontWeight="medium">
            {position.symbol}
          </Typography>
          <Chip size="sm" variant="soft" color={position.account === 'GIA' ? 'warning' : position.account === 'ISA' ? 'success' : 'primary'}>
            {position.account}
          </Chip>
        </Stack>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          {position.quantity.toLocaleString()}
        </Typography>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          ${position.avgPrice.toFixed(2)}
        </Typography>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          ${position.currentPrice.toFixed(2)}
        </Typography>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono" color={pnlColor}>
          {position.unrealizedPnL >= 0 ? '+' : ''}${position.unrealizedPnL.toFixed(2)}
        </Typography>
      </td>
      <td>
        <Typography level="body-sm" fontFamily="mono">
          ${(position.quantity * position.currentPrice).toLocaleString()}
        </Typography>
      </td>
      <td>
        <Stack direction="row" spacing={1}>
          <Button size="sm" variant="outlined" color="danger" startDecorator={<TrendingDown size={12} />}>
            Close
          </Button>
          <Button size="sm" variant="outlined" startDecorator={<Target size={12} />}>
            Hedge
          </Button>
        </Stack>
      </td>
    </tr>
  );
}

export default function OrderManagement() {
  const [orders, setOrders] = useState<Order[]>(mockOrders);
  const [positions, setPositions] = useState<Position[]>(mockPositions);
  const [activeTab, setActiveTab] = useState<'orders' | 'positions'>('orders');

  const handleSubmitOrder = (newOrder: any) => {
    const order: Order = {
      id: `ORD${Date.now()}`,
      ...newOrder,
      status: 'PENDING' as const,
      filled: 0,
      timestamp: new Date(),
      latency: Math.random() * 0.2 + 0.05 // Simulate 0.05-0.25ms latency
    };

    setOrders(prev => [order, ...prev]);

    // Simulate order processing
    setTimeout(() => {
      setOrders(prev => prev.map(o =>
        o.id === order.id
          ? { ...o, status: 'WORKING' as const }
          : o
      ));
    }, 100);
  };

  const handleCancelOrder = (orderId: string) => {
    setOrders(prev => prev.map(order =>
      order.id === orderId
        ? { ...order, status: 'CANCELLED' as const }
        : order
    ));
  };

  const workingOrders = orders.filter(o => o.status === 'WORKING' || o.status === 'PENDING');
  const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
  const avgLatency = orders.filter(o => o.latency).reduce((sum, o) => sum + (o.latency || 0), 0) / orders.filter(o => o.latency).length;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography level="h3">Order Management</Typography>
          <Typography level="body-sm" color="neutral">
            Ultra-fast order entry and execution monitoring
          </Typography>
        </Box>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Chip variant="soft" color="primary">
            {workingOrders.length} Working
          </Chip>
          <Chip variant="soft" color={totalPnL >= 0 ? 'success' : 'danger'}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)} P&L
          </Chip>
          <Chip variant="soft" color="neutral">
            {avgLatency.toFixed(2)}ms Avg
          </Chip>
        </Stack>
      </Stack>

      {/* Performance Alert */}
      {avgLatency > 0.2 && (
        <Alert color="warning" sx={{ mb: 3 }} startDecorator={<Timer />}>
          <Box>
            <Typography level="body-sm" fontWeight="medium">
              High Order Latency Detected
            </Typography>
            <Typography level="body-xs">
              Average execution latency is {avgLatency.toFixed(2)}ms. Consider optimizing network connection.
            </Typography>
          </Box>
        </Alert>
      )}

      {/* Quick Order Entry */}
      <QuickOrderEntry onSubmitOrder={handleSubmitOrder} />

      {/* Tab Navigation */}
      <Box sx={{ mt: 3 }}>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Button
            variant={activeTab === 'orders' ? 'solid' : 'outlined'}
            onClick={() => setActiveTab('orders')}
            startDecorator={<BarChart3 size={16} />}
          >
            Orders ({orders.length})
          </Button>
          <Button
            variant={activeTab === 'positions' ? 'solid' : 'outlined'}
            onClick={() => setActiveTab('positions')}
            startDecorator={<Target size={16} />}
          >
            Positions ({positions.length})
          </Button>
        </Stack>

        {/* Orders Table */}
        {activeTab === 'orders' && (
          <Card variant="outlined">
            <Box sx={{ overflow: 'auto' }}>
              <Table>
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Type</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Status</th>
                    <th>Filled</th>
                    <th>Latency</th>
                    <th>Time</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <OrderRow
                      key={order.id}
                      order={order}
                      onCancel={handleCancelOrder}
                    />
                  ))}
                </tbody>
              </Table>
            </Box>
          </Card>
        )}

        {/* Positions Table */}
        {activeTab === 'positions' && (
          <Card variant="outlined">
            <Box sx={{ overflow: 'auto' }}>
              <Table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Avg Price</th>
                    <th>Current Price</th>
                    <th>Unrealized P&L</th>
                    <th>Market Value</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map(position => (
                    <PositionRow key={`${position.symbol}-${position.account}`} position={position} />
                  ))}
                </tbody>
              </Table>
            </Box>
          </Card>
        )}
      </Box>
    </Box>
  );
}