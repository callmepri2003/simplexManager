
import React from 'react';

export default function ErrorPage({ 
  code = '401', 
  title = 'Unauthorized', 
  message = 'You don\'t have permission to access this resource.',
  onAction,
  actionText = 'Go Back'
}){
  const styles = {
    container: {
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#fafafa',
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      padding: '16px'
    },
    card: {
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
      padding: '48px 32px',
      textAlign: 'center',
      maxWidth: '400px',
      width: '100%'
    },
    code: {
      fontSize: '3rem',
      fontWeight: 300,
      color: '#f44336',
      margin: '0 0 16px 0',
      lineHeight: 1
    },
    title: {
      fontSize: '1.5rem',
      fontWeight: 400,
      color: 'rgba(0, 0, 0, 0.87)',
      margin: '0 0 8px 0'
    },
    message: {
      fontSize: '1rem',
      fontWeight: 400,
      color: 'rgba(0, 0, 0, 0.6)',
      margin: '0 0 32px 0',
      lineHeight: 1.5
    },
    button: {
      backgroundColor: '#1976d2',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      padding: '10px 16px',
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'uppercase',
      cursor: 'pointer',
      transition: 'background-color 250ms cubic-bezier(0.4, 0, 0.2, 1) 0ms, box-shadow 250ms cubic-bezier(0.4, 0, 0.2, 1) 0ms',
      fontFamily: 'inherit',
      outline: 'none'
    },
    buttonHover: {
      backgroundColor: '#1565c0',
      boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)'
    }
  };

  const [isHovered, setIsHovered] = React.useState(false);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.code}>{code}</h1>
        <h2 style={styles.title}>{title}</h2>
        <p style={styles.message}>{message}</p>
        {onAction && (
          <button
            style={{
              ...styles.button,
              ...(isHovered ? styles.buttonHover : {})
            }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onClick={onAction}
          >
            {actionText}
          </button>
        )}
      </div>
    </div>
  );
};