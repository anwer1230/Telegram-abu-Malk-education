import React from 'react';
import { SenderModal } from './SenderModal';

export const MonitorModal: React.FC = () => {
  // MonitorModal seamlessly delegates to the unified Broadcast & Monitoring Hub
  return <SenderModal />;
};
