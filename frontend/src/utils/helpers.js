export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatPercentage = (value) => {
  return `${value.toFixed(1)}%`;
};

export const getTransactionTypeColor = (type) => {
  const colors = {
    income: 'text-green-600',
    expense: 'text-red-600',
    investment: 'text-blue-600',
  };
  return colors[type] || 'text-gray-600';
};

export const getCategoryIcon = (icon) => {
  return icon || '📊';
};
