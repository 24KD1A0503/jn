# Fix the Docker networking and proxy issues

# The problem is that the React app is trying to proxy to localhost:3001
# but in Docker, services communicate using service names, not localhost

# Fixed files to resolve the proxy/networking issue
fixed_networking_files = {}

# 1. Fixed docker-compose.yml with proper networking
fixed_networking_files['docker-compose.yml'] = """services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://backend:3001
      - REACT_APP_API_URL=http://localhost:3001
    depends_on:
      - backend
    networks:
      - jatayu-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://jatayu:password@postgres:5432/jatayu_netra
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-super-secret-jwt-key-change-in-production
      - PORT=3001
    depends_on:
      - postgres
      - redis
    networks:
      - jatayu-network

  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - PORT=5000
    networks:
      - jatayu-network

  postgres:
    image: postgis/postgis:14-3.2
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=jatayu
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=jatayu_netra
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/postgresql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    networks:
      - jatayu-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - jatayu-network

volumes:
  postgres_data:

networks:
  jatayu-network:
    driver: bridge"""

# 2. Fixed frontend package.json (REMOVE proxy setting)
fixed_networking_files['frontend/package.json'] = """{
  "name": "jatayu-netra-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.3.0",
    "react-scripts": "5.0.1",
    "axios": "^1.4.0",
    "react-hot-toast": "^2.4.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}"""

# 3. Fixed frontend Login.js with proper API URL handling
fixed_networking_files['frontend/src/pages/Login.js'] = """import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import axios from 'axios';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'tourist'
  });
  const [loading, setLoading] = useState(false);

  // Configure axios base URL for API calls
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  
  const roles = [
    { value: 'tourist', label: '🧳 Tourist', demo: { username: 'priya_sharma', password: 'Tourist@123' } },
    { value: 'police', label: '👮 Police', demo: { username: 'officer_singh', password: 'Police@789' } },
    { value: 'hospital', label: '🏥 Hospital', demo: { username: 'dr_patel', password: 'Doctor@101' } },
    { value: 'tourism', label: '🏛️ Tourism', demo: { username: 'tourism_admin', password: 'Tourism@202' } }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      console.log('Attempting login to:', `${API_BASE_URL}/api/auth/login`);
      console.log('Login data:', { ...formData, password: '[HIDDEN]' });
      
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, formData, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Login response:', response.data);
      
      if (response.data.success) {
        localStorage.setItem('user', JSON.stringify(response.data.data.user));
        toast.success('Login successful!');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.code === 'ECONNREFUSED') {
        toast.error('Cannot connect to server. Please ensure backend is running.');
      } else if (error.response) {
        toast.error(error.response.data?.message || 'Login failed');
      } else if (error.request) {
        toast.error('Network error: Cannot reach server');
      } else {
        toast.error('Login failed: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (role) => {
    const roleData = roles.find(r => r.value === role);
    if (roleData) {
      setFormData({ 
        ...roleData.demo, 
        role 
      });
    }
  };

  const testConnection = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      toast.success('Backend connection successful!');
      console.log('Backend health:', response.data);
    } catch (error) {
      toast.error('Cannot connect to backend');
      console.error('Connection test failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🛡️</div>
          <h1 className="text-3xl font-bold text-gray-900">JatayuNetra</h1>
          <p className="text-gray-600 mt-2">Smart Tourist Safety System</p>
        </div>

        {/* Connection Test Button */}
        <div className="mb-4 text-center">
          <button
            type="button"
            onClick={testConnection}
            className="text-xs bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded"
          >
            Test Backend Connection
          </button>
          <p className="text-xs text-gray-500 mt-1">API: {API_BASE_URL}</p>
        </div>

        {/* Demo Credentials */}
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-3">Quick Demo Login:</p>
          <div className="grid grid-cols-2 gap-2">
            {roles.map((role) => (
              <button
                key={role.value}
                type="button"
                onClick={() => fillDemo(role.value)}
                className="text-xs p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                {role.label}
              </button>
            ))}
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <select
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              {roles.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <input
              type="text"
              placeholder="Username"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-blue-300"
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;"""

# 4. Fixed backend server.js with better CORS and error handling
fixed_networking_files['backend/src/server.js'] = """const express = require('express');
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
});"""

