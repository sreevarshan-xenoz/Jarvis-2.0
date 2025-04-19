import React from 'react';

const ErrorBoundary = ({ children, fallback }) => {
  const [hasError, setHasError] = React.useState(false);

  const handleError = React.useCallback(() => {
    setHasError(true);
  }, []);

  React.useEffect(() => {
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, [handleError]);

  if (hasError) {
    return fallback || null;
  }

  return children;
};

export default ErrorBoundary; 