-- Migración: Agregar índices para optimización de rendimiento
-- Fecha: 2026-01-29
-- Descripción: Índices críticos para mejorar el rendimiento de consultas frecuentes

-- 1. Índice compuesto para consultas de calendario por rango de fechas y tipo de actividad
-- Optimiza: CalendarActivity.query.filter(date >= X, date <= Y, employee_id.in_(...), activity_type=...)
CREATE INDEX IF NOT EXISTS idx_calendar_activity_date_range 
ON calendar_activity(date, employee_id, activity_type);

-- 2. Índice compuesto para consultas de festivos por país y fecha
-- Optimiza: Holiday.query.filter(country=X, date >= Y, date <= Z, active=true)
CREATE INDEX IF NOT EXISTS idx_holiday_country_date 
ON holiday(country, date) 
WHERE active = true;

-- 3. Índice compuesto para consultas de empleados activos por equipo
-- Optimiza: Employee.query.filter(team_id=X, active=true)
CREATE INDEX IF NOT EXISTS idx_employee_team_active 
ON employee(team_id, active) 
WHERE active = true;

-- 4. Índice adicional para consultas de festivos por región (para festivos regionales)
CREATE INDEX IF NOT EXISTS idx_holiday_region_date 
ON holiday(region, date) 
WHERE active = true AND region IS NOT NULL;

-- 5. Índice adicional para consultas de festivos por ciudad (para festivos locales)
CREATE INDEX IF NOT EXISTS idx_holiday_city_date 
ON holiday(city, date) 
WHERE active = true AND city IS NOT NULL;

-- Verificar que los índices se crearon correctamente
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('calendar_activity', 'holiday', 'employee')
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
