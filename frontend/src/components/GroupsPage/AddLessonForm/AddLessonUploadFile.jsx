import React, { useRef, useState } from 'react';

/**
 * FileUploadField Component
 * 
 * A Material Design styled file upload field that supports single or multiple files.
 * 
 * @param {Object} props
 * @param {File[]} props.files - Array of currently selected files
 * @param {Function} props.onChange - Callback when files change: (files: File[]) => void
 * @param {boolean} props.multiple - Whether to allow multiple file selection (default: false)
 * @param {string} props.accept - File type filter (e.g., "image/*", ".pdf,.doc")
 * @param {number} props.maxFiles - Maximum number of files allowed (only used if multiple=true)
 * @param {string} props.label - Label text for the field
 * @param {boolean} props.disabled - Whether the field is disabled
 * @param {string} props.helperText - Helper text shown below the field
 * @param {string} props.error - Error message to display
 */
export const FileUploadField = ({ 
  files = [], 
  onChange, 
  multiple = false,
  accept = "*",
  maxFiles = null,
  label = "Upload Files",
  disabled = false,
  helperText = "",
  error = ""
}) => {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  // Handle file selection from input
  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    handleFiles(selectedFiles);
  };

  // Handle files from either input or drag-drop
  const handleFiles = (newFiles) => {
    if (disabled) return;

    let updatedFiles;
    
    if (multiple) {
      // Add new files to existing ones
      updatedFiles = [...files, ...newFiles];
      
      // Enforce max files limit if specified
      if (maxFiles && updatedFiles.length > maxFiles) {
        updatedFiles = updatedFiles.slice(0, maxFiles);
      }
    } else {
      // Single file mode - replace existing file
      updatedFiles = newFiles.slice(0, 1);
    }

    onChange(updatedFiles);
    
    // Reset input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Remove a specific file
  const handleRemoveFile = (indexToRemove) => {
    const updatedFiles = files.filter((_, index) => index !== indexToRemove);
    onChange(updatedFiles);
  };

  // Drag and drop handlers
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  // Format file size for display
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="mb-3">
      {/* Label */}
      {label && (
        <label className="form-label text-secondary fw-medium small">
          {label}
        </label>
      )}

      {/* Drop Zone */}
      <div
        className={`border rounded p-4 text-center position-relative ${
          isDragging ? 'border-primary bg-light' : 'border-secondary'
        } ${disabled ? 'opacity-50' : 'cursor-pointer'} ${
          error ? 'border-danger' : ''
        }`}
        style={{
          transition: 'all 0.2s ease',
          cursor: disabled ? 'not-allowed' : 'pointer'
        }}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="d-none"
          multiple={multiple}
          accept={accept}
          onChange={handleFileSelect}
          disabled={disabled}
        />

        {/* Upload Icon */}
        <svg 
          width="48" 
          height="48" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          className={`mx-auto mb-3 ${error ? 'text-danger' : 'text-primary'}`}
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>

        <p className="mb-1 fw-medium">
          {isDragging ? 'Drop files here' : 'Click to upload or drag and drop'}
        </p>
        <p className="text-muted small mb-0">
          {multiple ? 'Select one or more files' : 'Select a file'}
          {maxFiles && ` (max ${maxFiles})`}
        </p>
      </div>

      {/* Helper Text or Error */}
      {(helperText || error) && (
        <div className={`form-text small mt-1 ${error ? 'text-danger' : 'text-muted'}`}>
          {error || helperText}
        </div>
      )}

      {/* Selected Files List */}
      {files.length > 0 && (
        <div className="mt-3">
          {files.map((file, index) => (
            <div
              key={index}
              className="d-flex align-items-center justify-content-between p-3 mb-2 border rounded bg-light"
              style={{ transition: 'all 0.2s ease' }}
            >
              <div className="d-flex align-items-center flex-grow-1 overflow-hidden">
                {/* File Icon */}
                <svg 
                  width="24" 
                  height="24" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2"
                  className="text-primary flex-shrink-0"
                >
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                  <polyline points="13 2 13 9 20 9" />
                </svg>

                {/* File Info */}
                <div className="ms-3 overflow-hidden">
                  <p className="mb-0 fw-medium text-truncate" style={{ maxWidth: '300px' }}>
                    {file.name}
                  </p>
                  <p className="mb-0 text-muted small">
                    {formatFileSize(file.size)}
                  </p>
                </div>
              </div>

              {/* Remove Button */}
              {!disabled && (
                <button
                  type="button"
                  className="btn btn-sm btn-outline-danger ms-2 flex-shrink-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile(index);
                  }}
                  aria-label={`Remove ${file.name}`}
                >
                  <svg 
                    width="16" 
                    height="16" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                  >
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};