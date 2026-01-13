import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  getProject,
  updateProject,
  getWorkerTypes,
  createTimeEntry,
  deleteTimeEntry,
  createMaterial,
  deleteMaterial,
  getReportUrl,
  sendOfferEmail,
} from '../services/api';
import Modal from '../components/Modal';

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [workerTypes, setWorkerTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTimeModal, setShowTimeModal] = useState(false);
  const [showMaterialModal, setShowMaterialModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [formError, setFormError] = useState('');
  const [emailSending, setEmailSending] = useState(false);
  const [emailSuccess, setEmailSuccess] = useState('');

  const [emailForm, setEmailForm] = useState({
    to_email: '',
    subject: '',
    message: '',
  });

  const [timeForm, setTimeForm] = useState({
    worker_type_id: '',
    hours: '',
    date: new Date().toISOString().split('T')[0],
    description: '',
  });

  const [materialForm, setMaterialForm] = useState({
    name: '',
    quantity: '',
    unit: 'pcs',
    unit_price: '',
    supplier: '',
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [projectRes, workerTypesRes] = await Promise.all([
        getProject(id),
        getWorkerTypes(),
      ]);
      setProject(projectRes.data);
      setEditData(projectRes.data);
      setWorkerTypes(workerTypesRes.data);
    } catch (err) {
      console.error('Failed to load project', err);
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProject = async () => {
    setFormError('');
    try {
      await updateProject(id, editData);
      setEditing(false);
      loadData();
    } catch (err) {
      console.error('Failed to update project', err);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setFormError(detail.map(e => e.msg).join(', '));
      } else {
        setFormError(detail || 'Failed to update project');
      }
    }
  };

  const handleAddTimeEntry = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!timeForm.worker_type_id || !timeForm.hours) {
      setFormError('Please select a worker type and enter hours');
      return;
    }

    try {
      const data = {
        worker_type_id: parseInt(timeForm.worker_type_id),
        hours: parseFloat(timeForm.hours),
      };
      if (timeForm.date) data.date = timeForm.date;
      if (timeForm.description) data.description = timeForm.description;

      await createTimeEntry(id, data);
      setShowTimeModal(false);
      setTimeForm({ worker_type_id: '', hours: '', date: new Date().toISOString().split('T')[0], description: '' });
      loadData();
    } catch (err) {
      console.error('Failed to add time entry', err);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setFormError(detail.map(e => e.msg).join(', '));
      } else {
        setFormError(detail || 'Failed to add time entry');
      }
    }
  };

  const handleDeleteTimeEntry = async (entryId) => {
    if (!confirm('Delete this time entry?')) return;
    try {
      await deleteTimeEntry(entryId);
      loadData();
    } catch (err) {
      console.error('Failed to delete time entry', err);
    }
  };

  const handleAddMaterial = async (e) => {
    e.preventDefault();
    try {
      await createMaterial(id, {
        ...materialForm,
        quantity: parseFloat(materialForm.quantity),
        unit_price: parseFloat(materialForm.unit_price),
      });
      setShowMaterialModal(false);
      setMaterialForm({ name: '', quantity: '', unit: 'pcs', unit_price: '', supplier: '' });
      loadData();
    } catch (err) {
      console.error('Failed to add material', err);
    }
  };

  const handleDeleteMaterial = async (materialId) => {
    if (!confirm('Delete this material?')) return;
    try {
      await deleteMaterial(materialId);
      loadData();
    } catch (err) {
      console.error('Failed to delete material', err);
    }
  };

  const getWorkerTypeName = (id) => {
    const wt = workerTypes.find((w) => w.id === id);
    return wt ? wt.name : 'Unknown';
  };

  const getWorkerTypeRate = (id) => {
    const wt = workerTypes.find((w) => w.id === id);
    return wt ? wt.hourly_rate : 0;
  };

  const calculateLaborTotal = () => {
    return project?.time_entries?.reduce((sum, entry) => {
      return sum + entry.hours * getWorkerTypeRate(entry.worker_type_id);
    }, 0) || 0;
  };

  const calculateMaterialTotal = () => {
    return project?.materials?.reduce((sum, mat) => {
      return sum + mat.quantity * mat.unit_price;
    }, 0) || 0;
  };

  const openReport = (format) => {
    const token = localStorage.getItem('token');
    const url = getReportUrl(id, format);
    window.open(`${url}&token=${token}`, '_blank');
  };

  const openEmailModal = () => {
    setEmailForm({
      to_email: project.customer_email || '',
      subject: '',
      message: '',
    });
    setFormError('');
    setEmailSuccess('');
    setShowEmailModal(true);
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    setFormError('');
    setEmailSuccess('');
    setEmailSending(true);

    try {
      const data = { to_email: emailForm.to_email };
      if (emailForm.subject) data.subject = emailForm.subject;
      if (emailForm.message) data.message = emailForm.message;

      await sendOfferEmail(id, data);
      setEmailSuccess('Email sent successfully!');
      setTimeout(() => {
        setShowEmailModal(false);
        setEmailSuccess('');
      }, 2000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(detail || 'Failed to send email');
    } finally {
      setEmailSending(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!project) return <div className="error">Project not found</div>;

  return (
    <div className="project-detail">
      <div className="page-header">
        <div>
          <h1>{project.name}</h1>
          <span className={`status-badge status-${project.status}`}>{project.status}</span>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => { setEditing(!editing); setFormError(''); }}>
            {editing ? 'Cancel' : 'Edit'}
          </button>
          <button className="btn btn-primary" onClick={() => openReport('html')}>
            View Report
          </button>
          <button className="btn btn-primary" onClick={openEmailModal}>
            Send Email
          </button>
          <a
            href={getReportUrl(id, 'pdf')}
            target="_blank"
            className="btn btn-primary"
            onClick={(e) => {
              e.preventDefault();
              const token = localStorage.getItem('token');
              fetch(getReportUrl(id, 'pdf'), {
                headers: { Authorization: `Bearer ${token}` },
              })
                .then((res) => res.blob())
                .then((blob) => {
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `offer_${project.name.replace(/ /g, '_')}.pdf`;
                  a.click();
                });
            }}
          >
            Download PDF
          </a>
        </div>
      </div>

      {editing ? (
        <div className="edit-form">
          {formError && <div className="error">{formError}</div>}
          <div className="form-grid">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={editData.name}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Status</label>
              <select
                value={editData.status}
                onChange={(e) => setEditData({ ...editData, status: e.target.value })}
              >
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div className="form-group full-width">
              <label>Description</label>
              <textarea
                value={editData.description || ''}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Customer Name</label>
              <input
                type="text"
                value={editData.customer_name || ''}
                onChange={(e) => setEditData({ ...editData, customer_name: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Customer Email</label>
              <input
                type="email"
                value={editData.customer_email || ''}
                onChange={(e) => setEditData({ ...editData, customer_email: e.target.value })}
              />
            </div>
            <div className="form-group full-width">
              <label>Customer Address</label>
              <textarea
                value={editData.customer_address || ''}
                onChange={(e) => setEditData({ ...editData, customer_address: e.target.value })}
              />
            </div>
            <div className="form-group full-width">
              <label>Offer Terms (appears in report footer)</label>
              <textarea
                value={editData.offer_terms || ''}
                onChange={(e) => setEditData({ ...editData, offer_terms: e.target.value })}
                rows={5}
                placeholder="Enter terms and conditions for this offer..."
              />
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleUpdateProject}>Save Changes</button>
        </div>
      ) : (
        <div className="project-info-section">
          <p><strong>Description:</strong> {project.description || 'N/A'}</p>
          <p><strong>Customer:</strong> {project.customer_name || 'N/A'}</p>
          <p><strong>Email:</strong> {project.customer_email || 'N/A'}</p>
          <p><strong>Address:</strong> {project.customer_address || 'N/A'}</p>
          {project.offer_terms && (
            <div className="offer-terms-display">
              <strong>Offer Terms:</strong>
              <pre>{project.offer_terms}</pre>
            </div>
          )}
        </div>
      )}

      <div className="section">
        <div className="section-header">
          <h2>Time Entries</h2>
          <button className="btn btn-secondary" onClick={() => setShowTimeModal(true)}>
            Add Time
          </button>
        </div>
        {project.time_entries?.length === 0 ? (
          <p className="empty-state">No time entries yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Worker Type</th>
                <th>Hours</th>
                <th>Rate</th>
                <th>Cost</th>
                <th>Description</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {project.time_entries?.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.date}</td>
                  <td>{getWorkerTypeName(entry.worker_type_id)}</td>
                  <td>{entry.hours}</td>
                  <td>€{getWorkerTypeRate(entry.worker_type_id).toFixed(2)}/hr</td>
                  <td>€{(entry.hours * getWorkerTypeRate(entry.worker_type_id)).toFixed(2)}</td>
                  <td>{entry.description || '-'}</td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteTimeEntry(entry.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              <tr className="total-row">
                <td colSpan="4"><strong>Labor Subtotal</strong></td>
                <td colSpan="3"><strong>€{calculateLaborTotal().toFixed(2)}</strong></td>
              </tr>
            </tbody>
          </table>
        )}
      </div>

      <div className="section">
        <div className="section-header">
          <h2>Materials</h2>
          <button className="btn btn-secondary" onClick={() => setShowMaterialModal(true)}>
            Add Material
          </button>
        </div>
        {project.materials?.length === 0 ? (
          <p className="empty-state">No materials yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Material</th>
                <th>Quantity</th>
                <th>Unit</th>
                <th>Unit Price</th>
                <th>Cost</th>
                <th>Supplier</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {project.materials?.map((mat) => (
                <tr key={mat.id}>
                  <td>{mat.name}</td>
                  <td>{mat.quantity}</td>
                  <td>{mat.unit}</td>
                  <td>€{mat.unit_price.toFixed(2)}</td>
                  <td>€{(mat.quantity * mat.unit_price).toFixed(2)}</td>
                  <td>{mat.supplier || '-'}</td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteMaterial(mat.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              <tr className="total-row">
                <td colSpan="4"><strong>Material Subtotal</strong></td>
                <td colSpan="3"><strong>€{calculateMaterialTotal().toFixed(2)}</strong></td>
              </tr>
            </tbody>
          </table>
        )}
      </div>

      <div className="grand-total">
        <h2>Grand Total: €{(calculateLaborTotal() + calculateMaterialTotal()).toFixed(2)}</h2>
      </div>

      <Modal isOpen={showTimeModal} onClose={() => { setShowTimeModal(false); setFormError(''); }} title="Add Time Entry">
        <form onSubmit={handleAddTimeEntry}>
          {formError && <div className="error">{formError}</div>}
          <div className="form-group">
            <label>Worker Type *</label>
            <select
              value={timeForm.worker_type_id}
              onChange={(e) => setTimeForm({ ...timeForm, worker_type_id: e.target.value })}
              required
            >
              <option value="">Select worker type</option>
              {workerTypes.map((wt) => (
                <option key={wt.id} value={wt.id}>
                  {wt.name} (€{wt.hourly_rate}/hr)
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Hours *</label>
            <input
              type="number"
              step="0.5"
              min="0"
              value={timeForm.hours}
              onChange={(e) => setTimeForm({ ...timeForm, hours: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Date</label>
            <input
              type="date"
              value={timeForm.date}
              onChange={(e) => setTimeForm({ ...timeForm, date: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <input
              type="text"
              value={timeForm.description}
              onChange={(e) => setTimeForm({ ...timeForm, description: e.target.value })}
            />
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setShowTimeModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">Add</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={showMaterialModal} onClose={() => setShowMaterialModal(false)} title="Add Material">
        <form onSubmit={handleAddMaterial}>
          <div className="form-group">
            <label>Material Name *</label>
            <input
              type="text"
              value={materialForm.name}
              onChange={(e) => setMaterialForm({ ...materialForm, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Quantity *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={materialForm.quantity}
              onChange={(e) => setMaterialForm({ ...materialForm, quantity: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Unit *</label>
            <select
              value={materialForm.unit}
              onChange={(e) => setMaterialForm({ ...materialForm, unit: e.target.value })}
            >
              <option value="pcs">Pieces</option>
              <option value="m">Meters</option>
              <option value="m2">Square Meters</option>
              <option value="kg">Kilograms</option>
              <option value="l">Liters</option>
              <option value="box">Boxes</option>
            </select>
          </div>
          <div className="form-group">
            <label>Unit Price (€) *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={materialForm.unit_price}
              onChange={(e) => setMaterialForm({ ...materialForm, unit_price: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Supplier</label>
            <input
              type="text"
              value={materialForm.supplier}
              onChange={(e) => setMaterialForm({ ...materialForm, supplier: e.target.value })}
            />
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setShowMaterialModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">Add</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={showEmailModal} onClose={() => setShowEmailModal(false)} title="Send Offer via Email">
        <form onSubmit={handleSendEmail}>
          {formError && <div className="error">{formError}</div>}
          {emailSuccess && <div className="success">{emailSuccess}</div>}
          <div className="form-group">
            <label>Recipient Email *</label>
            <input
              type="email"
              value={emailForm.to_email}
              onChange={(e) => setEmailForm({ ...emailForm, to_email: e.target.value })}
              required
              placeholder="customer@example.com"
            />
          </div>
          <div className="form-group">
            <label>Subject (optional)</label>
            <input
              type="text"
              value={emailForm.subject}
              onChange={(e) => setEmailForm({ ...emailForm, subject: e.target.value })}
              placeholder="Leave empty for default subject"
            />
          </div>
          <div className="form-group">
            <label>Message (optional)</label>
            <textarea
              value={emailForm.message}
              onChange={(e) => setEmailForm({ ...emailForm, message: e.target.value })}
              rows={5}
              placeholder="Leave empty for default message"
            />
          </div>
          <p className="email-note">The PDF offer will be attached. You will receive a copy (CC).</p>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setShowEmailModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={emailSending}>
              {emailSending ? 'Sending...' : 'Send Email'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
