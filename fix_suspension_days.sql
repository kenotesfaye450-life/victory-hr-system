-- Fix NULL suspension_days and set default value
-- Run this SQL migration once to fix existing data

-- Update all NULL suspension_days to 0
UPDATE employees SET suspension_days = 0 WHERE suspension_days IS NULL;

-- Set default value for suspension_days column
ALTER TABLE employees ALTER COLUMN suspension_days SET DEFAULT 0;

-- Verify the changes
SELECT COUNT(*) as fixed_rows FROM employees WHERE suspension_days = 0;
