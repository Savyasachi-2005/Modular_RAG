import api from './api';

export const speechService = {
  /**
   * Convert speech audio to text using SarvamAI ASR
   * @param {Blob} audioBlob - The audio blob to transcribe
   * @returns {Promise<{text: string}>} - The transcribed text
   */
  async speechToText(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');

    const response = await api.post('/speech/to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Convert text to speech audio using SarvamAI TTS
   * @param {string} text - The text to convert to speech
   * @param {object} options - Optional TTS parameters
   * @returns {Promise<Blob>} - The audio blob
   */
  async textToSpeech(text, options = {}) {
    const response = await api.post(
      '/speech/to-audio',
      {
        text,
        target_language_code: options.languageCode || 'en-IN',
        speaker: options.speaker || 'anushka',
        pitch: options.pitch || 0,
        pace: options.pace || 1,
        loudness: options.loudness || 1,
      },
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },

  /**
   * Check if speech service is available
   * @returns {Promise<{available: boolean, message: string}>}
   */
  async checkHealth() {
    const response = await api.get('/speech/health');
    return response.data;
  },
};
