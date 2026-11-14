import React, { useState } from 'react';
import { Sidebar, ActiveTab } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './views/OverviewView';
import { FireMapView } from './views/FireMapView';
import { CalendarView } from './views/CalendarView';
import { SensorComparisonView } from './views/SensorComparisonView';
import { RegionalAnalyticsView } from './views/RegionalAnalyticsView';
import { MethodologyView } from './views/MethodologyView';
import { AboutView } from './views/AboutView';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [region, setRegion] = useState<'india' | 'maharashtra'>('maharashtra');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Fixed Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        region={region}
        setRegion={setRegion}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Header region={region} />

        <main className="flex-1 p-6 overflow-y-auto">
          {activeTab === 'overview' && (
            <OverviewView region={region} onNavigateToTab={setActiveTab} />
          )}
          {activeTab === 'map' && <FireMapView region={region} />}
          {activeTab === 'calendar' && <CalendarView region={region} />}
          {activeTab === 'comparison' && <SensorComparisonView region={region} />}
          {activeTab === 'analytics' && <RegionalAnalyticsView region={region} />}
          {activeTab === 'methodology' && <MethodologyView />}
          {activeTab === 'about' && <AboutView />}
        </main>
      </div>
    </div>
  );
};

export default App;
