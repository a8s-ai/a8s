import { VncScreen } from 'react-vnc';
import { useRef, useEffect, useState, CSSProperties } from 'react';
import { isValidServiceUrl } from '@/lib/utils';

const defaultStyles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  } as CSSProperties,
  screen: {
    width: '75vw',
    height: '75vh',
  } as CSSProperties,
  error: {
    padding: '1rem',
    color: '#dc2626',
    backgroundColor: '#fef2f2',
    borderRadius: '0.5rem',
  } as CSSProperties,
  loading: {
    padding: '1rem',
    color: '#4b5563',
  } as CSSProperties,
};

interface VNCViewerProps {
  serviceUrl: string;
  styles?: {
    container?: CSSProperties;
    screen?: CSSProperties;
    error?: CSSProperties;
    loading?: CSSProperties;
  };
}

const VNCViewer: React.FC<VNCViewerProps> = ({
  serviceUrl,
  styles = {},
}) => {
  const ref = useRef();
  const [error, setError] = useState<string | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!serviceUrl) {
      setError('Service URL is required');
      return;
    }
    
    if (!isValidServiceUrl(serviceUrl)) {
      setError('Invalid connection URL format. Expected format: service-name.namespace.svc.cluster.local');
      return;
    }

    setError(null);
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    setWsUrl(`${protocol}//${window.location.host}/${serviceUrl}/websockify`);
  }, [serviceUrl]);

  if (error) {
    return (
      <div style={{ ...defaultStyles.container, ...defaultStyles.error, ...styles.container, ...styles.error }}>
        <p className="font-medium">Error:</p>
        <p>{error}</p>
      </div>
    );
  }

  if (!wsUrl) {
    return (
      <div style={{ ...defaultStyles.container, ...defaultStyles.loading, ...styles.container, ...styles.loading }}>
        Validating connection...
      </div>
    );
  }

  return (
    <div style={{ ...defaultStyles.container, ...styles.container }}>
      <VncScreen
        url={wsUrl}
        scaleViewport
        background="#000000"
        style={{ ...defaultStyles.screen, ...styles.screen }}
        ref={ref as any}
      />
    </div>
  );
};

export default VNCViewer;
