import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { analyticsAPI } from '../services/api';
import { formatCurrency, formatPercentage } from '../utils/helpers';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Analytics = () => {
  const [period, setPeriod] = useState('month');
  const [summary, setSummary] = useState(null);
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [period]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [summaryRes, categoryRes] = await Promise.all([
        analyticsAPI.getSummary(period),
        analyticsAPI.getSpendingByCategory(period),
      ]);
      setSummary(summaryRes.data);
      setCategoryData(categoryRes.data.results || categoryRes.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryChartData = {
    labels: categoryData.map(item => item.category),
    datasets: [
      {
        label: 'Spending',
        data: categoryData.map(item => item.amount),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
          '#EC4899', '#06B6D4', '#F97316', '#14B8A6', '#6366F1',
        ],
      },
    ],
  };

  const savingsRate = summary 
    ? ((summary.net_savings / summary.total_income) * 100).toFixed(1)
    : 0;

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <h3 className="text-lg font-medium mb-2">Total Income</h3>
          <p className="text-3xl font-bold">{formatCurrency(summary?.total_income || 0)}</p>
        </div>

        <div className="card bg-gradient-to-br from-red-500 to-red-600 text-white">
          <h3 className="text-lg font-medium mb-2">Total Expenses</h3>
          <p className="text-3xl font-bold">{formatCurrency(summary?.total_expenses || 0)}</p>
        </div>

        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <h3 className="text-lg font-medium mb-2">Net Savings</h3>
          <p className="text-3xl font-bold">{formatCurrency(summary?.net_savings || 0)}</p>
          <p className="text-sm mt-2">Savings Rate: {savingsRate}%</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending Breakdown */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Spending Breakdown</h2>
          {categoryData.length > 0 ? (
            <div className="h-80 flex items-center justify-center">
              <Doughnut
                data={categoryChartData}
                options={{
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { position: 'bottom' },
                  },
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>

        {/* Category Bar Chart */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Spending by Category</h2>
          {categoryData.length > 0 ? (
            <div className="h-80">
              <Bar
                data={categoryChartData}
                options={{
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                  },
                  scales: {
                    y: { beginAtZero: true },
                  },
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>
      </div>

      {/* Detailed Category Table */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Category Details</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">% of Total</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg per Transaction</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {categoryData.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    {formatCurrency(item.amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                    {item.count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                    {formatPercentage(item.percentage)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                    {formatCurrency(item.amount / item.count)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
