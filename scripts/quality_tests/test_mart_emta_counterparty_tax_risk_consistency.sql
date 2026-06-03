DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM mart.emta_counterparty_tax_risk
        WHERE tax_debt_eur < 0
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.emta_counterparty_tax_risk sisaldab negatiivset tax_debt_eur väärtust';
    ELSIF EXISTS (
        SELECT 1
        FROM mart.emta_counterparty_tax_risk
        WHERE risk_status NOT IN ('risk', 'ok')
           OR risk_status IS NULL
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.emta_counterparty_tax_risk sisaldab vigast risk_status väärtust';
    ELSIF EXISTS (
        SELECT 1
        FROM mart.emta_counterparty_tax_risk
        WHERE (tax_debt_eur > 0 AND risk_status <> 'risk')
           OR (tax_debt_eur = 0 AND risk_status <> 'ok')
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.emta_counterparty_tax_risk risk_status ei klapi tax_debt_eur väärtusega';
    ELSE
        RAISE NOTICE 'PASS: mart.emta_counterparty_tax_risk loogika korras';
    END IF;
END $$;
