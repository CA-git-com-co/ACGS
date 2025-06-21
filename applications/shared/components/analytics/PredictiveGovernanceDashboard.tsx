import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Alert,
  AlertDescription,
  Badge,
  Progress,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Target } from 'lucide-react';

// Types
interface PredictiveMetrics {
  constitutionalStability: number;
  complianceForecast: number;
  policyImpactScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  confidenceScore: number;
  timestamp: string;
}

interface GovernanceOutcome {
  id: string;
  policyId: string;
  predictedOutcome: 'success' | 'failure' | 'partial';
  actualOutcome?: 'success' | 'failure' | 'partial';
  confidence: number;
  impactAreas: string[];
  riskFactors: string[];
}

interface RiskAssessment {
  category: string;
  probability: number;
  impact: number;
  riskScore: number;
  mitigationStrategies: string[];
}

const PredictiveGovernanceDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PredictiveMetrics | null>(null);
  const [outcomes, setOutcomes] = useState<GovernanceOutcome[]>([]);
  const [riskAssessments, setRiskAssessments] = useState<RiskAssessment[]>([]);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchPredictiveAnalytics();
    const interval = setInterval(fetchPredictiveAnalytics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPredictiveAnalytics = async () => {
    try {
      setLoading(true);

      // Simulate API calls - replace with actual service calls
      const mockMetrics: PredictiveMetrics = {
        constitutionalStability: 0.92,
        complianceForecast: 0.88,
        policyImpactScore: 0.85,
        riskLevel: 'low',
        confidenceScore: 0.94,
        timestamp: new Date().toISOString()
      };

      const mockOutcomes: GovernanceOutcome[] = [
        {
          id: 'PRED-001',
          policyId: 'POL-2024-001',
          predictedOutcome: 'success',
          confidence: 0.89,
          impactAreas: ['Constitutional Compliance', 'Democratic Participation'],
          riskFactors: ['Stakeholder Resistance']
        },
        {
          id: 'PRED-002',
          policyId: 'POL-2024-002',
          predictedOutcome: 'partial',
          confidence: 0.76,
          impactAreas: ['Policy Enforcement', 'Resource Allocation'],
          riskFactors: ['Implementation Complexity', 'Resource Constraints']
        }
      ];

      const mockRiskAssessments: RiskAssessment[] = [
        {
          category: 'Constitutional Drift',
          probability: 0.15,
          impact: 0.85,
          riskScore: 0.13,
          mitigationStrategies: ['Regular constitutional audits', 'Stakeholder engagement']
        },
        {
          category: 'Policy Conflicts',
          probability: 0.25,
          impact: 0.6,
          riskScore: 0.15,
          mitigationStrategies: ['Conflict detection algorithms', 'Mediation protocols']
        }
      ];

      const mockHistoricalData = Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        stability: 0.85 + Math.random() * 0.15,
        compliance: 0.8 + Math.random() * 0.2,
        riskScore: 0.1 + Math.random() * 0.2
      }));

      setMetrics(mockMetrics);
      setOutcomes(mockOutcomes);
      setRiskAssessments(mockRiskAssessments);
      setHistoricalData(mockHistoricalData);
    } catch (error) {
      console.error('Failed to fetch predictive analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'high':
        return 'text-orange-600';
      case 'critical':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getOutcomeIcon = (outcome: string) => {
    switch (outcome) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failure':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'partial':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <Target className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Predictive Governance Analytics</h2>
        <Badge variant="outline" className="text-sm">
          Last Updated: {metrics ? new Date(metrics.timestamp).toLocaleTimeString() : 'N/A'}
        </Badge>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Constitutional Stability</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((metrics?.constitutionalStability || 0) * 100).toFixed(1)}%
            </div>
            <Progress value={(metrics?.constitutionalStability || 0) * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Forecast</CardTitle>
            <Target className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((metrics?.complianceForecast || 0) * 100).toFixed(1)}%
            </div>
            <Progress value={(metrics?.complianceForecast || 0) * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Policy Impact Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((metrics?.policyImpactScore || 0) * 100).toFixed(1)}%
            </div>
            <Progress value={(metrics?.policyImpactScore || 0) * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${getRiskColor(metrics?.riskLevel || 'low')}`} />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold capitalize ${getRiskColor(metrics?.riskLevel || 'low')}`}
            >
              {metrics?.riskLevel || 'Unknown'}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Confidence: {((metrics?.confidenceScore || 0) * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="outcomes">Outcome Predictions</TabsTrigger>
          <TabsTrigger value="risks">Risk Assessment</TabsTrigger>
          <TabsTrigger value="trends">Historical Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Governance Stability Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historicalData.slice(-7)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="stability" stroke="#8884d8" strokeWidth={2} />
                    <Line type="monotone" dataKey="compliance" stroke="#82ca9d" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskAssessments}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, riskScore }) =>
                        `${category}: ${(riskScore * 100).toFixed(1)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="riskScore"
                    >
                      {riskAssessments.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={index % 2 === 0 ? '#8884d8' : '#82ca9d'}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="outcomes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Policy Outcome Predictions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {outcomes.map(outcome => (
                  <div key={outcome.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getOutcomeIcon(outcome.predictedOutcome)}
                        <span className="font-medium">{outcome.policyId}</span>
                        <Badge variant="outline">{outcome.predictedOutcome}</Badge>
                      </div>
                      <span className="text-sm text-gray-600">
                        Confidence: {(outcome.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <strong>Impact Areas:</strong>
                        <ul className="list-disc list-inside mt-1">
                          {outcome.impactAreas.map((area, index) => (
                            <li key={index}>{area}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <strong>Risk Factors:</strong>
                        <ul className="list-disc list-inside mt-1">
                          {outcome.riskFactors.map((factor, index) => (
                            <li key={index}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {riskAssessments.map((risk, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{risk.category}</h4>
                      <Badge
                        variant={
                          risk.riskScore > 0.2
                            ? 'destructive'
                            : risk.riskScore > 0.1
                              ? 'default'
                              : 'secondary'
                        }
                      >
                        Risk Score: {(risk.riskScore * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-3">
                      <div>
                        <span className="text-sm text-gray-600">Probability:</span>
                        <Progress value={risk.probability * 100} className="mt-1" />
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Impact:</span>
                        <Progress value={risk.impact * 100} className="mt-1" />
                      </div>
                    </div>
                    <div>
                      <strong className="text-sm">Mitigation Strategies:</strong>
                      <ul className="list-disc list-inside mt-1 text-sm">
                        {risk.mitigationStrategies.map((strategy, strategyIndex) => (
                          <li key={strategyIndex}>{strategy}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>30-Day Historical Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="stability"
                    stackId="1"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="compliance"
                    stackId="2"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="riskScore"
                    stackId="3"
                    stroke="#ffc658"
                    fill="#ffc658"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Alerts */}
      {metrics && metrics.riskLevel !== 'low' && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Elevated risk level detected: {metrics.riskLevel}. Consider reviewing current policies
            and implementing additional safeguards.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default PredictiveGovernanceDashboard;
