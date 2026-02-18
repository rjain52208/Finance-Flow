import React, { useState, useEffect } from 'react';
import { budgetsAPI, categoriesAPI } from '../services/api';
import { formatCurrency, formatPercentage } from '../utils/helpers';
import { toast } from 'react-toastify';
import { Plus, AlertCircle, CheckCircle } from 'lucide-react';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
    period: 'monthly',
    start_date: new Date().toISOString().split('T')[0],
    alert_enabled: true,
    alert_threshold: 80,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [budgetsRes, categoriesRes] = await Promise.all([
        budgetsAPI.getAll(),
        categoriesAPI.getAll(),
      ]);
      setBudgets(budgetsRes.data.results || budgetsRes.data);
      setCategories((categoriesRes.data.results || categoriesRes.data).filter(cat => cat.type === 'expense'));
    } catch (error) {
      toast.error('Failed to fetch budgets');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await budgetsAPI.create(formData);
      toast.success('Budget created successfully!');
      setShowModal(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error('Failed to create budget');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this budget?')) {
      try {
        await budgetsAPI.delete(id);
        toast.success('Budget deleted');
        fetchData();
      } catch (error) {
        toast.error('Failed to delete budget');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      category: '',
      amount: '',
      period: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      alert_enabled: true,
      alert_threshold: 80,
    });
  };

  const getBudgetStatus = (percentage) => {
    if (percentage >= 100) return { color: 'bg-red-500', status: 'Over Budget' };
    if (percentage >= 80) return { color: 'bg-yellow-500', status: 'Warning' };
    return { color: 'bg-green-500', status: 'On Track' };
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Budgets</h1>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Create Budget
        </button>
      </div>

      {/* Budgets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {budgets.map((budget) => {
          const status = getBudgetStatus(budget.percentage_used);
          
          return (
            <div key={budget.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {budget.category_name}
                  </h3>
                  <p className="text-sm text-gray-600 capitalize">{budget.period}</p>
                </div>
                {budget.is_over_budget ? (
                  <AlertCircle className="w-6 h-6 text-red-500" />
                ) : (
                  <CheckCircle className="w-6 h-6 text-green-500" />
                )}
              </div>

              <div className="space-y-3">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl font-bold text-gray-900">
                      {formatCurrency(budget.current_spending)}
                    </span>
                    <span className="text-sm text-gray-600">
                      of {formatCurrency(budget.amount)}
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`${status.color} h-3 rounded-full transition-all duration-300`}
                      style={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm font-medium" style={{ color: status.color.replace('bg-', '') }}>
                      {status.status}
                    </span>
                    <span className="text-sm text-gray-600">
                      {formatPercentage(budget.percentage_used)}
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    Remaining: {formatCurrency(Math.max(0, budget.amount - budget.current_spending))}
                  </span>
                  <button
                    onClick={() => handleDelete(budget.id)}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {budgets.length === 0 && !loading && (
          <div className="col-span-full text-center py-12 text-gray-500">
            <p>No budgets created yet. Create your first budget to start tracking!</p>
          </div>
        )}
      </div>

      {/* Create Budget Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-6">Create Budget</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Category</label>
                <select
                  className="input"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                >
                  <option value="">Select category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Budget Amount</label>
                <input
                  type="number"
                  step="0.01"
                  className="input"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="label">Period</label>
                <select
                  className="input"
                  value={formData.period}
                  onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>

              <div>
                <label className="label">Start Date</label>
                <input
                  type="date"
                  className="input"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="label">Alert Threshold (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  className="input"
                  value={formData.alert_threshold}
                  onChange={(e) => setFormData({ ...formData, alert_threshold: e.target.value })}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Get notified when spending reaches this percentage
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="alert_enabled"
                  checked={formData.alert_enabled}
                  onChange={(e) => setFormData({ ...formData, alert_enabled: e.target.checked })}
                  className="mr-2"
                />
                <label htmlFor="alert_enabled" className="text-sm text-gray-700">
                  Enable email alerts
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button type="submit" className="btn btn-primary flex-1">
                  Create Budget
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="btn btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budgets;
