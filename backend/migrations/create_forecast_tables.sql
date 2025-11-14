-- Migración: Crear tabla company y añadir campo hourly_rate a employee
-- Fecha: 2025-01-25
-- Descripción: Sistema de Forecast con períodos de facturación personalizados

-- Crear tabla company
CREATE TABLE IF NOT EXISTS company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    billing_period_start_day INTEGER NOT NULL CHECK (billing_period_start_day >= 1 AND billing_period_start_day <= 31),
    billing_period_end_day INTEGER NOT NULL CHECK (billing_period_end_day >= 1 AND billing_period_end_day <= 31),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Añadir campo hourly_rate a employee (tarifa por hora, solo visible para admin)
ALTER TABLE employee 
ADD COLUMN IF NOT EXISTS hourly_rate FLOAT;

-- Crear índice para búsquedas rápidas de empresas activas
CREATE INDEX IF NOT EXISTS idx_company_active ON company(active);

-- Comentarios para documentación
COMMENT ON TABLE company IS 'Empresas/clientes con períodos de facturación personalizados para cálculo de forecast';
COMMENT ON COLUMN company.billing_period_start_day IS 'Día de inicio del período de facturación (1-31). Si es mayor que end_day, cruza meses.';
COMMENT ON COLUMN company.billing_period_end_day IS 'Día de fin del período de facturación (1-31)';
COMMENT ON COLUMN employee.hourly_rate IS 'Tarifa por hora del empleado en euros. Solo visible para administradores.';

