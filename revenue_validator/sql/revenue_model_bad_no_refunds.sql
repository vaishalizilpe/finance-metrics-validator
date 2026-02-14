SELECT
  service_month,
  SUM(invoice_amount) AS recognized_revenue
FROM ledger
WHERE status = 'paid'
GROUP BY 1;