import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Bell,
  CheckCircle,
  ChevronRight,
  Clock,
  CreditCard,
  Database,
  Eye,
  MapPin,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Smartphone,
  User,
  XCircle,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  Cell,
  XAxis,
  YAxis,
} from "recharts";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

interface Transaction {
  transaction_id: string;
  user_id: string;
  timestamp: string;
  amount: number;
  merchant_category: string;
  location: string;
  payment_method: string;
  fraud_probability: number;
  risk_score: number;
  is_fraud: number;
  risk_level: string;
  created_at: string;
}

interface Reason {
  feature: string;
  impact: number;
  direction: "increases_fraud_risk" | "decreases_fraud_risk";
}

interface TransactionDetails extends Transaction {
  id: number;
  merchant_id: string;
  device_id: string;
  ip_address: string;
  account_age: number;
  transaction_count_24h: number;
  avg_transaction_amount: number;
  distance_from_home: number;
  is_new_device: number;
  is_new_location: number;
  reasons: Reason[] | null;
}

interface Statistics {
  total_transactions: number;
  fraud_transactions: number;
  high_risk_transactions: number;
  medium_risk_transactions: number;
  low_risk_transactions: number;
  average_transaction_amount: number;
  average_fraud_probability: number;
}

const emptyStats: Statistics = {
  total_transactions: 0,
  fraud_transactions: 0,
  high_risk_transactions: 0,
  medium_risk_transactions: 0,
  low_risk_transactions: 0,
  average_transaction_amount: 0,
  average_fraud_probability: 0,
};

function formatAmount(value: number | null | undefined) {
  return `₹${Number(value || 0).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  })}`;
}

function formatDate(value: string) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function riskBadge(risk: string) {
  const normalized = String(risk || "LOW").toLowerCase();

  return (
    <span className={`risk-badge ${normalized}`}>
      {normalized.toUpperCase()}
    </span>
  );
}

