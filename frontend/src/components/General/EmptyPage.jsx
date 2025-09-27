import React from 'react';

export default function EmptyPage(){
  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center max-w-md">
        <h1 className="text-2xl font-light text-gray-900 mb-4">
          Welcome
        </h1>
        <p className="text-gray-500 text-sm">
          Select a section from the navigation to begin
        </p>
      </div>
    </div>
  );
};