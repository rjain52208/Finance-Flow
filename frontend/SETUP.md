# Frontend Setup Guide

## Prerequisites

- Node.js 18+ and npm (or yarn)
- Backend API running at `http://localhost:8000`

## Step-by-Step Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

or with yarn:

```bash
yarn install
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

For production, update to your deployed backend URL.

### 4. Start Development Server

```bash
npm run dev
```

or with yarn:

```bash
yarn dev
```

The application will be available at: `http://localhost:3000`

### 5. Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` folder.

### 6. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   └── Layout.jsx    # Main layout with sidebar
│   ├── contexts/         # React contexts
│   │   └── AuthContext.jsx
│   ├── pages/            # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Transactions.jsx
│   │   ├── Budgets.jsx
│   │   ├── Analytics.jsx
│   │   └── Profile.jsx
│   ├── services/         # API services
│   │   └── api.js
│   ├── utils/            # Helper functions
│   │   └── helpers.js
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Key Features

### 1. Authentication
- JWT-based authentication
- Automatic token refresh
- Protected routes

### 2. Dashboard
- Financial summary with cards
- Doughnut chart for spending by category
- Line chart for monthly trends
- Period filtering (day, week, month, year)

### 3. Transactions
- Add/delete transactions
- Bulk CSV upload
- Auto-categorization
- Filtering and search
- Real-time updates

### 4. Budgets
- Create budgets per category
- Visual progress bars
- Alert thresholds
- Over-budget warnings

### 5. Analytics
- Detailed spending breakdown
- Bar and doughnut charts
- Category-wise analysis
- Savings rate calculation

### 6. Profile
- Update personal information
- Configure email notifications
- Set budget alert thresholds
- Currency preferences

## Technologies Used

- **React 18** - UI library
- **React Router v6** - Navigation
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Chart.js** - Data visualization
- **Axios** - HTTP client
- **React Toastify** - Notifications
- **Lucide React** - Icons

## Styling Guide

### Using Tailwind Classes

The project uses TailwindCSS for styling. Common patterns:

```jsx
// Button
<button className="btn btn-primary">Click me</button>

// Card
<div className="card">Content</div>

// Input
<input className="input" type="text" />

// Label
<label className="label">Field Name</label>
```

### Custom CSS Classes

Defined in `src/index.css`:

- `.btn` - Base button styles
- `.btn-primary` - Primary button
- `.btn-secondary` - Secondary button
- `.card` - Card container
- `.input` - Form input
- `.label` - Form label

## API Integration

### API Service (`src/services/api.js`)

The API service handles all HTTP requests:

```javascript
import api, { transactionsAPI } from './services/api';

// Get all transactions
const transactions = await transactionsAPI.getAll();

// Create transaction
await transactionsAPI.create({
  date: '2024-10-15',
  amount: 50.00,
  type: 'expense',
  description: 'Lunch',
});
```

### Available APIs

- `authAPI` - Authentication endpoints
- `transactionsAPI` - Transaction management
- `categoriesAPI` - Category management
- `budgetsAPI` - Budget management
- `analyticsAPI` - Analytics endpoints

## Common Tasks

### Add a New Page

1. Create component in `src/pages/`:

```jsx
// src/pages/NewPage.jsx
import React from 'react';

const NewPage = () => {
  return (
    <div>
      <h1>New Page</h1>
    </div>
  );
};

export default NewPage;
```

2. Add route in `src/App.jsx`:

```jsx
import NewPage from './pages/NewPage';

// Inside Routes
<Route path="/new-page" element={<NewPage />} />
```

3. Add navigation link in `src/components/Layout.jsx`:

```jsx
const menuItems = [
  // ... existing items
  { path: '/new-page', icon: IconName, label: 'New Page' },
];
```

### Add a New API Endpoint

In `src/services/api.js`:

```javascript
export const newAPI = {
  getAll: () => api.get('/new-endpoint/'),
  create: (data) => api.post('/new-endpoint/', data),
};
```

## Troubleshooting

### Issue 1: CORS Errors

**Error:** `Access to fetch at '...' has been blocked by CORS policy`

**Solution:**
- Ensure backend `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
- Check `vite.config.js` proxy settings

### Issue 2: API Not Found

**Error:** `404 Not Found`

**Solution:**
- Verify `VITE_API_URL` in `.env`
- Ensure backend is running
- Check API endpoint paths

### Issue 3: Authentication Not Working

**Solution:**
- Clear browser localStorage
- Check JWT token expiration
- Verify backend authentication settings

### Issue 4: Charts Not Rendering

**Solution:**
- Ensure Chart.js is properly registered
- Check data format matches chart requirements
- Verify chart container has defined height

## Deployment

### Deploying to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variables in Vercel dashboard:
   - `VITE_API_URL` = Your production API URL

### Deploying to Netlify

1. Build the project:
```bash
npm run build
```

2. Deploy `dist/` folder to Netlify

3. Set environment variables in Netlify dashboard

### Deploying to Static Hosting

After building:
```bash
npm run build
```

Upload the `dist/` folder to any static hosting service:
- AWS S3 + CloudFront
- GitHub Pages
- DigitalOcean Spaces
- Firebase Hosting

## Performance Optimization

- Code splitting with React.lazy()
- Image optimization
- Lazy loading for charts
- Memoization with React.memo()
- Virtual scrolling for long lists

## Best Practices

1. **Component Structure**
   - Keep components small and focused
   - Extract reusable logic to custom hooks
   - Use composition over inheritance

2. **State Management**
   - Use Context for global state
   - Keep local state when possible
   - Consider React Query for server state

3. **Error Handling**
   - Always handle API errors
   - Show user-friendly error messages
   - Use try-catch blocks

4. **Code Quality**
   - Follow ESLint rules
   - Use TypeScript (optional enhancement)
   - Write meaningful variable names

## Next Steps

1. Customize colors in `tailwind.config.js`
2. Add more visualizations
3. Implement real-time updates with WebSockets
4. Add export functionality (PDF, Excel)
5. Integrate with banking APIs (Plaid)
