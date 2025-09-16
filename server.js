const express = require('express');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: ["http://localhost:3000", "http://frontend:3000"],
    methods: ["GET", "POST"],
    credentials: true
  }
});

const PORT = process.env.PORT || 3001;

// Enhanced CORS configuration
app.use(cors({
  origin: ["http://localhost:3000", "http://frontend:3000"],
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true
}));

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  console.log('Request body:', req.body);
  next();
});

// Health check
app.get('/health', (req, res) => {
  console.log('Health check requested');
  res.json({
    status: 'OK',
    service: 'JatayuNetra Backend',
    timestamp: new Date().toISOString(),
    port: PORT
  });
});

// Basic auth endpoint with enhanced logging
app.post('/api/auth/login', (req, res) => {
  console.log('Login attempt:', { 
    username: req.body.username, 
    role: req.body.role,
    hasPassword: !!req.body.password 
  });

  const { username, password, role } = req.body;

  // Validation
  if (!username || !password || !role) {
    console.log('Missing required fields');
    return res.status(400).json({
      success: false,
      message: 'Username, password, and role are required'
    });
  }

  // Demo users
  const users = {
    'priya_sharma': { password: 'Tourist@123', role: 'tourist', name: 'Priya Sharma' },
    'officer_singh': { password: 'Police@789', role: 'police', name: 'Officer Singh' },
    'dr_patel': { password: 'Doctor@101', role: 'hospital', name: 'Dr. Patel' },
    'tourism_admin': { password: 'Tourism@202', role: 'tourism', name: 'Tourism Admin' }
  };

  const user = users[username];
  console.log('User lookup result:', { found: !!user, username });

  if (!user) {
    console.log('User not found');
    return res.status(401).json({
      success: false,
      message: 'Invalid username'
    });
  }

  if (user.password !== password) {
    console.log('Password mismatch');
    return res.status(401).json({
      success: false,
      message: 'Invalid password'
    });
  }

  if (user.role !== role) {
    console.log('Role mismatch');
    return res.status(401).json({
      success: false,
      message: 'Invalid role for this user'
    });
  }

  console.log('Login successful for:', username);

  res.json({
    success: true,
    data: {
      token: 'demo-jwt-token-' + Date.now(),
      user: {
        id: username,
        username: username,
        fullName: user.name,
        role: user.role
      }
    }
  });
});

// SOS endpoint
app.post('/api/emergency/sos', (req, res) => {
  console.log('SOS Alert received:', req.body);
  res.json({
    success: true,
    message: 'SOS alert sent successfully',
    alertId: 'SOS-' + Date.now()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    success: false,
    message: 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  console.log('404 - Route not found:', req.originalUrl);
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// WebSocket connection
io.on('connection', (socket) => {
  console.log('User connected via WebSocket:', socket.id);

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 JatayuNetra Backend running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔐 Login endpoint: http://localhost:${PORT}/api/auth/login`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});