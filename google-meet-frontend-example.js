/**
 * Google Meet Integration API Client for Next.js Frontend
 * 
 * Usage example for your Next.js application to integrate with Google Meet scheduling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class GoogleMeetAPI {
  constructor(authToken) {
    this.authToken = authToken;
    this.headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.authToken}`,
    };
  }

  async checkGoogleConnection() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company/google/check-connection/`, {
        method: 'GET',
        headers: this.headers,
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error checking Google connection:', error);
      throw error;
    }
  }

  async initiateGoogleConnect() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company/google/connect/`, {
        method: 'GET',
        headers: this.headers,
      });
      
      const data = await response.json();
      
      if (data.authorization_url) {
        // Redirect user to Google OAuth
        window.location.href = data.authorization_url;
      }
      
      return data;
    } catch (error) {
      console.error('Error initiating Google connect:', error);
      throw error;
    }
  }

  async disconnectGoogle() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company/google/disconnect/`, {
        method: 'DELETE',
        headers: this.headers,
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error disconnecting Google:', error);
      throw error;
    }
  }

  async createGoogleMeetInterview(interviewData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company/google/create-interview/`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(interviewData),
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating Google Meet interview:', error);
      throw error;
    }
  }

  async listInterviews() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company/interviews/`, {
        method: 'GET',
        headers: this.headers,
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error listing interviews:', error);
      throw error;
    }
  }
}

// React Component Example
export function GoogleMeetIntegration({ authToken }) {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const googleMeetAPI = new GoogleMeetAPI(authToken);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const result = await googleMeetAPI.checkGoogleConnection();
      setIsConnected(result.connected);
    } catch (error) {
      console.error('Error checking connection:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      await googleMeetAPI.initiateGoogleConnect();
    } catch (error) {
      console.error('Error connecting Google:', error);
    }
  };

  const handleDisconnect = async () => {
    if (confirm('Are you sure you want to disconnect Google Calendar?')) {
      try {
        const result = await googleMeetAPI.disconnectGoogle();
        if (result.success) {
          setIsConnected(false);
          alert('Google Calendar disconnected successfully!');
        }
      } catch (error) {
        console.error('Error disconnecting Google:', error);
      }
    }
  };

  const scheduleInterview = async (candidateId, jobTitle, date, time, note = '') => {
    try {
      const interviewData = {
        candidate_id: candidateId,
        job_title: jobTitle,
        date: date,
        time: time,
        timezone: 'UTC',
        note: note,
      };

      const result = await googleMeetAPI.createGoogleMeetInterview(interviewData);
      
      if (result.success) {
        alert(`Interview scheduled successfully! Meet link: ${result.meeting_link}`);
        return result;
      } else if (result.needs_google_auth) {
        alert('Please connect your Google Calendar first.');
        handleConnect();
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error scheduling interview:', error);
      alert('Error scheduling interview. Please try again.');
    }
  };

  if (isLoading) {
    return <div>Checking Google Calendar connection...</div>;
  }

  return (
    <div className="google-meet-integration">
      <h3>Google Meet Integration</h3>
      
      {isConnected ? (
        <div>
          <div className="status connected">
            ✅ Google Calendar connected! You can now schedule interviews with Google Meet.
          </div>
          <button onClick={handleDisconnect} className="btn btn-danger">
            Disconnect Google Calendar
          </button>
        </div>
      ) : (
        <div>
          <div className="status disconnected">
            ⚠️ Connect your Google Calendar to schedule interviews with Google Meet.
          </div>
          <button onClick={handleConnect} className="btn btn-primary">
            Connect Google Calendar
          </button>
        </div>
      )}

      {/* Example usage in interview scheduling form */}
      <InterviewScheduleForm 
        onSchedule={scheduleInterview}
        googleConnected={isConnected}
      />
    </div>
  );
}

// Example interview scheduling form component
function InterviewScheduleForm({ onSchedule, googleConnected }) {
  const [formData, setFormData] = useState({
    candidateId: '',
    jobTitle: '',
    date: '',
    time: '',
    note: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!googleConnected) {
      alert('Please connect Google Calendar first');
      return;
    }
    
    onSchedule(
      formData.candidateId,
      formData.jobTitle,
      formData.date,
      formData.time,
      formData.note
    );
  };

  return (
    <form onSubmit={handleSubmit} className="interview-form">
      <h4>Schedule Google Meet Interview</h4>
      
      <input
        type="number"
        placeholder="Candidate ID"
        value={formData.candidateId}
        onChange={(e) => setFormData({...formData, candidateId: e.target.value})}
        required
      />
      
      <input
        type="text"
        placeholder="Job Title"
        value={formData.jobTitle}
        onChange={(e) => setFormData({...formData, jobTitle: e.target.value})}
        required
      />
      
      <input
        type="date"
        value={formData.date}
        onChange={(e) => setFormData({...formData, date: e.target.value})}
        required
      />
      
      <input
        type="time"
        value={formData.time}
        onChange={(e) => setFormData({...formData, time: e.target.value})}
        required
      />
      
      <textarea
        placeholder="Interview notes (optional)"
        value={formData.note}
        onChange={(e) => setFormData({...formData, note: e.target.value})}
      />
      
      <button 
        type="submit" 
        disabled={!googleConnected}
        className="btn btn-success"
      >
        Schedule Google Meet Interview
      </button>
    </form>
  );
}

export default GoogleMeetAPI;
