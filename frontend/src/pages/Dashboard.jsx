import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title } from 'chart.js';
import { Doughnut, Line } from 'react-chartjs-2';
import { analyticsAPI } from '../services/api';
import { formatCurrency, formatPercentage } from '../utils/helpers';
import { TrendingUp, TrendingDown, DollarSign, Receipt, Wallet, PiggyBank } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title);

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [spendingByCategory, setSpendingByCategory] = useState([]);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('month');

  useEffect(() => {
    fetchData();
  }, [period]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [summaryRes, categoryRes, trendsRes] = await Promise.all([
        analyticsAPI.getSummary(period),
        analyticsAPI.getSpendingByCategory(period),
        analyticsAPI.getMonthlyTrends(),
      ]);

      setSummary(summaryRes.data);
      setSpendingByCategory(categoryRes.data.results || categoryRes.data);
      setMonthlyTrends(trendsRes.data.results || trendsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, change, color }) => (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>{formatPercentage(Math.abs(change))}</span>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-full ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );

  const categoryChartData = {
    labels: spendingByCategory.map(item => item.category),
    datasets: [
      {
        data: spendingByCategory.map(item => item.amount),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
          '#EC4899', '#06B6D4', '#F97316', '#14B8A6', '#6366F1',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const trendsChartData = {
    labels: monthlyTrends.map(item => item.month),
    datasets: [
      {
        label: 'Income',
        data: monthlyTrends.map(item => item.income),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Expenses',
        data: monthlyTrends.map(item => item.expenses),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Net',
        data: monthlyTrends.map(item => item.net),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="day">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
        </select>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={DollarSign}
          title="Total Income"
          value={formatCurrency(summary?.total_income || 0)}
          color="bg-green-500"
        />
        <StatCard
          icon={Receipt}
          title="Total Expenses"
          value={formatCurrency(summary?.total_expenses || 0)}
          color="bg-red-500"
        />
        <StatCard
          icon={PiggyBank}
          title="Net Savings"
          value={formatCurrency(summary?.net_savings || 0)}
          color="bg-blue-500"
        />
        <StatCard
          icon={Wallet}
          title="Transactions"
          value={summary?.transaction_count || 0}
          color="bg-purple-500"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending by Category */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Spending by Category</h2>
          {spendingByCategory.length > 0 ? (
            <div className="h-80 flex items-center justify-center">
              <Doughnut data={categoryChartData} options={{ maintainAspectRatio: false }} />
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No spending data available</p>
          )}
        </div>

        {/* Category List */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Top Categories</h2>
          <div className="space-y-3">
            {spendingByCategory.slice(0, 5).map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{item.category}</span>
                    <span className="text-sm text-gray-600">{formatCurrency(item.amount)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${item.percentage}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monthly Trends */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Monthly Trends</h2>
        {monthlyTrends.length > 0 ? (
          <div className="h-80">
            <Line
              data={trendsChartData}
              options={{
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                },
                scales: {
                  y: { beginAtZero: true },
                },
              }}
            />
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No trend data available</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