# 5. Fixed Dashboard.js with proper API URL
fixed_networking_files['frontend/src/pages/Dashboard.js'] = """import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import axios from 'axios';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(userData));
  }, [navigate]);

  const handleSOS = async () => {
    if (window.confirm('🚨 EMERGENCY SOS ALERT! Are you sure you want to send an SOS signal?')) {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/emergency/sos`, {
          timestamp: new Date().toISOString(),
          location: { lat: 10.0261, lng: 76.3125 },
          type: 'manual'
        });
        
        if (response.data.success) {
          toast.success('🚨 SOS Alert sent successfully! Help is on the way!');
        }
      } catch (error) {
        console.error('SOS error:', error);
        toast.error('Failed to send SOS alert');
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    toast.success('Logged out successfully');
    navigate('/login');
  };

  if (!user) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;

  const getDashboardContent = () => {
    switch (user.role) {
      case 'tourist':
        return (
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <div className="card-icon">👤</div>
              <div className="card-title">My Profile</div>
              <div className="card-description">Manage personal information and emergency contacts</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">🚗</div>
              <div className="card-title">Vehicle Assistance</div>
              <div className="card-description">Find nearby fuel stations, mechanics, and tire repair</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">🏥</div>
              <div className="card-title">Medical Assistance</div>
              <div className="card-description">Emergency medical help and nearby hospitals</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">👮</div>
              <div className="card-title">Police Assistance</div>
              <div className="card-description">Report incidents and get police help</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">📞</div>
              <div className="card-title">Emergency Contacts</div>
              <div className="card-description">Manage your emergency contact list</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">🗺️</div>
              <div className="card-title">Plan a Trip</div>
              <div className="card-description">Plan safe routes and get travel recommendations</div>
            </div>
          </div>
        );
      case 'police':
        return (
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <div className="card-icon">🚨</div>
              <div className="card-title">SOS Alerts</div>
              <div className="card-description">Monitor and respond to emergency alerts</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">👥</div>
              <div className="card-title">Tourist Records</div>
              <div className="card-description">View tourist information and tracking data</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">📋</div>
              <div className="card-title">E-FIR Generator</div>
              <div className="card-description">Generate electronic FIRs automatically</div>
            </div>
          </div>
        );
      case 'hospital':
        return (
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <div className="card-icon">🚑</div>
              <div className="card-title">Medical Alerts</div>
              <div className="card-description">Receive and respond to medical emergencies</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">👨‍⚕️</div>
              <div className="card-title">Patient Information</div>
              <div className="card-description">Access tourist medical information</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">🚨</div>
              <div className="card-title">Ambulance Dispatch</div>
              <div className="card-description">Coordinate ambulance services</div>
            </div>
          </div>
        );
      case 'tourism':
        return (
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <div className="card-icon">📊</div>
              <div className="card-title">Tourist Analytics</div>
              <div className="card-description">View tourism statistics and trends</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">🗺️</div>
              <div className="card-title">Safety Heatmap</div>
              <div className="card-description">Monitor tourist safety zones and hotspots</div>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">⚠️</div>
              <div className="card-title">Risk Monitoring</div>
              <div className="card-description">Track and assess safety risks in real-time</div>
            </div>
          </div>
        );
      default:
        return <div>Unknown role</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-2xl mr-2">🛡️</span>
              <h1 className="text-xl font-bold text-gray-900">JatayuNetra</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user.fullName} ({user.role})
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {user.role.charAt(0).toUpperCase() + user.role.slice(1)} Dashboard
            </h2>
            
            {/* SOS Button - Only for tourists */}
            {user.role === 'tourist' && (
              <div className="mb-8">
                <button
                  onClick={handleSOS}
                  className="sos-button"
                  title="Emergency SOS - Click in case of emergency"
                >
                  🚨 SOS
                </button>
                <p className="text-sm text-gray-600 mt-2">
                  Emergency SOS Button - Click only in case of real emergency
                </p>
              </div>
            )}
          </div>

          {getDashboardContent()}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;"""

print("✅ Fixed Docker networking and proxy issues!")
print(f"📊 Fixed files: {len(fixed_networking_files)}")
print("\n🔧 Key fixes applied:")
print("   ✅ Removed proxy setting from frontend package.json")
print("   ✅ Added proper API URL configuration")
print("   ✅ Enhanced CORS settings in backend")
print("   ✅ Added connection testing in frontend")
print("   ✅ Better error handling and logging")
print("   ✅ Fixed Docker service communication")

for file_path in fixed_networking_files.keys():
    print(f"  📄 {file_path}")