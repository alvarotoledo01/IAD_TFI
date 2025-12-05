import React from 'react';

export const DashboardHeader = ({ lastUpdated }: { lastUpdated: Date }) => {
  return (
    <header className="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
      <h1 className="text-xl font-bold">SAR System - AI Agent Controlled</h1>
      <div className="text-sm">
        Actualizado: {lastUpdated.toLocaleTimeString()}
      </div>
    </header>
  );
};

