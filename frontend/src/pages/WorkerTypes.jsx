import { useState, useEffect } from 'react';
import { getWorkerTypes, createWorkerType, updateWorkerType, deleteWorkerType } from '../services/api';
import Modal from '../components/Modal';

export default function WorkerTypes() {
  const [workerTypes, setWorkerTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ name: '', hourly_rate: '' });

  useEffect(() => {
    loadWorkerTypes();
  }, []);

  const loadWorkerTypes = async () => {
    try {
      const res = await getWorkerTypes();
      setWorkerTypes(res.data);
    } catch (err) {
      console.error('Failed to load worker types', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...formData, hourly_rate: parseFloat(formData.hourly_rate) };
      if (editingId) {
        await updateWorkerType(editingId, data);
      } else {
        await createWorkerType(data);
      }
      closeModal();
      loadWorkerTypes();
    } catch (err) {
      console.error('Failed to save worker type', err);
    }
  };

  const handleEdit = (wt) => {
    setEditingId(wt.id);
    setFormData({ name: wt.name, hourly_rate: wt.hourly_rate.toString() });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this worker type?')) return;
    try {
      await deleteWorkerType(id);
      loadWorkerTypes();
    } catch (err) {
      console.error('Failed to delete worker type', err);
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ name: '', hourly_rate: '' });
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="worker-types-page">
      <div className="page-header">
        <h1>Worker Types</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          Add Worker Type
        </button>
      </div>

      <p className="page-description">
        Define different worker categories and their hourly rates. These will be used when logging time on projects.
      </p>

      {workerTypes.length === 0 ? (
        <p className="empty-state">
          No worker types defined. Add some to start tracking time by worker category.
        </p>
      ) : (
        <div className="worker-types-grid">
          {workerTypes.map((wt) => (
            <div key={wt.id} className="worker-type-card">
              <div className="worker-type-info">
                <h3>{wt.name}</h3>
                <p className="rate">€{wt.hourly_rate.toFixed(2)} / hour</p>
              </div>
              <div className="worker-type-actions">
                <button className="btn btn-secondary btn-sm" onClick={() => handleEdit(wt)}>
                  Edit
                </button>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(wt.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editingId ? 'Edit Worker Type' : 'Add Worker Type'}
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Electrician, Plumber, General Labor"
              required
            />
          </div>
          <div className="form-group">
            <label>Hourly Rate (€) *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.hourly_rate}
              onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
              placeholder="e.g., 75.00"
              required
            />
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={closeModal}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {editingId ? 'Save' : 'Create'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
