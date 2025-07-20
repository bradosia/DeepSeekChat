const express = require('express');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
const dotenv = require('dotenv');
const { DebateManager } = require('./services/DebateManager');
const { GMIApiService } = require('./services/GMIApiService');

// Load environment variables
dotenv.config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Initialize services
const gmiService = new GMIApiService();
const debateManager = new DebateManager(gmiService);

// Routes
app.get('/api/speakers', (req, res) => {
  const speakers = require('./data/speakers.json');
  res.json(speakers);
});

app.get('/api/topics', (req, res) => {
  const topics = require('./data/topics.json');
  res.json(topics);
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('startDebate', async (data) => {
    const { speaker1, speaker2, topic } = data;
    
    try {
      await debateManager.startDebate(socket, speaker1, speaker2, topic);
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  socket.on('sendQuestion', async (data) => {
    const { question } = data;
    
    try {
      await debateManager.handleUserQuestion(socket, question);
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    debateManager.cleanupDebate(socket.id);
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 