const axios = require('axios');

class GMIApiService {
  constructor() {
    this.apiKey = process.env.GMI_API_KEY;
    this.baseURL = 'https://api.gmi-serving.com/v1/chat/completions';
    
    if (!this.apiKey) {
      throw new Error('GMI_API_KEY not found in environment variables');
    }
  }

  async generateResponse(messages, temperature = 0.7) {
    try {
      const response = await axios.post(this.baseURL, {
        model: "deepseek-ai/DeepSeek-R1-0528",
        messages: messages,
        temperature: temperature,
        max_tokens: 150,
        stream: false
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        }
      });

      if (response.data.choices && response.data.choices.length > 0) {
        return response.data.choices[0].message.content;
      } else {
        throw new Error('No response from GMI API');
      }
    } catch (error) {
      console.error('GMI API Error:', error.response?.data || error.message);
      throw new Error(`GMI API Error: ${error.response?.data?.error || error.message}`);
    }
  }

  async generateSpeakerResponse(speaker, context, topic, userQuestion = null) {
    const speakerPrompt = this.buildSpeakerPrompt(speaker, context, topic, userQuestion);
    
    const messages = [
      {
        role: "system",
        content: speakerPrompt
      },
      {
        role: "user",
        content: userQuestion || `Continue the discussion about ${topic}. Keep your response concise (2-3 sentences max) and stay in character.`
      }
    ];

    return await this.generateResponse(messages, speaker.temperature || 0.7);
  }

  buildSpeakerPrompt(speaker, context, topic, userQuestion) {
    let prompt = `You are ${speaker.name}, ${speaker.description}. `;
    prompt += `Your communication style: ${speaker.style}. `;
    prompt += `Key traits: ${speaker.traits.join(', ')}. `;
    
    if (context) {
      prompt += `\n\nPrevious conversation context:\n${context}\n\n`;
    }
    
    prompt += `Current topic: ${topic}\n\n`;
    
    if (userQuestion) {
      prompt += `A user has asked: "${userQuestion}"\n\n`;
    }
    
    prompt += `Respond as ${speaker.name} would. Keep responses concise (2-3 sentences), authentic to your personality, and engaging. Use your characteristic tone and mannerisms.`;
    
    return prompt;
  }
}

module.exports = { GMIApiService }; 