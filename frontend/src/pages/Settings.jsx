import { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { uploadLogo, deleteLogo, updateProfile } from '../services/api';

export default function Settings() {
  const { user, updateUser } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);
  const [vatId, setVatId] = useState(user?.vat_id || '');
  const [companyName, setCompanyName] = useState(user?.company_name || '');

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const response = await uploadLogo(file);
      updateUser(response.data);
      setSuccess('Logo uploaded successfully');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload logo');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteLogo = async () => {
    if (!window.confirm('Are you sure you want to delete the logo?')) return;

    setError('');
    setSuccess('');

    try {
      const response = await deleteLogo();
      updateUser(response.data);
      setSuccess('Logo deleted successfully');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete logo');
    }
  };

  const handleSaveProfile = async () => {
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const response = await updateProfile({
        company_name: companyName,
        vat_id: vatId,
      });
      updateUser(response.data);
      setSuccess('Profile updated successfully');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const logoUrl = user?.logo_path
    ? `http://localhost:8000/uploads/${user.logo_path}`
    : null;

  return (
    <div className="settings-page">
      <h1>Settings</h1>

      <div className="settings-section">
        <h2>Company Logo</h2>
        <p className="settings-description">
          Upload your company logo to display it on reports and commercial offers.
        </p>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="logo-section">
          {logoUrl ? (
            <div className="current-logo">
              <img src={logoUrl} alt="Company Logo" className="logo-preview" />
              <div className="logo-actions">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="btn btn-primary"
                  disabled={uploading}
                >
                  {uploading ? 'Uploading...' : 'Change Logo'}
                </button>
                <button
                  onClick={handleDeleteLogo}
                  className="btn btn-danger"
                  disabled={uploading}
                >
                  Delete Logo
                </button>
              </div>
            </div>
          ) : (
            <div className="no-logo">
              <div className="logo-placeholder">No logo uploaded</div>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="btn btn-primary"
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Upload Logo'}
              </button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>
      </div>

      <div className="settings-section">
        <h2>Company Information</h2>
        <p className="settings-description">
          This information will appear on your reports and commercial offers.
        </p>
        <div className="form-grid">
          <div className="form-group">
            <label>Company Name</label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Your company name"
            />
          </div>
          <div className="form-group">
            <label>VAT ID</label>
            <input
              type="text"
              value={vatId}
              onChange={(e) => setVatId(e.target.value)}
              placeholder="e.g., HR12345678901"
            />
          </div>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleSaveProfile}
          disabled={saving}
          style={{ marginTop: '16px' }}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="settings-section">
        <h2>Account Information</h2>
        <div className="info-grid">
          <div className="info-item">
            <label>Username</label>
            <span>{user?.username}</span>
          </div>
          <div className="info-item">
            <label>Email</label>
            <span>{user?.email}</span>
          </div>
        </div>
      </div>

      <style>{`
        .settings-page {
          max-width: 800px;
          margin: 0 auto;
        }

        .settings-section {
          background: white;
          border-radius: 8px;
          padding: 24px;
          margin-bottom: 24px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .settings-section h2 {
          margin: 0 0 8px 0;
          font-size: 18px;
          color: #333;
        }

        .settings-description {
          color: #666;
          margin-bottom: 20px;
        }

        .error-message {
          background: #fef2f2;
          color: #dc2626;
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 16px;
        }

        .success-message {
          background: #f0fdf4;
          color: #16a34a;
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 16px;
        }

        .logo-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 20px;
          border: 2px dashed #ddd;
          border-radius: 8px;
          background: #fafafa;
        }

        .current-logo {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .logo-preview {
          max-width: 200px;
          max-height: 100px;
          object-fit: contain;
        }

        .logo-actions {
          display: flex;
          gap: 12px;
        }

        .no-logo {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .logo-placeholder {
          color: #999;
          font-style: italic;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
        }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-primary {
          background: #2c5282;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #234876;
        }

        .btn-danger {
          background: #dc2626;
          color: white;
        }

        .btn-danger:hover:not(:disabled) {
          background: #b91c1c;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: #555;
        }

        .form-group input {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
        }

        .form-group input:focus {
          outline: none;
          border-color: #2c5282;
        }

        .info-grid {
          display: grid;
          gap: 16px;
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .info-item label {
          font-weight: 600;
          color: #666;
          font-size: 14px;
        }

        .info-item span {
          color: #333;
        }

        @media (max-width: 600px) {
          .form-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}
