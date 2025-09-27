import React from 'react';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

export function ResourceItem({ resource }) {
  return (
    <a 
      href={resource.file} 
      target="_blank" 
      rel="noopener noreferrer" 
      className="d-flex align-items-center text-decoration-none text-dark border-0 rounded-2 p-3 mb-3 bg-white position-relative"
      style={{
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        border: '1px solid #e9ecef'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-1px)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
      data-cy={`resource${resource.id}`}
    >
      {/* PDF Icon */}
      <div 
        className="d-flex align-items-center justify-content-center rounded-1 me-3 flex-shrink-0"
        style={{
          width: '40px',
          height: '40px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #e9ecef'
        }}
      >
        <PictureAsPdfIcon style={{ color: '#6c757d', fontSize: '20px' }} />
      </div>

      {/* Content */}
      <div className="flex-grow-1">
        <h6 className="mb-0 fw-medium text-truncate" style={{ color: '#495057' }}>
          {resource.name || 'Resource Document'}
        </h6>
      </div>

      {/* Action indicator */}
      <div className="ms-2 flex-shrink-0">
        <svg 
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          style={{ color: '#adb5bd' }}
        >
          <path 
            d="M10 6L8.59 7.41 13.17 12L8.59 16.59L10 18L16 12L10 6Z" 
            fill="currentColor"
          />
        </svg>
      </div>
    </a>
  );
}