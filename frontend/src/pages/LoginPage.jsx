import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  InputAdornment,
  IconButton,
  Link,
  Divider
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Lock,
  Person
} from '@mui/icons-material';

import { login } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError(''); // Clear error when user starts typing
  };

  const handleSubmit = async (e) => {
    
    e.preventDefault();
    setError('');

    // Basic validation
    if (!formData.username || !formData.password) {
      setError('Please fill in all fields');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    try {

      const res = await login(formData.username, formData.password);

      
      if (res.status === 200) {
        localStorage.setItem("authTokens", JSON.stringify(res.data));
        navigate('/dashboard');
      }
      
    } catch (err) {
      setError('Authentication failed. Please try again.');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({ username: '', password: '' });
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          minHeight: '100vh'
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
            borderRadius: 2
          }}
        >
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              backgroundColor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2
            }}
          >
            <Person sx={{ color: 'white', fontSize: 30 }} />
          </Box>

          <Typography component="h1" variant="h4" gutterBottom>
            {isLogin ? 'Sign In' : 'Sign Up'}
          </Typography>

          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            {isLogin 
              ? 'Welcome back! Please sign in to your account.' 
              : 'Create your account to get started.'
            }
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoFocus
              value={formData.username}
              onChange={handleInputChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleInputChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={togglePasswordVisibility}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 3, 
                mb: 2, 
                height: 48,
                borderRadius: 2
              }}
            >
              {isLogin ? 'Sign In' : 'Sign Up'}
            </Button>

            <Divider sx={{ my: 2 }}>OR</Divider>

            <Box textAlign="center">
              <Typography variant="body2" color="textSecondary">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <Link
                  component="button"
                  variant="body2"
                  onClick={switchMode}
                  sx={{ textDecoration: 'none' }}
                >
                  {isLogin ? 'Sign up here' : 'Sign in here'}
                </Link>
              </Typography>
            </Box>

            {isLogin && (
              <Box textAlign="center" sx={{ mt: 1 }}>
                <Link
                  component="button"
                  variant="body2"
                  sx={{ textDecoration: 'none' }}
                  onClick={() => alert('Password reset functionality would go here')}
                >
                  Forgot password?
                </Link>
              </Box>
            )}
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}