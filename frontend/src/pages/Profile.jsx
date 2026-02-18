import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import { toast } from 'react-toastify';
import { User, Mail, Phone, DollarSign, Bell } from 'lucide-react';

const Profile = () => {
  const { user, checkAuth } = useAuth();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    currency: 'USD',
    monthly_budget: '',
    email_notifications: true,
    budget_alert_threshold: 80,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        currency: user.currency || 'USD',
        monthly_budget: user.monthly_budget || '',
        email_notifications: user.email_notifications ?? true,
        budget_alert_threshold: user.budget_alert_threshold || 80,
      });
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authAPI.updateProfile(formData);
      await checkAuth();
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <User className="w-5 h-5" />
              Personal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">First Name</label>
                <input
                  type="text"
                  className="input"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                />
              </div>

              <div>
                <label className="label">Last Name</label>
                <input
                  type="text"
                  className="input"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Contact Information
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div>
                <label className="label">Phone Number</label>
                <input
                  type="tel"
                  className="input"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>
          </div>

          {/* Financial Settings */}
          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Financial Settings
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Currency</label>
                <select
                  className="input"
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                >
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="INR">INR - Indian Rupee</option>
                </select>
              </div>

              <div>
                <label className="label">Monthly Budget</label>
                <input
                  type="number"
                  step="0.01"
                  className="input"
                  value={formData.monthly_budget}
                  onChange={(e) => setFormData({ ...formData, monthly_budget: e.target.value })}
                  placeholder="5000.00"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Set your overall monthly spending budget
                </p>
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notification Settings
            </h2>
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="email_notifications"
                  checked={formData.email_notifications}
                  onChange={(e) => setFormData({ ...formData, email_notifications: e.target.checked })}
                  className="mr-3 w-5 h-5"
                />
                <label htmlFor="email_notifications" className="text-gray-700">
                  Enable email notifications for budget alerts and reports
                </label>
              </div>

              <div>
                <label className="label">Budget Alert Threshold (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  className="input"
                  value={formData.budget_alert_threshold}
                  onChange={(e) => setFormData({ ...formData, budget_alert_threshold: e.target.value })}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Receive alerts when your spending reaches this percentage of your budget
                </p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-6">
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full py-3"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>

      {/* Account Information */}
      <div className="card bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
        <dl className="space-y-2">
          <div className="flex justify-between">
            <dt className="text-gray-600">Username:</dt>
            <dd className="font-medium text-gray-900">{user?.username}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-600">Member since:</dt>
            <dd className="font-medium text-gray-900">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
};

export default Profile;
