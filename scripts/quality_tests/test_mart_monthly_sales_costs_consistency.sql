DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM mart.monthly_sales_costs
        WHERE month IS NULL
           OR month_start IS NULL
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.monthly_sales_costs sisaldab NULL month või month_start väärtusi';
    ELSIF EXISTS (
        SELECT month_start
        FROM mart.monthly_sales_costs
        GROUP BY month_start
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.monthly_sales_costs sisaldab duplikaatseid month_start väärtusi';
    ELSIF EXISTS (
        SELECT 1
        FROM mart.monthly_sales_costs
        WHERE abs(net_eur - (sales_eur - costs_eur)) > 0.01
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.monthly_sales_costs net_eur ei klapi sales_eur - costs_eur arvutusega';
    ELSE
        RAISE NOTICE 'PASS: mart.monthly_sales_costs arvutusloogika korras';
    END IF;
END $$;
