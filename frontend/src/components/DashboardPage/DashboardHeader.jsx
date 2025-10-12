// components/DashboardPage/DashboardHeader.jsx
import { useState } from 'react';

export default function DashboardHeader({ dateRange, onDateRangeChange }) {
  const [showCustomRange, setShowCustomRange] = useState(false);
  const [customStart, setCustomStart] = useState(dateRange.start);
  const [customEnd, setCustomEnd] = useState(dateRange.end);

  // Preset date ranges
  const presetRanges = [
    {
      label: 'Last 30 Days',
      getValue: () => {
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - 30);
        return {
          start: start.toISOString().split('T')[0],
          end: end.toISOString().split('T')[0]
        };
      }
    },
    {
      label: 'Last 90 Days',
      getValue: () => {
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - 90);
        return {
          start: start.toISOString().split('T')[0],
          end: end.toISOString().split('T')[0]
        };
      }
    },
    {
      label: 'This Year',
      getValue: () => {
        const end = new Date();
        const start = new Date(end.getFullYear(), 0, 1);
        return {
          start: start.toISOString().split('T')[0],
          end: end.toISOString().split('T')[0]
        };
      }
    }
  ];

  const handlePresetClick = (preset) => {
    const newRange = preset.getValue();
    onDateRangeChange(newRange);
    setShowCustomRange(false);
  };

  const handleCustomRangeSubmit = (e) => {
    e.preventDefault();
    onDateRangeChange({
      start: customStart,
      end: customEnd
    });
    setShowCustomRange(false);
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  return (
    <div className="mb-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h1 className="h2 mb-1" style={{ color: '#004aad', fontWeight: 600 }}>
            Dashboard
          </h1>
          <p className="text-muted mb-0">
            {formatDate(dateRange.start)} - {formatDate(dateRange.end)}
          </p>
        </div>

        <div className="btn-group">
          {presetRanges.map((preset, index) => (
            <button
              key={index}
              type="button"
              className="btn btn-outline-primary"
              onClick={() => handlePresetClick(preset)}
            >
              {preset.label}
            </button>
          ))}
          <button
            type="button"
            className={`btn ${showCustomRange ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setShowCustomRange(!showCustomRange)}
          >
            Custom Range
          </button>
        </div>
      </div>

      {/* Custom Date Range Picker */}
      {showCustomRange && (
        <div className="card mb-3">
          <div className="card-body">
            <form onSubmit={handleCustomRangeSubmit} className="row g-3 align-items-end">
              <div className="col-md-4">
                <label htmlFor="startDate" className="form-label">Start Date</label>
                <input
                  type="date"
                  className="form-control"
                  id="startDate"
                  value={customStart}
                  onChange={(e) => setCustomStart(e.target.value)}
                  max={customEnd}
                  required
                />
              </div>
              <div className="col-md-4">
                <label htmlFor="endDate" className="form-label">End Date</label>
                <input
                  type="date"
                  className="form-control"
                  id="endDate"
                  value={customEnd}
                  onChange={(e) => setCustomEnd(e.target.value)}
                  min={customStart}
                  max={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>
              <div className="col-md-4">
                <button type="submit" className="btn btn-primary me-2">
                  Apply
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setShowCustomRange(false)}
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
}