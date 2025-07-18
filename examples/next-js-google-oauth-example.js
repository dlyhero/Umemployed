// pages/companies/[companyId]/dashboard.js or app/companies/[companyId]/dashboard/page.js
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router'; // or 'next/navigation' for app router

/*
* IMPORTANT: OAuth Redirect Behavior
* 
* After successful Google OAuth, the backend will redirect the user to:
* - /companies/{company_id}/dashboard?google_oauth=success (if user has a company)
* - /dashboard/settings?google_oauth=success (fallback if no company)
* 
* Your Next.js app should handle both routes and check for the google_oauth
* query parameter to show appropriate success/error messages.
* 
* For company-specific dashboards, make sure your routing structure matches:
* - pages/companies/[companyId]/dashboard.js (Pages Router)
* - app/companies/[companyId]/dashboard/page.js (App Router)
*/

export default function CompanyDashboard() {
  const router = useRouter();
  const { companyId } = router.query; // Get company ID from URL
  const [googleConnected, setGoogleConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Check if we're returning from Google OAuth
    const { google_oauth, message: oauthMessage } = router.query;
    
    if (google_oauth === 'success') {
      setMessage('Google Calendar connected successfully! You can now schedule interviews with Google Meet.');
      setGoogleConnected(true);
      // Clear URL params but keep company ID
      router.replace(`/companies/${companyId}/dashboard`, undefined, { shallow: true });
    } else if (google_oauth === 'error') {
      setMessage(oauthMessage || 'Failed to connect Google Calendar. Please try again.');
    }

    // Check current Google connection status
    if (companyId) {
      checkGoogleConnection();
    }
  }, [router.query, companyId]);

  const checkGoogleConnection = async () => {
    try {
      const token = localStorage.getItem('auth_token'); // Your auth token
      const response = await fetch('/api/company/google/check-connection/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setGoogleConnected(data.connected);
    } catch (error) {
      console.error('Error checking Google connection:', error);
    }
  };

  const connectGoogle = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/company/google/connect/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      
      if (data.authorization_url) {
        // Redirect to Google OAuth
        window.location.href = data.authorization_url;
      }
    } catch (error) {
      setMessage('Error initiating Google connection');
      setLoading(false);
    }
  };

  const disconnectGoogle = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      await fetch('/api/company/google/disconnect/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setGoogleConnected(false);
      setMessage('Google Calendar disconnected');
    } catch (error) {
      setMessage('Error disconnecting Google Calendar');
    }
  };

  return (
    <div className="company-dashboard">
      <h1>Company Dashboard</h1>
      
      {/* Success/Error message display */}
      {message && (
        <div className={`alert ${message.includes('success') ? 'alert-success' : 'alert-error'}`}>
          {message}
          {message.includes('success') && (
            <p className="text-sm mt-2">
              You can now schedule interviews with automatic Google Meet links!
            </p>
          )}
        </div>
      )}
      
      <div className="google-calendar-section">
        <h2>Google Calendar Integration</h2>
        <p>Connect your Google Calendar to schedule interviews with Google Meet links.</p>
        
        {googleConnected ? (
          <div>
            <p className="status connected">✅ Google Calendar is connected</p>
            <button onClick={disconnectGoogle} className="btn btn-secondary">
              Disconnect Google Calendar
            </button>
          </div>
        ) : (
          <div>
            <p className="status disconnected">❌ Google Calendar is not connected</p>
            <button 
              onClick={connectGoogle} 
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Connecting...' : 'Connect Google Calendar'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
