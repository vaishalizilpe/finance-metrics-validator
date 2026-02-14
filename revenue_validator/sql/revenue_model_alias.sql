SELECT
  service_month,
  SUM(invoice_amount - refund_amount) AS rev
FROM ledger
WHERE status = 'paid'
GROUP BY 1;