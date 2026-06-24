import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sheet, Typography, FormControl, FormLabel, Input, Button, Box, IconButton, useColorScheme } from '@mui/joy';
import { Moon, Sun } from 'lucide-react';

function ColorSchemeToggle() {
  const { mode, setMode } = useColorScheme();
  return (
    <IconButton
      onClick={() => setMode(mode === 'light' ? 'dark' : 'light')}
      variant="outlined"
      size="sm"
      sx={{ position: 'absolute', top: 16, right: 16, borderRadius: 'xl' }}
    >
      {mode === 'light' ? <Moon /> : <Sun />}
    </IconButton>
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulated authentication
    navigate('/dashboard');
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh', 
      bgcolor: 'background.body',
      position: 'relative'
    }}>
      <ColorSchemeToggle />
      <Sheet 
        variant="outlined"
        sx={{ 
          width: 400, 
          p: 4, 
          borderRadius: 'lg', 
          boxShadow: 'lg',
          bgcolor: 'background.surface'
        }}
      >
        <Typography level="h3" sx={{ mb: 1, textAlign: 'center' }}>
          Nova Trader Auth
        </Typography>
        <Typography level="body-sm" sx={{ mb: 3, textAlign: 'center', color: 'text.secondary' }}>
          Sign in to access your trading dashboard
        </Typography>
        <form onSubmit={handleLogin}>
          <FormControl sx={{ mb: 2 }}>
            <FormLabel>Email</FormLabel>
            <Input 
              type="email" 
              required 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@novatrader.com"
            />
          </FormControl>
          <FormControl sx={{ mb: 4 }}>
            <FormLabel>Password</FormLabel>
            <Input 
              type="password" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </FormControl>
          <Button type="submit" fullWidth color="primary" size="lg">
            Login to Dashboard
          </Button>
        </form>
      </Sheet>
    </Box>
  );
}