function App() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<Statistics>(emptyStats);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [selectedTransaction, setSelectedTransaction] =
    useState<TransactionDetails | null>(null);
  const [investigationLoading, setInvestigationLoading] = useState(false);

  const loadDashboard = async () => {
  setLoading(true);
  setApiError("");

  try {
    const statsResponse = await axios.get(
      `${API_URL}/stats`
    );

    const transactionsResponse = await axios.get(
      `${API_URL}/transactions?limit=50`
    );

    const alertsResponse = await axios.get(
      `${API_URL}/fraud-alerts?limit=10`
    );

    console.log("STATS:", statsResponse.data);
    console.log(
      "TRANSACTIONS:",
      transactionsResponse.data
    );
    console.log(
      "ALERTS:",
      alertsResponse.data
    );

    setStats(
      statsResponse.data.statistics
    );

    setTransactions(
      transactionsResponse.data.transactions || []
    );

    setAlerts(
      alertsResponse.data.alerts || []
    );

  } catch (error: any) {

    console.error(
      "Dashboard error:",
      error
    );

    setApiError(
      `Dashboard request failed: ${
        error?.response?.data?.detail ||
        error?.message ||
        "Unknown error"
      }`
    );

  } finally {

    setLoading(false);

  }
};

  const investigateTransaction = async (transactionId: string) => {
    try {
      setInvestigationLoading(true);
      setApiError("");

      const response = await axios.get(
        `${API_URL}/transactions/${encodeURIComponent(transactionId)}`
      );

      setSelectedTransaction(response.data.transaction);
    } catch (error) {
      console.error("Investigation error:", error);
      setApiError("Could not load this transaction.");
    } finally {
      setInvestigationLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();

    const interval = window.setInterval(loadDashboard, 15000);
    return () => window.clearInterval(interval);
  }, []);

  const filteredTransactions = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return transactions;

    return transactions.filter((transaction) =>
      [
        transaction.transaction_id,
        transaction.user_id,
        transaction.merchant_category,
        transaction.location,
        transaction.payment_method,
      ]
        .join(" ")
        .toLowerCase()
        .includes(query)
    );
  }, [transactions, search]);

  const activityData = useMemo(() => {
    const buckets = new Map<string, { total: number; fraud: number }>();

    transactions.forEach((transaction) => {
      const date = new Date(transaction.created_at || transaction.timestamp);
      const key = Number.isNaN(date.getTime())
        ? "Unknown"
        : date.toLocaleTimeString("en-IN", {
            hour: "2-digit",
            minute: "2-digit",
          });

      const current = buckets.get(key) || { total: 0, fraud: 0 };
      current.total += 1;
      if (transaction.is_fraud === 1) current.fraud += 1;
      buckets.set(key, current);
    });

    return Array.from(buckets.entries())
      .slice(-12)
      .map(([time, values]) => ({
        time,
        transactions: values.total,
        fraud: values.fraud,
      }));
  }, [transactions]);

  const riskData = [
    { name: "High", value: Number(stats.high_risk_transactions || 0) },
    { name: "Medium", value: Number(stats.medium_risk_transactions || 0) },
    { name: "Low", value: Number(stats.low_risk_transactions || 0) },
  ];

  const renderDashboard = () => (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldAlert size={22} />
          </div>
          <div>
            <h1>FinGuard AI</h1>
            <span>SECURITY PLATFORM</span>
          </div>
        </div>

        <div className="nav-section">MONITORING</div>

        <button className="nav-item active">
          <Activity size={17} />
          <span>Dashboard</span>
        </button>

        <div className="sidebar-status">
          <span className="status-dot" />
          <div>
            <strong>System Operational</strong>
            <span>API + ML + Database</span>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h2>Dashboard</h2>
            <p>Real-time financial transaction monitoring</p>
          </div>

          <div className="header-actions">
            <button
              className="refresh-button"
              onClick={loadDashboard}
              disabled={loading}
            >
              <RefreshCw size={16} className={loading ? "spin" : ""} />
              Refresh
            </button>

            <div className="notification">
              <Bell size={17} />
              {alerts.length > 0 && (
                <span className="notification-badge">{alerts.length}</span>
              )}
            </div>
          </div>
        </header>

        {apiError && <div className="api-error">{apiError}</div>}

        <section className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-top">
              <span>Total Transactions</span>
              <div className="kpi-icon">
                <Database size={16} />
              </div>
            </div>
            <strong className="kpi-value">
              {stats.total_transactions.toLocaleString("en-IN")}
            </strong>
            <span className="kpi-trend">Stored in PostgreSQL</span>
          </div>

          <div className="kpi-card danger">
            <div className="kpi-top">
              <span>Fraud Detected</span>
              <div className="kpi-icon">
                <ShieldAlert size={16} />
              </div>
            </div>
            <strong className="kpi-value">
              {stats.fraud_transactions.toLocaleString("en-IN")}
            </strong>
            <span className="kpi-trend">Model decisions</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <span>High Risk</span>
              <div className="kpi-icon">
                <AlertTriangle size={16} />
              </div>
            </div>
            <strong className="kpi-value">
              {stats.high_risk_transactions.toLocaleString("en-IN")}
            </strong>
            <span className="kpi-trend">Requires investigation</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <span>Low Risk</span>
              <div className="kpi-icon">
                <ShieldCheck size={16} />
              </div>
            </div>
            <strong className="kpi-value">
              {stats.low_risk_transactions.toLocaleString("en-IN")}
            </strong>
            <span className="kpi-trend">
              Avg score {(stats.average_fraud_probability * 100).toFixed(1)}%
            </span>
          </div>
        </section>

        <section className="charts-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Transaction Activity</h3>
                <span>Recent stored transactions</span>
              </div>
              <div className="live-label">
                <span />
                LIVE
              </div>
            </div>

            <div className="chart-container">
              {activityData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={activityData}>
                    <defs>
                      <linearGradient id="txGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#18212d" vertical={false} />
                    <XAxis dataKey="time" stroke="#475569" fontSize={9} />
                    <YAxis stroke="#475569" fontSize={9} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{
                        background: "#0d121b",
                        border: "1px solid #1e293b",
                        borderRadius: 8,
                        color: "#e2e8f0",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="transactions"
                      stroke="#60a5fa"
                      fill="url(#txGradient)"
                      strokeWidth={2}
                    />
                    <Area
                      type="monotone"
                      dataKey="fraud"
                      stroke="#ef4444"
                      fill="transparent"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">
                  <Activity size={22} />
                  <span>No transaction data yet</span>
                </div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Risk Distribution</h3>
                <span>Current stored decisions</span>
              </div>
            </div>

            <div className="risk-chart">
              {riskData.some((item) => item.value > 0) ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={55}
                      outerRadius={80}
                      paddingAngle={3}
                    >
                      <Cell fill="#ef4444" />
                      <Cell fill="#f59e0b" />
                      <Cell fill="#22c55e" />
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "#0d121b",
                        border: "1px solid #1e293b",
                        borderRadius: 8,
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">
                  <ShieldCheck size={22} />
                  <span>No risk data yet</span>
                </div>
              )}
            </div>

            <div className="risk-legend">
              <div className="legend-item">
                <div><span className="legend-dot high" />High</div>
                <strong>{stats.high_risk_transactions}</strong>
              </div>
              <div className="legend-item">
                <div><span className="legend-dot medium" />Medium</div>
                <strong>{stats.medium_risk_transactions}</strong>
              </div>
              <div className="legend-item">
                <div><span className="legend-dot low" />Low</div>
                <strong>{stats.low_risk_transactions}</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Fraud Alerts</h3>
                <span>Recent suspicious transactions</span>
              </div>
              <AlertTriangle size={16} />
            </div>

            <div className="alerts-list">
              {alerts.length === 0 ? (
                <div className="empty-state">
                  <ShieldCheck size={22} />
                  <span>No fraud alerts</span>
                </div>
              ) : (
                alerts.map((alert) => (
                  <div className="alert-item" key={alert.transaction_id}>
                    <div className="alert-icon">
                      <AlertTriangle size={15} />
                    </div>

                    <div className="alert-info">
                      <strong>{alert.transaction_id}</strong>
                      <span>
                        {formatAmount(alert.amount)} • {alert.merchant_category}
                      </span>
                    </div>

                    <div className="alert-score">
                      <strong>
                        {(alert.fraud_probability * 100).toFixed(1)}%
                      </strong>
                      <span>fraud probability</span>
                    </div>

                    <button
                      className="row-action"
                      onClick={() =>
                        investigateTransaction(alert.transaction_id)
                      }
                    >
                      <ChevronRight size={14} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="panel transactions-panel">
            <div className="panel-header">
              <div>
                <h3>Recent Transactions</h3>
                <span>Click Investigate for full AI analysis</span>
              </div>

              <div className="search-box">
                <Eye size={13} />
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search..."
                />
              </div>
            </div>

            <div className="table-wrapper">
              {filteredTransactions.length === 0 ? (
                <div className="empty-state table-empty">
                  <Database size={25} />
                  <span>
                    {apiError
                      ? "Unable to load transactions"
                      : "0 records"}
                  </span>
                  <small>
                    {apiError
                      ? "Check FastAPI and PostgreSQL."
                      : "Send a /predict request to create a transaction."}
                  </small>
                </div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Transaction</th>
                      <th>User</th>
                      <th>Amount</th>
                      <th>Category</th>
                      <th>Risk</th>
                      <th>Probability</th>
                      <th />
                    </tr>
                  </thead>

                  <tbody>
                    {filteredTransactions.map((transaction) => (
                      <tr key={transaction.transaction_id}>
                        <td>
                          <strong>{transaction.transaction_id}</strong>
                          <small>{formatDate(transaction.timestamp)}</small>
                        </td>

                        <td>{transaction.user_id}</td>

                        <td>{formatAmount(transaction.amount)}</td>

                        <td>{transaction.merchant_category}</td>

                        <td>{riskBadge(transaction.risk_level)}</td>

                        <td>
                          <div className="probability">
                            <span>
                              {(transaction.fraud_probability * 100).toFixed(1)}%
                            </span>
                            <div className="progress">
                              <div
                                style={{
                                  width: `${Math.min(
                                    transaction.fraud_probability * 100,
                                    100
                                  )}%`,
                                }}
                              />
                            </div>
                          </div>
                        </td>

                        <td>
                          <button
                            className="investigate-button"
                            onClick={() =>
                              investigateTransaction(transaction.transaction_id)
                            }
                          >
                            Investigate
                            <ChevronRight size={13} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );

  const renderInvestigation = () => {
    if (!selectedTransaction) return null;

    const probability = selectedTransaction.fraud_probability * 100;
    const reasons = selectedTransaction.reasons || [];

    return (
      <div className="app">
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-icon">
              <ShieldAlert size={22} />
            </div>
            <div>
              <h1>FinGuard AI</h1>
              <span>SECURITY PLATFORM</span>
            </div>
          </div>

          <div className="nav-section">INVESTIGATION</div>

          <button
            className="nav-item active"
            onClick={() => setSelectedTransaction(null)}
          >
            <Activity size={17} />
            <span>Transaction Analysis</span>
          </button>

          <div className="sidebar-status">
            <span className="status-dot" />
            <div>
              <strong>System Operational</strong>
              <span>XGBoost + SHAP</span>
            </div>
          </div>
        </aside>

        <main className="main">
          <header className="investigation-topbar">
            <button
              className="back-button"
              onClick={() => setSelectedTransaction(null)}
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </button>

            <div>
              <h2>Transaction Investigation</h2>
              <p>AI-powered fraud analysis and explainability</p>
            </div>
          </header>

          {apiError && <div className="api-error">{apiError}</div>}

          <section className="investigation-summary">
            <div className="investigation-card">
              <span className="card-label">TRANSACTION ID</span>
              <strong className="transaction-id-large">
                {selectedTransaction.transaction_id}
              </strong>
              <span className="transaction-time">
                <Clock size={14} />
                {formatDate(selectedTransaction.timestamp)}
              </span>
            </div>

            <div className="investigation-card">
              <span className="card-label">RISK LEVEL</span>
              <div className="large-risk">
                {riskBadge(selectedTransaction.risk_level)}
              </div>
              <p className="risk-description">
                {selectedTransaction.is_fraud === 1
                  ? "The model classified this transaction as potentially fraudulent."
                  : "The model classified this transaction as legitimate."}
              </p>
            </div>

            <div className="investigation-card">
              <span className="card-label">FRAUD PROBABILITY</span>
              <strong className="probability-number">
                {probability.toFixed(2)}%
              </strong>
              <div className="probability-bar">
                <div
                  className="probability-fill"
                  style={{ width: `${Math.min(probability, 100)}%` }}
                />
              </div>
            </div>
          </section>

          <section className="investigation-grid">
            <div className="investigation-panel">
              <div className="panel-header">
                <div>
                  <h3>AI Decision Explanation</h3>
                  <span>Top SHAP feature contributions</span>
                </div>
                <Activity size={17} />
              </div>

              <div className="explanation-content">
                {reasons.length === 0 ? (
                  <div className="empty-state">
                    <Activity size={25} />
                    <span>No SHAP explanation stored</span>
                    <small>
                      Run a new prediction after the database update.
                    </small>
                  </div>
                ) : (
                  reasons.map((reason, index) => {
                    const positive =
                      reason.direction === "increases_fraud_risk";

                    return (
                      <div
                        className={`reason-card ${
                          positive ? "positive" : "negative"
                        }`}
                        key={`${reason.feature}-${index}`}
                      >
                        <div className="reason-icon">
                          {positive ? (
                            <AlertTriangle size={17} />
                          ) : (
                            <CheckCircle size={17} />
                          )}
                        </div>

                        <div className="reason-main">
                          <strong>{reason.feature}</strong>
                          <span>
                            {positive
                              ? "Increases fraud risk"
                              : "Decreases fraud risk"}
                          </span>
                        </div>

                        <strong className="reason-impact">
                          {reason.impact > 0 ? "+" : ""}
                          {reason.impact.toFixed(3)}
                        </strong>
                      </div>
                    );
                  })
                )}
              </div>

              <div className="shap-note">
                SHAP impact is shown in the model's contribution scale; it is
                not a percentage-point change in probability.
              </div>
            </div>

            <div className="investigation-panel">
              <div className="panel-header">
                <div>
                  <h3>Transaction Information</h3>
                  <span>Transaction context</span>
                </div>
                <CreditCard size={17} />
              </div>

              <div className="details-grid">
                <Detail icon={<User size={15} />} label="User ID" value={selectedTransaction.user_id} />
                <Detail icon={<CreditCard size={15} />} label="Amount" value={formatAmount(selectedTransaction.amount)} />
                <Detail icon={<Database size={15} />} label="Merchant ID" value={selectedTransaction.merchant_id} />
                <Detail icon={<Database size={15} />} label="Category" value={selectedTransaction.merchant_category} />
                <Detail icon={<MapPin size={15} />} label="Location" value={selectedTransaction.location} />
                <Detail icon={<Smartphone size={15} />} label="Device ID" value={selectedTransaction.device_id} />
                <Detail icon={<CreditCard size={15} />} label="Payment" value={selectedTransaction.payment_method} />
                <Detail icon={<Database size={15} />} label="IP Address" value={selectedTransaction.ip_address} />
              </div>
            </div>
          </section>

          <section className="investigation-panel">
            <div className="panel-header">
              <div>
                <h3>Behavioral Signals</h3>
                <span>Features used by the fraud detection pipeline</span>
              </div>
              <ShieldAlert size={17} />
            </div>

            <div className="signal-grid">
              <Signal
                label="Transactions / 24h"
                value={selectedTransaction.transaction_count_24h}
              />
              <Signal
                label="Average Amount"
                value={formatAmount(selectedTransaction.avg_transaction_amount)}
              />
              <Signal
                label="Distance From Home"
                value={`${selectedTransaction.distance_from_home} km`}
              />
              <Signal
                label="Account Age"
                value={`${selectedTransaction.account_age} days`}
              />
              <Signal
                label="New Device"
                value={selectedTransaction.is_new_device ? "YES" : "NO"}
                danger={!!selectedTransaction.is_new_device}
              />
              <Signal
                label="New Location"
                value={selectedTransaction.is_new_location ? "YES" : "NO"}
                danger={!!selectedTransaction.is_new_location}
              />
            </div>
          </section>

          <section
            className={`decision-banner ${
              selectedTransaction.is_fraud ? "fraud" : "legitimate"
            }`}
          >
            {selectedTransaction.is_fraud ? (
              <XCircle size={27} />
            ) : (
              <CheckCircle size={27} />
            )}

            <div>
              <strong>
                {selectedTransaction.is_fraud
                  ? "Potential Fraud Detected"
                  : "Transaction Classified as Legitimate"}
              </strong>
              <span>
                XGBoost fraud probability: {probability.toFixed(2)}%
              </span>
            </div>
          </section>
        </main>
      </div>
    );
  };

  return investigationLoading ? (
    <div className="full-screen-loading">
      <RefreshCw className="spin" size={24} />
      Loading investigation...
    </div>
  ) : selectedTransaction ? (
    renderInvestigation()
  ) : (
    renderDashboard()
  );
}

function Detail({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="detail-item">
      {icon}
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function Signal({
  label,
  value,
  danger = false,
}: {
  label: string;
  value: React.ReactNode;
  danger?: boolean;
}) {
  return (
    <div className={`signal-card ${danger ? "signal-danger" : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default App;
