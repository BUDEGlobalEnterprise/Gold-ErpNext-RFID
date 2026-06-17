// AUTO-GENERATED from zevar_core/api/realtime/events_schema.py
// by scripts/gen_realtime_types.py. Do not edit by hand —
// edit events_schema.py and re-run the generator.


export const SCHEMA_VERSION = '1.0.0';

export interface EventEnvelope {
	v: string;
	id: string;
	channel: string;
	event_type: string;
	ts: string;
	store?: string | null;
	actor_user: string;
	actor_name: string;
}

export interface SaleCompletedData {
	invoice: string;
	customer?: string | null;
	net_total: number;
	grand_total: number;
	qty: number;
	channel: string;
	gross_margin_pct?: number | null;
}

export interface SaleCancelledData {
	invoice: string;
	reason?: string | null;
}

export interface RepairStatus_changedData {
	repair: string;
	status: string;
	customer?: string | null;
	warehouse?: string | null;
	assigned_to?: string | null;
}

export interface AnomalyDetectedData {
	severity: string;
	type: string;
	title: string;
	message: string;
	count?: number | null;
}

export interface HealthHeartbeatData {
	active_repairs?: number | null;
	pos_invoices_submitted?: number | null;
}

export const EVENT_TYPES = {
	'sale.completed': { channel: 'sales_tick', dataType: 'SaleCompletedData' },
	'sale.cancelled': { channel: 'sales_tick', dataType: 'SaleCancelledData' },
	'repair.status_changed': { channel: 'repair_live_event', dataType: 'RepairStatus_changedData' },
	'anomaly.detected': { channel: 'repair_anomaly_alert', dataType: 'AnomalyDetectedData' },
	'health.heartbeat': { channel: 'system_health', dataType: 'HealthHeartbeatData' },
} as const;

export const CHANNELS = {
	'repair_live_event': { scope: 'admin' },
	'repair_anomaly_alert': { scope: 'admin' },
	'system_health': { scope: 'admin' },
	'sales_tick': { scope: 'store' },
	'associate_personal': { scope: 'user' },
} as const;

