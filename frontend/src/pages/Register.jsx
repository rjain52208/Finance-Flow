import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { DollarSign } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.password_confirm) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await register(formData);
      toast.success('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      const errors = error.response?.data;
      if (errors) {
        Object.keys(errors).forEach((key) => {
          toast.error(`${key}: ${errors[key]}`);
        });
      } else {
        toast.error('Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="flex justify-center mb-6">
          <div className="bg-primary-100 p-3 rounded-full">
            <DollarSign className="w-12 h-12 text-primary-600" />
          </div>
        </div>
        
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-2">
          Create Account
        </h2>
        <p className="text-center text-gray-600 mb-8">
          Start managing your finances today
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">First Name</label>
              <input
                type="text"
                name="first_name"
                className="input"
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="label">Last Name</label>
              <input
                type="text"
                name="last_name"
                className="input"
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div>
            <label className="label">Username</label>
            <input
              type="text"
              name="username"
              className="input"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label className="label">Email</label>
            <input
              type="email"
              name="email"
              className="input"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label className="label">Password</label>
            <input
              type="password"
              name="password"
              className="input"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
            />
          </div>

          <div>
            <label className="label">Confirm Password</label>
            <input
              type="password"
              name="password_confirm"
              className="input"
              value={formData.password_confirm}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn btn-primary py-3 text-lg mt-6"
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <p className="text-center text-gray-600 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
