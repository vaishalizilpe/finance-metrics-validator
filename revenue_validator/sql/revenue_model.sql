SELECT
  service_month,
  SUM(invoice_amount - refund_amount) AS recognized_revenue
FROM ledger
WHERE status = 'paid'
GROUP BY 1
ORDER BY 1;