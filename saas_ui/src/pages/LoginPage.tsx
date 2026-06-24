import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sheet, Typography, FormControl, FormLabel, Input, Button, Box } from '@mui/joy';

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
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', bgcolor: '#0a0a0a' }}>
      <Sheet sx={{ width: 400, p: 4, borderRadius: 'md', bgcolor: '#111', color: 'white', border: '1px solid #333' }}>
        <Typography level="h3" sx={{ mb: 2, color: 'white', textAlign: 'center' }}>
          Nova Trader Auth
        </Typography>
        <form onSubmit={handleLogin}>
          <FormControl sx={{ mb: 2 }}>
            <FormLabel sx={{ color: '#aaa' }}>Email</FormLabel>
            <Input 
              type="email" 
              required 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ bgcolor: '#222', color: 'white', borderColor: '#444' }}
            />
          </FormControl>
          <FormControl sx={{ mb: 3 }}>
            <FormLabel sx={{ color: '#aaa' }}>Password</FormLabel>
            <Input 
              type="password" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ bgcolor: '#222', color: 'white', borderColor: '#444' }}
            />
          </FormControl>
          <Button type="submit" fullWidth sx={{ bgcolor: '#ff6b35', '&:hover': { bgcolor: '#e85a28' } }}>
            Login to Dashboard
          </Button>
        </form>
      </Sheet>
    </Box>
  );
}
