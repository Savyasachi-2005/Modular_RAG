import api from './api';

export const exportService = {
  async exportToPDF(query, answer, sources = []) {
    const response = await api.post('/export/pdf', {
      query,
      answer,
      sources
    }, {
      responseType: 'blob'
    });
    
    // Create blob URL and trigger download
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    // Extract filename from Content-Disposition header if available
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'chat-export.pdf';
    if (contentDisposition) {
      const matches = contentDisposition.match(/filename="?([^"]+)"?/);
      if (matches) {
        filename = matches[1];
      }
    }
    
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    return { success: true, filename };
  },

  async exportToMarkdown(session, messages) {
    const timestamp = new Date().toLocaleString();
    const filename = `chat-${session.session_id}-${Date.now()}.md`;
    
    let content = `# Chat Export - ${session.title}\n\n`;
    content += `**Date:** ${timestamp}\n\n`;
    content += `---\n\n`;
    
    messages.forEach((msg, index) => {
      const role = msg.role === 'user' ? '👤 User' : '🤖 Assistant';
      content += `### ${role}\n\n`;
      content += `${msg.content}\n\n`;
      if (msg.sources && msg.sources.length > 0) {
        content += `**Sources:**\n`;
        msg.sources.forEach((source, i) => {
          content += `${i + 1}. ${source.title || 'Source'}\n`;
        });
        content += `\n`;
      }
      content += `---\n\n`;
    });

    // Create and download file
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    return { success: true, filename };
  },

  async exportToText(session, messages) {
    const timestamp = new Date().toLocaleString();
    const filename = `chat-${session.session_id}-${Date.now()}.txt`;
    
    let content = `Chat Export - ${session.title}\n`;
    content += `Date: ${timestamp}\n`;
    content += `${'='.repeat(60)}\n\n`;
    
    messages.forEach((msg, index) => {
      const role = msg.role === 'user' ? 'User' : 'Assistant';
      content += `${role}:\n`;
      content += `${msg.content}\n`;
      if (msg.sources && msg.sources.length > 0) {
        content += `\nSources:\n`;
        msg.sources.forEach((source, i) => {
          content += `  ${i + 1}. ${source.title || 'Source'}\n`;
        });
      }
      content += `\n${'-'.repeat(60)}\n\n`;
    });

    // Create and download file
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    return { success: true, filename };
  },

  async exportChatSession(session, messages, format = 'markdown') {
    if (format === 'pdf') {
      // For PDF, we'll combine all messages into a single export
      if (messages.length === 0) {
        throw new Error('No messages to export');
      }
      
      // Create a combined query and answer from all messages
      let combinedQuery = '';
      let combinedAnswer = '';
      let allSources = [];
      
      messages.forEach((msg, index) => {
        if (msg.role === 'user') {
          combinedQuery += (combinedQuery ? '\n\n' : '') + `Q${Math.floor(index/2) + 1}: ${msg.content}`;
        } else if (msg.role === 'assistant') {
          combinedAnswer += (combinedAnswer ? '\n\n' : '') + `A${Math.floor(index/2) + 1}: ${msg.content}`;
          if (msg.sources && msg.sources.length > 0) {
            allSources.push(...msg.sources);
          }
        }
      });
      
      return await this.exportToPDF(
        combinedQuery || `Chat Session: ${session.title}`, 
        combinedAnswer || 'No responses in this chat.', 
        allSources
      );
    } else if (format === 'markdown') {
      return await this.exportToMarkdown(session, messages);
    } else if (format === 'text') {
      return await this.exportToText(session, messages);
    }
    
    throw new Error('Unsupported export format');
  }
};